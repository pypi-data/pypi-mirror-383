"""Unified instruction data model."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Mapping

InstructionPayload = Any
InstructionMetadata = Mapping[str, Any]


@dataclass(frozen=True)
class Instruction:
    """Represents a normalized instruction Team Pal can process."""

    instruction_id: str
    channel: str
    source_metadata: Mapping[str, Any] = field(default_factory=dict)
    payload: InstructionPayload = field(default_factory=dict)
    requested_outputs: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the instruction."""

        return {
            "instruction_id": self.instruction_id,
            "channel": self.channel,
            "source_metadata": copy.deepcopy(dict(self.source_metadata)),
            "payload": copy.deepcopy(self.payload),
            "requested_outputs": copy.deepcopy(self.requested_outputs)
            if self.requested_outputs is not None
            else None,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Instruction":
        """Create an :class:`Instruction` from a mapping."""

        return cls(
            instruction_id=str(payload["instruction_id"]),
            channel=str(payload["channel"]),
            source_metadata=copy.deepcopy(dict(payload.get("source_metadata", {}))),
            payload=copy.deepcopy(payload.get("payload")),
            requested_outputs=copy.deepcopy(payload.get("requested_outputs"))
            if payload.get("requested_outputs") is not None
            else None,
        )


__all__ = ["Instruction", "InstructionPayload", "InstructionMetadata"]
