"""Utilities for parsing codex exec JSONL event streams."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Mapping, TextIO


@dataclass(frozen=True)
class CodexStreamEvent:
    """Represents a single Codex streaming event."""

    type: str
    payload: Mapping[str, object]


def iter_codex_jsonl_events(stream: TextIO) -> Iterator[CodexStreamEvent]:
    """Yield :class:`CodexStreamEvent` objects from a JSONL stream.

    空行はスキップし、JSON のパースに失敗した場合や `type` フィールドが存在しない場合は ValueError を送出する。
    """

    for line_no, raw_line in enumerate(stream, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid JSON in codex stream at line {line_no}") from exc
        event_type = data.get("type")
        if not isinstance(event_type, str):
            raise ValueError(f"Missing event type in codex stream at line {line_no}")
        payload = {key: value for key, value in data.items() if key != "type"}
        yield CodexStreamEvent(type=event_type, payload=payload)


def load_codex_jsonl_events(source: Path | str) -> list[CodexStreamEvent]:
    """Convenience helper to load events from a file path."""

    path = Path(source)
    with path.open("r", encoding="utf-8") as stream:
        return list(iter_codex_jsonl_events(stream))


__all__ = [
    "CodexStreamEvent",
    "iter_codex_jsonl_events",
    "load_codex_jsonl_events",
]
