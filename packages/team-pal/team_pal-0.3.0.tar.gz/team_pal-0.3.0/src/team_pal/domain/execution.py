"""Execution domain models for Team Pal."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from team_pal.domain.instruction import Instruction


class ExecutionStatus(Enum):
    """Represents the outcome of an execution request."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class ExecutionError:
    """Details the cause of a failed execution."""

    message: str
    detail: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "detail": copy.deepcopy(self.detail) if self.detail is not None else None,
        }


@dataclass(frozen=True)
class ExecutionResult:
    """Execution outcome along with metadata and payload."""

    instruction: Instruction
    status: ExecutionStatus
    output: Mapping[str, Any] | str | None
    error: ExecutionError | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def duration(self):
        """Return the execution duration as a :class:`datetime.timedelta`."""

        return self.finished_at - self.started_at

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the execution result."""

        return {
            "instruction": self.instruction.to_dict(),
            "status": self.status.value,
            "output": copy.deepcopy(self.output),
            "error": self.error.to_dict() if self.error is not None else None,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ExecutionResult:
        """Create an :class:`ExecutionResult` from a mapping."""

        instruction = Instruction.from_dict(payload["instruction"])
        error_payload = payload.get("error")
        execution_error = (
            ExecutionError(
                message=error_payload["message"],
                detail=error_payload.get("detail"),
            )
            if error_payload
            else None
        )
        return cls(
            instruction=instruction,
            status=ExecutionStatus(payload["status"]),
            output=copy.deepcopy(payload.get("output")),
            error=execution_error,
            started_at=datetime.fromisoformat(payload["started_at"]),
            finished_at=datetime.fromisoformat(payload["finished_at"]),
        )


__all__ = ["ExecutionError", "ExecutionResult", "ExecutionStatus"]
