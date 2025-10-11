"""Slack Socket Mode client abstraction."""

from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Iterator, Mapping, Protocol, Sequence

try:  # pragma: no cover - optional dependency import
    from slack_sdk.errors import SlackApiError
    from slack_sdk.socket_mode import SocketModeClient
    from slack_sdk.socket_mode.request import SocketModeRequest
    from slack_sdk.socket_mode.response import SocketModeResponse
    from slack_sdk.web import WebClient
except Exception as exc:  # pragma: no cover - executed when slack_sdk is missing
    SlackApiError = None  # type: ignore
    SocketModeClient = None  # type: ignore
    SocketModeRequest = None  # type: ignore
    SocketModeResponse = None  # type: ignore
    WebClient = None  # type: ignore


log = logging.getLogger(__name__)


class SlackClientError(RuntimeError):
    """Raised when Slack operations fail."""


@dataclass(frozen=True)
class SlackEvent:
    """Represents an event received via Socket Mode."""

    envelope_id: str
    type: str
    team_id: str | None
    payload: Mapping[str, Any]
    received_at: float


@dataclass(frozen=True)
class SlackMessage:
    """Represents a Slack message entity."""

    channel: str
    ts: str
    user: str | None
    text: str
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class SlackPostResponse:
    """Response returned after posting a message."""

    ok: bool
    channel: str
    ts: str
    raw: Mapping[str, Any] | None


class SlackClientProtocol(Protocol):
    """Protocol for Slack client implementations."""

    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def fetch_events(self) -> Iterable[SlackEvent]: ...

    def ack(self, envelope_id: str) -> None: ...

    def post_message(
        self,
        channel: str,
        text: str,
        *,
        thread_ts: str | None = None,
        blocks: Sequence[Mapping[str, Any]] | None = None,
    ) -> SlackPostResponse: ...

    def fetch_thread_messages(self, channel: str, thread_ts: str) -> Sequence[SlackMessage]: ...


SocketClientFactory = Callable[[str, str], tuple[Any, Any]]


class SlackSocketClient(SlackClientProtocol):
    """Concrete Slack client using Socket Mode for event delivery."""

    def __init__(
        self,
        *,
        bot_token: str,
        app_token: str,
        signing_secret: str | None = None,
        default_channel: str | None = None,
        socket_client_factory: Callable[[str, str], tuple[Any, Any]] | None = None,
        backoff_seconds: Sequence[float] | None = None,
    ) -> None:
        if SocketModeClient is None or WebClient is None:
            raise SlackClientError("slack_sdk is required but not installed")

        self._bot_token = bot_token
        self._app_token = app_token
        self._signing_secret = signing_secret
        self._default_channel = default_channel
        self._socket_client_factory = socket_client_factory or self._default_factory
        self._backoff_sequence = backoff_seconds or (1, 2, 4, 8, 16, 30)

        self._queue: queue.Queue[SlackEvent] = queue.Queue()
        self._connected = False
        self._lock = threading.Lock()
        self._socket_client: SocketModeClient | None = None
        self._web_client: WebClient | None = None

    def connect(self) -> None:
        with self._lock:
            if self._connected:
                return

            socket_client, web_client = self._socket_client_factory(self._app_token, self._bot_token)
            self._socket_client = socket_client
            self._web_client = web_client
            self._socket_client.socket_mode_request_listeners.append(self._handle_socket_request)

            for attempt, delay in enumerate(self._backoff_sequence, start=1):
                try:
                    self._socket_client.connect()
                    self._connected = True
                    log.info("Slack Socket Mode connected on attempt %s", attempt)
                    break
                except Exception as exc:  # pragma: no cover - network failures hard to reproduce
                    log.warning("Slack connection attempt %s failed: %s", attempt, exc)
                    time.sleep(delay)
            else:  # pragma: no cover - executed if all attempts fail
                raise SlackClientError("Failed to connect to Slack Socket Mode")

    def disconnect(self) -> None:
        with self._lock:
            if not self._connected or self._socket_client is None:
                return
            try:
                self._socket_client.disconnect()
            except AttributeError:  # pragma: no cover - legacy API fallback
                self._socket_client.close()
            finally:
                self._connected = False

    def fetch_events(self) -> Iterator[SlackEvent]:
        while self._connected or not self._queue.empty():
            try:
                event = self._queue.get(timeout=0.1)
                yield event
            except queue.Empty:
                continue

    def ack(self, envelope_id: str) -> None:
        if not self._socket_client:
            raise SlackClientError("Socket client not connected")
        response = SocketModeResponse(envelope_id=envelope_id)
        self._socket_client.send_socket_mode_response(response)

    def post_message(
        self,
        channel: str,
        text: str,
        *,
        thread_ts: str | None = None,
        blocks: Sequence[Mapping[str, Any]] | None = None,
    ) -> SlackPostResponse:
        if self._web_client is None:
            raise SlackClientError("Web client not initialized")

        try:
            result = self._web_client.chat_postMessage(
                channel=channel or self._default_channel,
                text=text,
                thread_ts=thread_ts,
                blocks=list(blocks) if blocks is not None else None,
            )
        except SlackApiError as exc:  # pragma: no cover - depends on remote API
            raise SlackClientError(f"Failed to post message: {exc}") from exc

        return SlackPostResponse(
            ok=bool(result.get("ok", False)),
            channel=str(result.get("channel")),
            ts=str(result.get("ts")),
            raw=result.data if hasattr(result, "data") else result,
        )

    def fetch_thread_messages(self, channel: str, thread_ts: str) -> Sequence[SlackMessage]:
        if self._web_client is None:
            raise SlackClientError("Web client not initialized")

        try:
            response = self._web_client.conversations_replies(channel=channel, ts=thread_ts)
        except SlackApiError as exc:  # pragma: no cover - depends on remote API
            raise SlackClientError(f"Failed to fetch thread messages: {exc}") from exc

        messages: list[SlackMessage] = []
        for message in response.get("messages", []):
            messages.append(
                SlackMessage(
                    channel=channel,
                    ts=str(message.get("ts")),
                    user=message.get("user"),
                    text=message.get("text", ""),
                    raw=message,
                )
            )
        return messages

    # Internal helpers -----------------------------------------------------

    def _default_factory(self, app_token: str, bot_token: str):
        web_client = WebClient(token=bot_token)
        socket_client = SocketModeClient(app_token=app_token, web_client=web_client)
        return socket_client, web_client

    def _handle_socket_request(self, client: SocketModeClient, request: SocketModeRequest) -> None:
        if request.type == "hello":  # pragma: no cover - handshake event
            log.debug("Received Slack hello event")
            return

        event = SlackEvent(
            envelope_id=request.envelope_id,
            type=request.type,
            team_id=request.payload.get("team_id") or request.payload.get("team"),
            payload=request.payload,
            received_at=time.time(),
        )
        self._queue.put(event)


__all__ = [
    "SlackClientError",
    "SlackClientProtocol",
    "SlackEvent",
    "SlackMessage",
    "SlackPostResponse",
    "SlackSocketClient",
]
