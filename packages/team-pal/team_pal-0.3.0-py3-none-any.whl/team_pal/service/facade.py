"""Service façade and listener abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from team_pal.container import DependencyContainer, ProviderNotFoundError
from team_pal.localization import format_message

if TYPE_CHECKING:
    from team_pal.application.project_context import ProjectContextResolver


class InstructionListener(ABC):
    """Abstract base class for channel-specific instruction listeners."""

    def __init__(
        self,
        *,
        project_resolver: "ProjectContextResolver | None" = None,
        language: str = "en",
    ) -> None:
        self._project_resolver = project_resolver
        self._active_sessions: dict[str, str] = {}
        self._language = language

    @abstractmethod
    def start(self) -> None:
        """Begin listening for incoming instructions."""

    @abstractmethod
    def stop(self) -> None:
        """Stop listening for incoming instructions."""

    @abstractmethod
    def _complete_session(self, session_id: str) -> None:
        """Complete the session identified by ``session_id``."""

    def _remember_session(self, channel_id: str, session_id: str) -> None:
        self._active_sessions[channel_id] = session_id

    def _current_session_id(self, channel_id: str) -> str | None:
        return self._active_sessions.get(channel_id)

    def _complete_active_session(self, channel_id: str) -> str | None:
        session_id = self._active_sessions.pop(channel_id, None)
        if session_id:
            self._complete_session(session_id)
        return session_id

    # ------------------------------------------------------------------ #
    # Project selection helpers                                          #
    # ------------------------------------------------------------------ #
    def _project_selection_prompt(self) -> str:
        if self._project_resolver is None:
            return format_message("project.list.disabled", self._language)

        projects = self._project_resolver.list_projects()
        lines = [format_message("project.guard.header", self._language)]
        if projects:
            lines.append(format_message("project.guard.available_intro", self._language))
            for name in projects:
                display = self._format_project_display(name)
                lines.append(format_message("project.guard.available_item", self._language, name=display))
        else:
            lines.append(format_message("project.guard.none", self._language))
        lines.append(format_message("project.guard.hint", self._language))
        return "\n".join(lines)

    def _project_list_message(self) -> str:
        if self._project_resolver is None:
            return format_message("project.list.disabled", self._language)
        projects = self._project_resolver.list_projects()
        if not projects:
            return format_message("project.list.empty", self._language)
        active_path = self._project_resolver.get_active_project() if projects else None
        lines = []
        for name in projects:
            path = self._project_resolver.project_path_for(name)
            prefix = "*" if active_path == path else "-"
            display = self._format_project_display(name)
            lines.append(
                format_message(
                    "project.list.item",
                    self._language,
                    prefix=prefix,
                    name=display,
                    path=path,
                )
            )
        return "\n".join(lines)

    def _select_project(self, channel_id: str, project_name: str) -> str:
        if self._project_resolver is None:
            return format_message("project.select.disabled", self._language)
        self._complete_active_session(channel_id)
        try:
            project_path = self._project_resolver.select_project(project_name)
        except ValueError as exc:
            return str(exc)
        return format_message("project.select.success", self._language, path=project_path)

    def _project_selection_required_message(self) -> str | None:
        if self._project_resolver and self._project_resolver.is_selection_required():
            return self._project_selection_prompt()
        return None

    def _format_project_display(self, name: str) -> str:
        if name == ".":
            return format_message("project.display.root", self._language)
        return name


class ResultDispatcher(ABC):
    """Protocol for dispatching execution results back to a channel."""

    @abstractmethod
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
