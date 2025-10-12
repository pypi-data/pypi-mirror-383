"""Language detection utilities."""

from __future__ import annotations

import locale
import logging
import os
from dataclasses import replace

from typing import Mapping

from team_pal.config.loader import AppConfig

_LOGGER = logging.getLogger("team_pal.localization")

_ENV_KEYS_POSIX = ("LANG", "LC_ALL", "LC_MESSAGES")


def _normalize_language(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.lower().strip()
    if not normalized:
        return None
    if "_" in normalized:
        normalized = normalized.split("_", 1)[0]
    if "-" in normalized:
        normalized = normalized.split("-", 1)[0]
    return normalized


def resolve_language(
    *,
    cli_language: str | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    """Return the resolved language code (``ja`` or ``en``)."""

    language = _normalize_language(cli_language)
    source_env: Mapping[str, str] = env or os.environ

    if language is None:
        language = _normalize_language(source_env.get("TEAM_PAL_LANG"))
    if language is None:
        for key in _ENV_KEYS_POSIX:
            language = _normalize_language(source_env.get(key))
            if language:
                break
    if language is None:
        locale_lang, _ = locale.getdefaultlocale()  # type: ignore[deprecated-call]
        language = _normalize_language(locale_lang)

    if language == "ja":
        return "ja"
    return "en"


def detect_language(config: AppConfig, *, cli_language: str | None = None) -> AppConfig:
    """Return ``config`` with the ``language`` attribute resolved."""

    language = resolve_language(cli_language=cli_language)

    if language != config.language:
        _LOGGER.debug("Resolved interface language: %s", language)
        return replace(config, language=language)
    return config


__all__ = ["detect_language", "resolve_language"]
