"""Session domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Sequence

from team_pal.domain.execution import ExecutionResult
from team_pal.domain.instruction import Instruction


class SessionStatus(Enum):
    """Represents the lifecycle state of an instruction session."""

    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPATCHED = "dispatched"
    ABORTED = "aborted"


@dataclass(frozen=True)
class SessionHistoryEntry:
    """History entry capturing an instruction and the corresponding result."""

    instruction: Instruction
    result: ExecutionResult
    timestamp: datetime


@dataclass
class InstructionSession:
    """Aggregates state for a logical instruction session."""

    session_id: str
    channel: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = SessionStatus.CREATED
    agent_session_id: str | None = None
    history: List[SessionHistoryEntry] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        return self.status in {SessionStatus.CREATED, SessionStatus.ACTIVE}

    def append(self, entry: SessionHistoryEntry) -> None:
        self.history.append(entry)
        self.updated_at = entry.timestamp

    def set_status(self, status: SessionStatus) -> None:
        self.status = status
        self.updated_at = datetime.now(timezone.utc)

    def as_history(self) -> Sequence[SessionHistoryEntry]:
        return list(self.history)


__all__ = ["InstructionSession", "SessionHistoryEntry", "SessionStatus"]
