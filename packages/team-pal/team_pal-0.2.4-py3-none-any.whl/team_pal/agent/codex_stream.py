"""Utilities for parsing codex exec JSONL event streams."""

from __future__ import annotations

import io
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


def parse_codex_stream_text(text: str) -> list[CodexStreamEvent]:
    """Parse Codex JSON/JSONL output into events with fallbacks.

    Attempts JSONL parsing first; if it fails, falls back to scanning the full
    payload for event dictionaries.
    """

    stripped = text.strip()
    if not stripped:
        return []

    stream = io.StringIO(stripped)
    try:
        return list(iter_codex_jsonl_events(stream))
    except ValueError:
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON in codex stream payload") from exc

        mappings = _collect_event_mappings(payload)
        if not mappings:
            raise ValueError("No codex events found in stream payload")
        events: list[CodexStreamEvent] = []
        for index, mapping in enumerate(mappings, start=1):
            events.append(_build_event(mapping, line_no=index, context="fallback payload"))
        return events


def _collect_event_mappings(payload: object, *, parent_key: str | None = None) -> list[Mapping[str, object]]:
    results: list[Mapping[str, object]] = []
    if isinstance(payload, Mapping):
        event_type = payload.get("type")
        if isinstance(event_type, str) and parent_key != "item":
            results.append(payload)
        for key, value in payload.items():
            results.extend(_collect_event_mappings(value, parent_key=key))
    elif isinstance(payload, list):
        for item in payload:
            results.extend(_collect_event_mappings(item, parent_key=parent_key))
    return results


__all__ = [
    "CodexStreamEvent",
    "iter_codex_jsonl_events",
    "load_codex_jsonl_events",
    "parse_codex_stream_text",
]
