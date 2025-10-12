"""Utilities for preparing Python virtual environments prior to execution."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping


class VirtualEnvActivator:
    """Activate a Python virtual environment by adjusting environment variables."""

    def __init__(self, *, enabled: bool, default_venv_path: str | None = ".venv") -> None:
        self._enabled = enabled
        self._default_venv_path = default_venv_path

    def prepare(self, project_directory: Path, *, base_env: Mapping[str, str] | None = None) -> dict[str, str] | None:
        """Return an environment dict with the virtualenv activated, or ``None``."""

        if not self._enabled:
            return None

        venv_dir = self._resolve_virtualenv_dir(project_directory)
        if venv_dir is None:
            return None

        env = dict(base_env or os.environ)
        env["VIRTUAL_ENV"] = str(venv_dir)

        bin_dir = venv_dir / ("Scripts" if os.name == "nt" else "bin")
        prev_path = env.get("PATH", "")
        if prev_path:
            env["PATH"] = os.pathsep.join([str(bin_dir), prev_path])
        else:
            env["PATH"] = str(bin_dir)

        if os.name != "nt":
            env.pop("PYTHONHOME", None)

        return env

    def _resolve_virtualenv_dir(self, project_directory: Path) -> Path | None:
        candidate = None
        if self._default_venv_path:
            candidate = (project_directory / self._default_venv_path).resolve()
        if candidate and candidate.is_dir():
            return candidate

        # Fallback: use VIRTUAL_ENV from base environment if it resides under project.
        current_env = os.environ.get("VIRTUAL_ENV")
        if current_env:
            venv_path = Path(current_env).resolve()
            try:
                root = project_directory.resolve()
                if venv_path.is_dir() and venv_path.is_relative_to(root):
                    return venv_path
            except AttributeError:
                # Python < 3.9 compatibility: fallback to manual check
                try:
                    root = project_directory.resolve()
                    if venv_path.is_dir() and str(venv_path).startswith(str(root)):
                        return venv_path
                except Exception:
                    pass
            except Exception:
                pass
        return None


__all__ = ["VirtualEnvActivator"]
