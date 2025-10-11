"""codex exec JSON streaming adapter."""

from __future__ import annotations

import io
import logging
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Mapping, Protocol

from team_pal.agent.codex_stream import CodexStreamEvent, iter_codex_jsonl_events
from team_pal.domain.execution import ExecutionError, ExecutionResult, ExecutionStatus
from team_pal.domain.instruction import Instruction
from team_pal.service.execution import AgentDispatcher

ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


@dataclass(frozen=True)
class CodexRunResult:
    """Represents the outcome of executing `codex exec --json`."""

    exit_code: int
    events: list[CodexStreamEvent]
    thread_id: str | None
    stderr: str
    duration: timedelta


class CodexRunnerProtocol(Protocol):
    """Protocol for invoking `codex exec --json`."""

    def run(
        self,
        prompt: str,
        *,
        metadata: Mapping[str, object],
        thread_id: str | None = None,
    ) -> CodexRunResult:
        ...


class CodexExecRunner(CodexRunnerProtocol):
    """Runs codex exec in JSON streaming mode and captures all events."""

    def __init__(
        self,
        binary_path: str,
        *,
        timeout_seconds: int = 300,
        extra_args: Iterable[str] | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._binary_path = binary_path
        self._timeout_seconds = timeout_seconds
        self._extra_args = list(extra_args or [])
        self._env = dict(env) if env is not None else None
        self._logger = logging.getLogger("team_pal.agent.codex.runner")

    def run(
        self,
        prompt: str,
        *,
        metadata: Mapping[str, object],
        thread_id: str | None = None,
    ) -> CodexRunResult:
        command: list[str] = [self._binary_path, "exec", "--json"]
        if self._extra_args:
            command.extend(self._extra_args)
        resume_target = _metadata_resume_target(metadata)
        resume_id = thread_id or resume_target
        if resume_id:
            command.extend(["resume", str(resume_id)])

        self._logger.debug("Executing codex command: %s", command)
        started = time.monotonic()
        try:
            completed = subprocess.run(  # noqa: PL subprocess usage acceptable
                command,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self._timeout_seconds,
                check=False,
                env=self._env,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("codex exec timed out") from exc
        except FileNotFoundError as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"codex binary not found at {self._binary_path}") from exc

        duration = timedelta(seconds=time.monotonic() - started)
        stdout = completed.stdout or ""
        stderr = _strip_control_sequences(completed.stderr or "")

        stream = io.StringIO(stdout)
        events = list(iter_codex_jsonl_events(stream))
        derived_thread_id = _extract_thread_id(events, fallback=resume_id)

        if completed.returncode != 0:
            self._logger.debug("codex exec exited with %s: stderr=%s", completed.returncode, stderr)

        return CodexRunResult(
            exit_code=completed.returncode,
            events=events,
            thread_id=derived_thread_id,
            stderr=stderr,
            duration=duration,
        )


class CodexCliAgentAdapter(AgentDispatcher):
    """Adapter that delegates to codex exec to execute instructions."""

    def __init__(self, runner: CodexRunnerProtocol) -> None:
        self._runner = runner
        self._logger = logging.getLogger("team_pal.agent.codex")

    def dispatch(self, instruction: Instruction, *, thread_id: str | None = None) -> ExecutionResult:
        prompt = self._extract_prompt(instruction)
        started_at = datetime.now(timezone.utc)
        try:
            run_result = self._runner.run(prompt, metadata=instruction.source_metadata, thread_id=thread_id)
            finished_at = datetime.now(timezone.utc)
        except TimeoutError as exc:
            finished_at = datetime.now(timezone.utc)
            return self._timeout_result(instruction, exc, started_at, finished_at)
        except Exception as exc:
            finished_at = datetime.now(timezone.utc)
            return self._failure_result(instruction, exc, started_at, finished_at)

        events_payload = [_event_to_payload(event) for event in run_result.events]
        final_message = _extract_final_agent_message(run_result.events)
        turn_failed = _has_turn_failed(run_result.events)
        status = ExecutionStatus.SUCCESS if run_result.exit_code == 0 and not turn_failed else ExecutionStatus.FAILURE

        error = None
        if status is ExecutionStatus.FAILURE:
            detail = {"stderr": run_result.stderr, "exit_code": run_result.exit_code}
            error_message = "codex exec reported failure"
            if turn_failed:
                error_message = "codex exec turn failed"
            error = ExecutionError(message=error_message, detail=detail)

        output = {
            "thread_id": run_result.thread_id,
            "events": events_payload,
            "final_message": final_message,
            "exit_code": run_result.exit_code,
            "stderr": run_result.stderr,
            "duration_seconds": run_result.duration.total_seconds(),
        }

        return ExecutionResult(
            instruction=instruction,
            status=status,
            output=output,
            error=error,
            started_at=started_at,
            finished_at=finished_at,
        )

    def _timeout_result(
        self,
        instruction: Instruction,
        exc: Exception,
        started_at: datetime,
        finished_at: datetime,
    ) -> ExecutionResult:
        return ExecutionResult(
            instruction=instruction,
            status=ExecutionStatus.TIMEOUT,
            output=None,
            error=ExecutionError(message=str(exc)),
            started_at=started_at,
            finished_at=finished_at,
        )

    def _failure_result(
        self,
        instruction: Instruction,
        exc: Exception,
        started_at: datetime,
        finished_at: datetime,
    ) -> ExecutionResult:
        return ExecutionResult(
            instruction=instruction,
            status=ExecutionStatus.FAILURE,
            output=None,
            error=ExecutionError(message=str(exc)),
            started_at=started_at,
            finished_at=finished_at,
        )

    def _extract_prompt(self, instruction: Instruction) -> str:
        payload = instruction.payload
        if isinstance(payload, str):
            return payload
        if isinstance(payload, Mapping):
            text = payload.get("text")
            if text:
                return str(text)
        return str(payload)

    def close(self) -> None:  # pragma: no cover - compatibility hook
        close_fn = getattr(self._runner, "close", None)
        if callable(close_fn):
            close_fn()


def _extract_thread_id(events: Iterable[CodexStreamEvent], fallback: str | None) -> str | None:
    for event in events:
        if event.type == "thread.started":
            thread_id = event.payload.get("thread_id")
            if isinstance(thread_id, str):
                return thread_id
    return fallback


def _has_turn_failed(events: Iterable[CodexStreamEvent]) -> bool:
    return any(event.type == "turn.failed" for event in events)


def _extract_final_agent_message(events: Iterable[CodexStreamEvent]) -> str | None:
    final_message: str | None = None
    for event in events:
        if event.type == "item.completed":
            item = event.payload.get("item")
            if isinstance(item, Mapping) and item.get("type") == "agent_message":
                text = item.get("text")
                if isinstance(text, str):
                    final_message = text
    return final_message


def _event_to_payload(event: CodexStreamEvent) -> Mapping[str, object]:
    return {"type": event.type, "payload": event.payload}


def _strip_control_sequences(text: str) -> str:
    cleaned = ANSI_RE.sub("", text or "")
    result: list[str] = []
    buffer: list[str] = []

    for ch in cleaned:
        if ch == "\r":
            buffer = []
            continue
        if ch == "\n":
            if buffer:
                result.append("".join(buffer))
                buffer = []
            continue
        if ch == "\b":
            if buffer:
                buffer.pop()
            continue
        buffer.append(ch)

    if buffer:
        result.append("".join(buffer))

    return "\n".join(result).strip()


def _metadata_resume_target(metadata: Mapping[str, object]) -> str | None:
    resume = metadata.get("codex_thread_id")
    if isinstance(resume, str) and resume:
        return resume
    return None


__all__ = [
    "CodexCliAgentAdapter",
    "CodexRunResult",
    "CodexRunnerProtocol",
    "CodexExecRunner",
]
