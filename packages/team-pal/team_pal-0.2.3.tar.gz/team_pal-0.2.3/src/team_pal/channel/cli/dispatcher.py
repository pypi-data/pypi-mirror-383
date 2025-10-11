"""CLI result dispatcher."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Iterable, Mapping, TextIO

from team_pal.domain.execution import ExecutionResult, ExecutionStatus
from team_pal.domain.instruction import Instruction
from team_pal.service.facade import ResultDispatcher


class CLIResultPresenter:
    """Formats execution results for CLI output."""

    def __init__(self, *, debug: bool = False) -> None:
        self._debug = debug

    def format(self, session_id: str, result: ExecutionResult) -> str:
        if self._debug:
            return self._format_debug(session_id, result)
        return self._format_human(session_id, result)

    def _format_human(self, session_id: str, result: ExecutionResult) -> str:
        status_icon = {
            ExecutionStatus.SUCCESS: "✅",
            ExecutionStatus.FAILURE: "❌",
            ExecutionStatus.TIMEOUT: "⌛",
        }.get(result.status, "ℹ️")
        timestamp = datetime.now().isoformat(timespec="seconds")
        prompt = self._extract_prompt(result.instruction)

        lines = [f"[{timestamp}] {status_icon} Session {session_id} -> {result.status.value}"]
        if prompt:
            lines.append(f"Prompt: {prompt}")

        final_message = self._extract_final_message(result.output)
        summary = self._summarize_output(result.output)

        if final_message:
            lines.append(f"Response: {final_message}")
        elif summary:
            label = "Details" if result.status is not ExecutionStatus.SUCCESS else "Summary"
            lines.append(f"{label}: {summary}")

        if result.error:
            lines.append(f"Error: {result.error.message}")

        return "\n".join(lines) + "\n"

    def _format_debug(self, session_id: str, result: ExecutionResult) -> str:
        status_icon = {
            ExecutionStatus.SUCCESS: "✅",
            ExecutionStatus.FAILURE: "❌",
            ExecutionStatus.TIMEOUT: "⌛",
        }.get(result.status, "ℹ️")
        timestamp = datetime.now().isoformat(timespec="seconds")
        prompt = self._extract_prompt(result.instruction)

        lines = [f"[{timestamp}] {status_icon} Session {session_id} -> {result.status.value}"]
        if prompt:
            lines.append(f"Prompt: {prompt}")
        if result.error:
            lines.append(f"Error: {result.error.message}")
        lines.append("Output:")
        for chunk in self._format_output(result.output):
            lines.append(f"  {chunk}")
        return "\n".join(lines) + "\n"

    def _extract_prompt(self, instruction: Instruction) -> str:
        payload = instruction.payload
        if isinstance(payload, str):
            return payload.strip()
        if isinstance(payload, dict):
            value = payload.get("text")
            if value:
                return str(value).strip()
        return ""

    def _format_output(self, output: object) -> Iterable[str]:
        if output is None:
            yield "(no output)"
            return
        if isinstance(output, str):
            yield from self._split_lines(output)
            return
        if isinstance(output, dict):
            events = output.get("events")
            if isinstance(events, list):
                yield from self._format_events(output)
                return
            formatted = json.dumps(output, ensure_ascii=False, indent=2)
            yield from self._split_lines(formatted)
            return
        yield repr(output)

    def _format_events(self, output: dict) -> Iterable[str]:
        thread_id = output.get("thread_id")
        if isinstance(thread_id, str):
            yield f"thread_id: {thread_id}"
        for event in output.get("events", []):
            if not isinstance(event, dict):
                yield f"event: {event!r}"
                continue
            event_type = event.get("type", "unknown")
            payload = event.get("payload", {})
            if event_type == "item.completed":
                item = payload.get("item", {})
                if isinstance(item, dict) and item.get("type") == "agent_message":
                    text = item.get("text") or ""
                    yield f"agent_message: {text}"
                    continue
            yield f"event[{event_type}]: {json.dumps(payload, ensure_ascii=False)}"
        final_message = output.get("final_message")
        if isinstance(final_message, str) and final_message:
            yield f"final: {final_message}"
        stderr = output.get("stderr")
        if isinstance(stderr, str) and stderr:
            yield f"stderr: {stderr}"
        exit_code = output.get("exit_code")
        if exit_code is not None:
            yield f"exit_code: {exit_code}"

    def _split_lines(self, text: str) -> Iterable[str]:
        for line in text.splitlines() or [""]:
            yield line

    def _extract_final_message(self, output: object) -> str | None:
        if isinstance(output, str):
            value = output.strip()
            return value or None
        if isinstance(output, Mapping):
            final_message = output.get("final_message")
            if isinstance(final_message, str) and final_message.strip():
                return final_message.strip()
            events = output.get("events")
            if isinstance(events, list):
                for event in events:
                    if (
                        isinstance(event, Mapping)
                        and event.get("type") == "item.completed"
                        and isinstance(event.get("payload"), Mapping)
                    ):
                        item = event["payload"].get("item")
                        if isinstance(item, Mapping) and item.get("type") == "agent_message":
                            text = item.get("text")
                            if isinstance(text, str) and text.strip():
                                return text.strip()
        return None

    def _summarize_output(self, output: object) -> str | None:
        if isinstance(output, str):
            value = output.strip()
            return value or None
        if isinstance(output, Mapping):
            exit_code = output.get("exit_code")
            if exit_code is not None:
                return f"exit_code={exit_code}"
            stderr = output.get("stderr")
            if isinstance(stderr, str) and stderr.strip():
                return stderr.strip()
        return None


class CLIResultDispatcher(ResultDispatcher):
    """Writes execution results to the configured output sink."""

    def __init__(self, *, presenter: CLIResultPresenter, output: TextIO) -> None:
        self._presenter = presenter
        self._output = output

    def dispatch(self, instruction_id: str, payload: object) -> None:
        if not isinstance(payload, ExecutionResult):
            self._output.write(f"Unsupported payload for CLI dispatcher: {payload!r}\n")
            self._output.flush()
            return
        message = self._presenter.format(instruction_id, payload)
        self._output.write(message)
        self._output.flush()


__all__ = ["CLIResultPresenter", "CLIResultDispatcher"]
