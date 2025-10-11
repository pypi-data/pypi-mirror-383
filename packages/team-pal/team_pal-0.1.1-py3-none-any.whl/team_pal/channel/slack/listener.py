"""Slack instruction listener implementation."""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from team_pal.channel.slack.client import SlackClientProtocol, SlackEvent
from team_pal.application.execution_service import InstructionExecutionService
from team_pal.domain.instruction import Instruction
from team_pal.service.facade import InstructionListener


log = logging.getLogger(__name__)


class SlackInstructionFactory(Protocol):
    """Protocol for building instructions from Slack events."""

    def from_event(self, event: SlackEvent) -> Instruction: ...


@dataclass
class DefaultSlackInstructionFactory(SlackInstructionFactory):
    """Convert Slack events into Team Pal instructions."""

    def from_event(self, event: SlackEvent) -> Instruction:
        payload = event.payload.get("event", {})
        instruction_id = str(payload.get("client_msg_id") or payload.get("ts") or event.envelope_id)
        metadata: Mapping[str, object] = {
            "user": payload.get("user"),
            "channel": payload.get("channel"),
            "thread_ts": payload.get("thread_ts") or payload.get("ts"),
            "team_id": payload.get("team"),
        }
        requested_outputs = {"channel": payload.get("channel")} if payload.get("channel") else {}
        return Instruction(
            instruction_id=instruction_id,
            channel="slack",
            source_metadata=metadata,
            payload=payload.get("text") or payload,
            requested_outputs=requested_outputs,
        )


class SlackInstructionListener(InstructionListener):
    """Listens for Slack events and dispatches instructions for execution."""

    def __init__(
        self,
        *,
        slack_client: SlackClientProtocol,
        instruction_factory: SlackInstructionFactory | None = None,
        execution_service: InstructionExecutionService,
        poll_interval: float = 1.0,
        allow_channel_messages: bool = False,
        watched_channels: Sequence[str] | None = None,
    ) -> None:
        self._client = slack_client
        self._factory = instruction_factory or DefaultSlackInstructionFactory()
        self._execution_service = execution_service
        self._poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._processed_event_ids: deque[str] = deque(maxlen=1024)
        self._processed_event_set: set[str] = set()
        self._started_at: float = 0.0
        self._allow_channel_messages = allow_channel_messages
        self._watched_channels = set(watched_channels or [])

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._started_at = time.time()
        self._client.connect()
        self._thread = threading.Thread(target=self._run, name="SlackInstructionListener", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._client.disconnect()
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    # Internal helpers -----------------------------------------------------

    def _run(self) -> None:
        while not self._stop_event.is_set():
            for event in self._client.fetch_events():
                if self._stop_event.is_set():
                    break
                self._process_event(event)
            time.sleep(self._poll_interval)

    def _process_event(self, event: SlackEvent) -> None:
        payload = event.payload.get("event", {}) if isinstance(event.payload, Mapping) else {}
        event_type = payload.get("type")
        envelope_event_id = event.payload.get("event_id") if isinstance(event.payload, Mapping) else None
        event_id = payload.get("event_id") or envelope_event_id
        event_ts = _extract_event_ts(payload)

        start_ts = getattr(self, "_started_at", 0.0)
        if event_ts is not None and start_ts and event_ts < start_ts - 1.0:
            self._safe_ack(event)
            return

        if event_id and event_id in self._processed_event_set:
            self._safe_ack(event)
            return

        if event_type == "message":
            channel_type = payload.get("channel_type")
            subtype = payload.get("subtype")
            bot_id = payload.get("bot_id")
            channel_id = payload.get("channel")
            if subtype or bot_id:
                self._safe_ack(event)
                return
            if channel_type == "im":
                pass
            elif self._allow_channel_messages and channel_id and channel_id in self._watched_channels:
                pass
            else:
                self._safe_ack(event)
                return
        elif event_type != "app_mention":
            self._safe_ack(event)
            return

        try:
            if event_id:
                self._remember_event(event_id)
            instruction = self._factory.from_event(event)
        except Exception as exc:  # pragma: no cover - conversion errors rare
            log.exception("Failed to convert Slack event %s into instruction: %s", event.envelope_id, exc)
            self._safe_ack(event)
            return

        try:
            self._execution_service.new_session(instruction)
        finally:
            self._safe_ack(event)

    def _safe_ack(self, event: SlackEvent) -> None:
        try:
            self._client.ack(event.envelope_id)
        except Exception as exc:  # pragma: no cover - ack failures are logged
            log.warning("Failed to ack Slack event %s: %s", event.envelope_id, exc)

    def _remember_event(self, event_id: str) -> None:
        if event_id in self._processed_event_set:
            return
        if len(self._processed_event_ids) == self._processed_event_ids.maxlen:
            old = self._processed_event_ids.popleft()
            self._processed_event_set.discard(old)
        self._processed_event_ids.append(event_id)
        self._processed_event_set.add(event_id)


__all__ = [
    "SlackInstructionFactory",
    "SlackInstructionListener",
    "DefaultSlackInstructionFactory",
]


def _extract_event_ts(payload: Mapping[str, object]) -> float | None:
    ts = payload.get("ts") or payload.get("event_ts")
    if isinstance(ts, str):
        try:
            return float(ts)
        except ValueError:  # pragma: no cover - malformed ts
            return None
    if isinstance(ts, (int, float)):
        return float(ts)
    return None
