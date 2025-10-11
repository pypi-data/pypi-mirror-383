"""Project context management for multi-project mode."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class ProjectSelectionRequiredError(RuntimeError):
    """Raised when a project must be selected before executing commands."""

    projects: Sequence[str]
    root_directory: Path

    def __str__(self) -> str:
        return "Project selection required"


class ProjectContextResolver:
    """Resolves and tracks the active project directory for sessions."""

    def __init__(self, *, root_directory: Path, multi_project_enabled: bool) -> None:
        self._root = root_directory.resolve()
        self._multi_project_enabled = multi_project_enabled
        self._session_projects: Dict[str, Path] = {}
        self._active_project: Path = self._root
        self._selection_made: bool = not multi_project_enabled

    # ------------------------------------------------------------------ #
    # Project discovery / selection                                      #
    # ------------------------------------------------------------------ #
    def list_projects(self) -> List[str]:
        """Return a list of available project identifiers."""

        if not self._multi_project_enabled:
            return ["."]

        try:
            entries: Sequence[Path] = list(self._root.iterdir())
        except FileNotFoundError:
            return ["."]

        projects = sorted(
            {entry.name for entry in entries if entry.is_dir()}
        )
        return ["."] + projects

    def select_project(self, project_name: str) -> Path:
        """Select a project as the active context."""

        project_path = self._resolve_project_path(project_name)
        self._active_project = project_path
        self._selection_made = True
        return project_path

    def get_active_project(self) -> Path:
        """Return the currently active project directory."""

        return self._active_project

    def has_active_selection(self) -> bool:
        """Return True when a project has been explicitly selected."""

        return self._selection_made

    def is_selection_required(self) -> bool:
        """Return True if multi-project mode demands an explicit selection."""

        return self._multi_project_enabled and not self._selection_made

    def selection_required_error(self) -> ProjectSelectionRequiredError:
        """Return a structured error indicating a project must be selected."""

        return ProjectSelectionRequiredError(
            projects=tuple(self.list_projects()),
            root_directory=self._root,
        )

    # ------------------------------------------------------------------ #
    # Session association                                                #
    # ------------------------------------------------------------------ #
    def assign_session(self, session_id: str, *, project_name: str | None = None) -> Path:
        """Associate a session with the given project (or active project)."""

        if project_name is not None:
            project_path = self._resolve_project_path(project_name)
            self._active_project = project_path
            self._selection_made = True
        else:
            if self.is_selection_required():
                raise self.selection_required_error()
            project_path = self._active_project
        self._session_projects[session_id] = project_path
        return project_path

    def get_session_project(self, session_id: str) -> Path:
        """Return the project directory associated with the session."""

        return self._session_projects.get(session_id, self._active_project)

    def clear_session(self, session_id: str) -> None:
        """Remove session → project association."""

        self._session_projects.pop(session_id, None)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    def _resolve_project_path(self, project_name: str) -> Path:
        if project_name in {"", "."} or not self._multi_project_enabled:
            return self._root

        candidate = (self._root / project_name).resolve()
        if not candidate.is_dir() or os.path.commonpath([str(candidate), str(self._root)]) != str(self._root):
            raise ValueError(f"Project '{project_name}' not found under {self._root}")
        return candidate

    def project_path_for(self, project_name: str) -> Path:
        """Return the resolved project path without mutating state."""

        return self._resolve_project_path(project_name)

    def root_directory(self) -> Path:
        """Expose the configured root directory."""

        return self._root


__all__ = ["ProjectContextResolver", "ProjectSelectionRequiredError"]
