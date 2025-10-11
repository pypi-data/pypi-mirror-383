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


def _build_event(data: Mapping[str, object], *, line_no: int, context: str | None = None) -> CodexStreamEvent:
    event_type = data.get("type")
    if not isinstance(event_type, str):
        suffix = f" ({context})" if context else ""
        raise ValueError(f"Missing event type in codex stream at line {line_no}{suffix}")
    payload = {key: value for key, value in data.items() if key != "type"}
    return CodexStreamEvent(type=event_type, payload=payload)


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
        if isinstance(data, Mapping):
            if isinstance(data.get("type"), str):
                yield _build_event(data, line_no=line_no)
                continue
            events_field = data.get("events")
            if isinstance(events_field, list):
                for index, raw_event in enumerate(events_field, start=1):
                    if not isinstance(raw_event, Mapping):
                        raise ValueError(
                            f"Invalid event payload in codex stream wrapper at line {line_no} (index {index})"
                        )
                    yield _build_event(raw_event, line_no=line_no, context=f"wrapper event #{index}")
                continue
        elif isinstance(data, list):
            for index, raw_event in enumerate(data, start=1):
                if not isinstance(raw_event, Mapping):
                    raise ValueError(
                        f"Invalid event payload in codex stream array at line {line_no} (index {index})"
                    )
                yield _build_event(raw_event, line_no=line_no, context=f"array event #{index}")
            continue
        raise ValueError(f"Missing event type in codex stream at line {line_no}")


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
