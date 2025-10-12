"""Formatting helpers for localized messages."""

from __future__ import annotations

from .messages import MESSAGES

SUPPORTED_LANGUAGES = {"en", "ja"}


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


def format_message(message_id: str, language: str, **kwargs) -> str:
    """Return the localized message for ``message_id``.

    Parameters
    ----------
    message_id:
        Identifier of the message entry in the catalog.
    language:
        Language code (``ja`` or ``en``). Other values fall back to English.
    kwargs:
        Placeholder values interpolated via :py:meth:`str.format`.
    """

    target_lang = _normalize_language(language) or "en"
    if target_lang not in SUPPORTED_LANGUAGES:
        target_lang = "en"

    catalog = MESSAGES.get(message_id)
    if not catalog:
        return message_id  # Fallback to message id for missing entries.

    template = catalog.get(target_lang) or catalog.get("en")
    if template is None:
        return message_id
    return template.format(**kwargs)


__all__ = ["format_message", "SUPPORTED_LANGUAGES"]
