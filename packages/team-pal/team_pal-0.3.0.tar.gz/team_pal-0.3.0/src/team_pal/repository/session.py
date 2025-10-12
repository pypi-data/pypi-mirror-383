"""Session repository abstractions."""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Iterable

from team_pal.domain.session import InstructionSession, SessionHistoryEntry, SessionStatus


class InstructionSessionRepository(ABC):
    """Abstract repository for persisting instruction sessions."""

    @abstractmethod
    def save(self, session: InstructionSession) -> None: ...

    @abstractmethod
    def get(self, session_id: str) -> InstructionSession | None: ...

    @abstractmethod
    def list(self) -> Iterable[InstructionSession]: ...

    @abstractmethod
    def append_history(self, session_id: str, entry: SessionHistoryEntry) -> None: ...

    @abstractmethod
    def update_status(self, session_id: str, status: SessionStatus) -> None: ...


class InMemoryInstructionSessionRepository(InstructionSessionRepository):
    """Thread-safe in-memory session repository."""

    def __init__(self) -> None:
        self._sessions: OrderedDict[str, InstructionSession] = OrderedDict()
        self._lock = threading.Lock()

    def save(self, session: InstructionSession) -> None:
        with self._lock:
            self._sessions[session.session_id] = session

    def get(self, session_id: str) -> InstructionSession | None:
        with self._lock:
            session = self._sessions.get(session_id)
            return None if session is None else session

    def list(self) -> Iterable[InstructionSession]:
        with self._lock:
            return list(self._sessions.values())

    def append_history(self, session_id: str, entry: SessionHistoryEntry) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise KeyError(session_id)
            session.append(entry)

    def update_status(self, session_id: str, status: SessionStatus) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise KeyError(session_id)
            session.set_status(status)


__all__ = [
    "InstructionSessionRepository",
    "InMemoryInstructionSessionRepository",
]
