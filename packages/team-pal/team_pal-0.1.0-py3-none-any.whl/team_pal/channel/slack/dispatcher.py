"""Slack result dispatcher implementation."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence, TextIO

from team_pal.channel.slack.client import SlackClientProtocol, SlackPostResponse
from team_pal.domain.execution import ExecutionError, ExecutionResult, ExecutionStatus
from team_pal.service.facade import ResultDispatcher


class SlackResponseFormatter(Protocol):
    """Formats execution results into Slack message payloads."""

    def format(self, instruction_id: str, result: ExecutionResult) -> Mapping[str, object]: ...


@dataclass
class DefaultSlackResponseFormatter(SlackResponseFormatter):
    """Formats execution results to minimal Slack text messages."""

    def format(self, instruction_id: str, result: ExecutionResult) -> Mapping[str, object]:
        text = self._determine_text(instruction_id, result)
        return {
            "channel": result.instruction.requested_outputs.get("channel") if isinstance(result.instruction.requested_outputs, Mapping) else None,
            "text": text,
            "thread_ts": None,
            "blocks": None,
        }

    def _determine_text(self, instruction_id: str, result: ExecutionResult) -> str:
        final_message = _extract_final_message(result.output)
        if final_message:
            return final_message
        if isinstance(result.output, str) and result.output.strip():
            return result.output.strip()
        if isinstance(result.output, Mapping):
            exit_code = result.output.get("exit_code")
            if exit_code is not None:
                return f"Execution finished (exit_code={exit_code})."
        if result.error:
            return f":x: {result.error.message}"
        if result.status is ExecutionStatus.SUCCESS:
            return ":white_check_mark: Execution completed successfully."
        return f":warning: Execution finished for `{instruction_id}`."


class SlackResultDispatcher(ResultDispatcher):
    """Dispatches execution results to Slack via the configured client."""

    def __init__(
        self,
        *,
        slack_client: SlackClientProtocol,
        response_formatter: SlackResponseFormatter | None = None,
        default_channel: str | None = None,
        debug: bool = False,
        log_output: TextIO | None = None,
    ) -> None:
        self._client = slack_client
        self._formatter = response_formatter or DefaultSlackResponseFormatter()
        self._default_channel = default_channel
        self._debug = debug
        self._log_output = log_output or sys.stdout

    def dispatch(self, instruction_id: str, payload: object) -> SlackPostResponse:
        if not isinstance(payload, ExecutionResult):
            raise TypeError("SlackResultDispatcher expects an ExecutionResult payload")

        formatted = self._formatter.format(instruction_id, payload)
        channel = formatted.get("channel")
        if not channel and self._default_channel:
            channel = self._default_channel
        if not channel and isinstance(payload.instruction.requested_outputs, Mapping):
            channel = payload.instruction.requested_outputs.get("channel")
        if not channel:
            raise ValueError("No Slack channel specified for result dispatch")

        text = formatted.get("text") or self._build_fallback_text(payload)
        thread_ts = formatted.get("thread_ts")
        blocks = formatted.get("blocks")
        if blocks is not None and not isinstance(blocks, Sequence):
            raise TypeError("Slack blocks must be a sequence of block payloads")

        response = self._client.post_message(
            channel=str(channel),
            text=str(text),
            thread_ts=str(thread_ts) if thread_ts else None,
            blocks=blocks,  # type: ignore[arg-type]
        )
        if self._debug:
            summary = {
                "instruction_id": instruction_id,
                "channel": channel,
                "thread_ts": thread_ts,
                "text": text,
                "status": payload.status.value,
                "output": payload.output,
            }
            self._log_output.write(json.dumps(summary, ensure_ascii=False, default=str, indent=2) + "\n")
            self._log_output.flush()

        return response

    def _build_fallback_text(self, result: ExecutionResult) -> str:
        if result.status is ExecutionStatus.SUCCESS:
            return ":white_check_mark: Execution completed successfully."
        if isinstance(result.error, ExecutionError):
            return f":x: Execution failed: {result.error.message}"
        return ":warning: Execution finished with no output."


__all__ = [
    "SlackResultDispatcher",
    "SlackResponseFormatter",
    "DefaultSlackResponseFormatter",
]


def _extract_final_message(output: object) -> str | None:
    if isinstance(output, str):
        value = output.strip()
        return value or None
    if isinstance(output, Mapping):
        final = output.get("final_message")
        if isinstance(final, str) and final.strip():
            return final.strip()
        events = output.get("events")
        if isinstance(events, Sequence):
            for event in events:
                if not isinstance(event, Mapping):
                    continue
                if event.get("type") == "item.completed":
                    payload = event.get("payload")
                    if isinstance(payload, Mapping):
                        item = payload.get("item")
                        if isinstance(item, Mapping) and item.get("type") == "agent_message":
                            text = item.get("text")
                            if isinstance(text, str) and text.strip():
                                return text.strip()
    return None
