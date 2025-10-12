"""Session management utilities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List

from team_pal.domain.execution import ExecutionResult, ExecutionStatus
from team_pal.domain.instruction import Instruction
from team_pal.domain.session import InstructionSession, SessionHistoryEntry, SessionStatus
from team_pal.repository.session import InstructionSessionRepository


@dataclass
class SessionManagerConfig:
    """Configuration options for the session manager."""

    default_channel: str = "cli"


class InstructionSessionManager:
    """Manages instruction session lifecycle and history."""

    def __init__(
        self,
        repository: InstructionSessionRepository,
        *,
        config: SessionManagerConfig | None = None,
    ) -> None:
        self._repository = repository
        self._config = config or SessionManagerConfig()

    def create_session(self, instruction: Instruction, *, agent_session_id: str | None = None) -> InstructionSession:
        session_id = instruction.instruction_id or str(uuid.uuid4())
        session = InstructionSession(
            session_id=session_id,
            channel=instruction.channel or self._config.default_channel,
            status=SessionStatus.CREATED,
            agent_session_id=agent_session_id,
        )
        self._repository.save(session)
        return session

    def append_history(self, session_id: str, instruction: Instruction, result: ExecutionResult) -> SessionHistoryEntry:
        entry = SessionHistoryEntry(
            instruction=instruction,
            result=result,
            timestamp=datetime.now(timezone.utc),
        )
        self._repository.append_history(session_id, entry)
        return entry

    def update_status(self, session_id: str, status: SessionStatus) -> None:
        self._repository.update_status(session_id, status)

    def abort(self, session_id: str, *, reason: str | None = None) -> None:
        session = self._require(session_id)
        session.set_status(SessionStatus.ABORTED)
        self._repository.save(session)
        if reason:
            abort_instruction = Instruction(
                instruction_id=f"{session_id}-abort",
                channel=session.channel,
                payload={"abort_reason": reason},
                source_metadata={},
            )
            abort_result = ExecutionResult(
                instruction=abort_instruction,
                status=ExecutionStatus.FAILURE,
                output={"message": reason},
                error=None,
                started_at=datetime.now(timezone.utc),
                finished_at=datetime.now(timezone.utc),
            )
            entry = SessionHistoryEntry(
                instruction=abort_instruction,
                result=abort_result,
                timestamp=datetime.now(timezone.utc),
            )
            session.append(entry)
            self._repository.save(session)

    def assign_agent_session(self, session_id: str, agent_session_id: str) -> None:
        session = self._require(session_id)
        session.agent_session_id = agent_session_id
        session.set_status(SessionStatus.ACTIVE)
        self._repository.save(session)

    def complete(self, session_id: str, status: SessionStatus) -> None:
        if status not in {SessionStatus.COMPLETED, SessionStatus.FAILED, SessionStatus.DISPATCHED}:
            raise ValueError("Invalid completion status")
        session = self._require(session_id)
        session.set_status(status)
        self._repository.save(session)

    def get_session(self, session_id: str) -> InstructionSession | None:
        return self._repository.get(session_id)

    def list_sessions(self, *, channel: str | None = None) -> List[InstructionSession]:
        sessions = list(self._repository.list())
        if channel is None:
            return sessions
        return [session for session in sessions if session.channel == channel]

    def _require(self, session_id: str) -> InstructionSession:
        session = self._repository.get(session_id)
        if session is None:
            raise KeyError(session_id)
        return session


__all__ = ["InstructionSessionManager", "SessionManagerConfig"]
