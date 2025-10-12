"""Agent session abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from team_pal.domain.instruction import Instruction
from team_pal.domain.execution import ExecutionResult


class AgentSession(Protocol):
    """Represents an interactive session with an execution agent."""

    def get_id(self) -> str: ...

    def send(self, instruction: Instruction) -> ExecutionResult: ...

    def close(self) -> None: ...


class AgentSessionFactory(Protocol):
    """Factory interface responsible for creating agent sessions."""

    def create(self, *, channel: str, instruction: Instruction) -> AgentSession: ...


@dataclass(frozen=True)
class AgentSessionHandle:
    """Links an application session to an underlying agent session identifier."""

    session_id: str
    agent_session_id: str


class AgentSessionError(RuntimeError):
    """Raised when agent session creation or execution fails."""


__all__ = ["AgentSession", "AgentSessionFactory", "AgentSessionHandle", "AgentSessionError"]
