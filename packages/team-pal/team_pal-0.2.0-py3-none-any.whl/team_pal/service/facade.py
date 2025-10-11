"""Service façade that resolves channel-specific components via a DI container."""

from __future__ import annotations

from typing import Protocol, runtime_checkable, cast

from team_pal.container import DependencyContainer, ProviderNotFoundError


@runtime_checkable
class InstructionListener(Protocol):
    """Protocol for channel-specific instruction listeners."""

    def start(self) -> None:
        """Begin listening for incoming instructions."""

    def stop(self) -> None:
        """Stop listening for incoming instructions."""


@runtime_checkable
class ResultDispatcher(Protocol):
    """Protocol for dispatching execution results back to a channel."""

    def dispatch(self, instruction_id: str, payload: object) -> None:
        """Send a result payload for the given instruction identifier."""


class TeamPalService:
    """Resolves instruction listeners and result dispatchers using a DI container."""

    def __init__(self, container: DependencyContainer) -> None:
        self._container = container

    def create_instruction_listener(self, channel: str) -> InstructionListener:
        """Return the registered listener for the target channel."""

        return cast(InstructionListener, self._resolve("instruction_listener", channel))

    def create_result_dispatcher(self, channel: str) -> ResultDispatcher:
        """Return the registered dispatcher for the target channel."""

        return cast(ResultDispatcher, self._resolve("result_dispatcher", channel))

    def _resolve(self, component_prefix: str, channel: str):
        key = f"{component_prefix}:{channel}"
        return self._container.resolve(key)


__all__ = [
    "InstructionListener",
    "ResultDispatcher",
    "TeamPalService",
    "ProviderNotFoundError",
]
