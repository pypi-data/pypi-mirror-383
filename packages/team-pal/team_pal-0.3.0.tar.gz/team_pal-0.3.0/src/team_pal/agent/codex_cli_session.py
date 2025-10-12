"""Codex CLI session management."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from team_pal.agent.codex_cli import CodexCliAgentAdapter
from team_pal.application.agent_session import AgentSession, AgentSessionError, AgentSessionFactory
from team_pal.domain.execution import ExecutionResult
from team_pal.domain.instruction import Instruction


@dataclass
class CodexProcessController:
    """Thin wrapper around :class:`CodexCliAgentAdapter` to execute prompts."""

    adapter: CodexCliAgentAdapter

    def __post_init__(self) -> None:
        self._thread_ids: dict[str, str] = {}

    def execute(self, session_id: str, instruction: Instruction) -> ExecutionResult:
        thread_id = self._thread_ids.get(session_id)
        result = self.adapter.dispatch(instruction, thread_id=thread_id)
        new_thread_id = _extract_thread_id(result)
        if new_thread_id:
            self._thread_ids[session_id] = new_thread_id
        return result

    def close(self) -> None:
        self._thread_ids.clear()
        close_fn = getattr(self.adapter, "close", None)
        if callable(close_fn):
            close_fn()


class CodexCliAgentSession(AgentSession):
    """Stateful wrapper representing a Codex CLI interactive session."""

    def __init__(self, controller: CodexProcessController, *, session_id: str | None = None) -> None:
        self._controller = controller
        self._session_id = session_id or str(uuid.uuid4())
        self._closed = False

    def get_id(self) -> str:
        return self._session_id

    def send(self, instruction: Instruction) -> ExecutionResult:
        if self._closed:
            raise AgentSessionError("Codex CLI session is already closed")
        return self._controller.execute(self._session_id, instruction)

    def close(self) -> None:
        if not self._closed:
            self._controller.close()
        self._closed = True


class CodexAgentSessionFactory(AgentSessionFactory):
    """Factory that produces Codex CLI agent sessions."""

    def __init__(self, controller: CodexProcessController) -> None:
        self._controller = controller

    def create(self, *, channel: str, instruction: Instruction) -> AgentSession:
        # channel parameter is accepted for interface compatibility; codex sessions
        # do not vary based on channel in Phase 2.
        return CodexCliAgentSession(self._controller)


__all__ = [
    "CodexProcessController",
    "CodexCliAgentSession",
    "CodexAgentSessionFactory",
]


def _extract_thread_id(result: ExecutionResult) -> str | None:
    output = result.output
    if isinstance(output, dict):
        thread_id = output.get("thread_id")
        if isinstance(thread_id, str) and thread_id:
            return thread_id
    return None
