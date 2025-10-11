"""Slack instruction listener implementation."""

from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from team_pal.channel.slack.client import SlackClientProtocol, SlackEvent
from team_pal.application.execution_service import InstructionExecutionService
from team_pal.application.project_context import ProjectContextResolver
from team_pal.domain.instruction import Instruction
from team_pal.domain.session import InstructionSession, SessionHistoryEntry
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
        project_resolver: ProjectContextResolver | None = None,
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
        self._project_resolver = project_resolver

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

        if self._try_handle_command(event, payload):
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

    def _try_handle_command(self, event: SlackEvent, payload: Mapping[str, object]) -> bool:
        text = payload.get("text")
        if not isinstance(text, str):
            return False

        command_text = text.strip()
        # Remove leading mention tokens (e.g. "<@U123>")
        if command_text.startswith("<@"):
            parts = command_text.split(maxsplit=1)
            if len(parts) == 2:
                command_text = parts[1].strip()
            else:
                command_text = ""
        if not command_text.startswith("$"):
            return False

        tokens = command_text.split()
        if not tokens:
            return False

        verb = tokens[0]
        channel_id = payload.get("channel") or event.payload.get("channel")
        if not channel_id:
            return False

        if verb in {"$list", "$ls"}:
            channel_filter = None
            as_json = False
            args = tokens[1:]
            idx = 0
            while idx < len(args):
                token = args[idx]
                if token == "--json":
                    as_json = True
                elif token == "--channel" and idx + 1 < len(args):
                    channel_filter = args[idx + 1]
                    idx += 1
                idx += 1

            sessions = self._execution_service.list_sessions(channel=channel_filter)
            message = self._format_session_list(sessions, as_json=as_json)
            self._post_command_response(channel_id, message)
            return True

        if verb in {"$status", "$st"}:
            if len(tokens) < 2:
                self._post_command_response(channel_id, "Usage: $status <session_id> [--json]")
                return True
            session_id = tokens[1]
            as_json = "--json" in tokens[2:]
            session = self._execution_service.get_session(session_id)
            if session is None:
                self._post_command_response(channel_id, f"Session {session_id} was not found.")
            else:
                message = self._format_session_detail(session, as_json=as_json)
                self._post_command_response(channel_id, message)
            return True

        if verb in {"$project_list", "$pl"}:
            if self._project_resolver is None:
                self._post_command_response(channel_id, "Multi-project mode is disabled.")
            else:
                projects = self._project_resolver.list_projects()
                active_path = self._project_resolver.get_active_project() if projects else None
                if not projects:
                    message = "No projects discovered under the root directory."
                else:
                    lines = []
                    for name in projects:
                        path = self._project_resolver.project_path_for(name)
                        prefix = "*" if active_path == path else "-"
                        display_name = name if name != "." else ". (root)"
                        lines.append(f"{prefix} {display_name} -> {path}")
                    message = "\n".join(lines)
                self._post_command_response(channel_id, message)
            return True

        if verb in {"$project_select", "$ps"}:
            if len(tokens) < 2:
                self._post_command_response(channel_id, "Usage: $project_select <project_name>")
                return True
            if self._project_resolver is None:
                self._post_command_response(channel_id, "Multi-project mode is disabled.")
                return True
            project_name = tokens[1]
            try:
                project_path = self._project_resolver.select_project(project_name)
                message = f"Active project set to {project_path}"
            except ValueError as exc:
                message = str(exc)
            self._post_command_response(channel_id, message)
            return True

        return False

    def _format_session_list(self, sessions: Sequence["InstructionSession"], *, as_json: bool) -> str:
        if as_json:
            payload = [
                {
                    "session_id": session.session_id,
                    "channel": session.channel,
                    "status": session.status.value,
                    "updated_at": session.updated_at.isoformat(),
                }
                for session in sessions
            ]
            return json.dumps({"sessions": payload}, ensure_ascii=False, indent=2)

        if not sessions:
            return "No sessions recorded."

        lines = ["session_id\tchannel\tstatus\tupdated_at"]
        for session in sessions:
            lines.append(
                f"{session.session_id}\t{session.channel}\t{session.status.value}\t{session.updated_at.isoformat()}"
            )
        return "\n".join(lines)

    def _format_session_detail(self, session: InstructionSession, *, as_json: bool) -> str:
        if as_json:
            return json.dumps({"session": self._serialize_session(session)}, ensure_ascii=False, indent=2)

        lines = [
            f"Session {session.session_id}",
            f"Channel: {session.channel}",
            f"Status: {session.status.value}",
            f"Updated: {session.updated_at.isoformat()}",
            "History:",
        ]
        if not session.history:
            lines.append("  (no entries)")
        else:
            for entry in session.history:
                payload = entry.instruction.payload
                if isinstance(payload, Mapping) and "text" in payload:
                    prompt = payload["text"]
                else:
                    prompt = payload
                lines.append(
                    f"  - {entry.timestamp.isoformat()} -> {entry.result.status.value}: {prompt}"
                )
        return "\n".join(lines)

    def _serialize_session(self, session: InstructionSession) -> dict[str, object]:
        return {
            "session_id": session.session_id,
            "channel": session.channel,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "history": [self._serialize_history(entry) for entry in session.history],
        }

    def _serialize_history(self, entry: SessionHistoryEntry) -> dict[str, object]:
        return {
            "prompt": entry.instruction.payload,
            "status": entry.result.status.value,
            "timestamp": entry.timestamp.isoformat(),
        }

    def _post_command_response(self, channel_id: str, message: str) -> None:
        try:
            self._client.post_message(channel=str(channel_id), text=message)
        except Exception as exc:  # pragma: no cover - network errors
            log.exception("Failed to post Slack command response: %s", exc)


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
