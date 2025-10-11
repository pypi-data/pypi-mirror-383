"""Configuration loader for Team Pal."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

try:  # pragma: no cover - import guard
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - fallback when python-dotenv is unavailable
    load_dotenv = None

ENV_PREFIX = "TEAM_PAL_"
_DOTENV_LOADED = False


@dataclass(frozen=True)
class AppConfig:
    """Application configuration values."""

    environment: str = "development"
    log_level: str = "INFO"
    default_input_channel: str = "cli"
    slack_bot_token: str | None = None
    slack_app_token: str | None = None
    slack_signing_secret: str | None = None
    slack_default_channel: str | None = None
    slack_allow_channel_messages: bool = False
    slack_watched_channels: str | None = None
    codex_cli_binary_path: str | None = None
    codex_cli_timeout_seconds: int = 300
    cli_history_path: str | None = None


def load_config(*, env: Mapping[str, str] | None = None) -> AppConfig:
    """Load configuration values from environment variables.

    Parameters
    ----------
    env:
        Optional mapping that overrides the process environment, provided mainly
        for testing. When omitted, :data:`os.environ` is used.
    """

    _load_dotenv_if_available(env is None)

    source: Mapping[str, str] = os.environ
    overrides: Mapping[str, str] = env or {}

    def _get(name: str, default: str | None = None) -> str | None:
        if env is not None:
            return overrides.get(name, default)
        return source.get(name, default)

    environment = _get(f"{ENV_PREFIX}ENVIRONMENT", AppConfig.environment)
    log_level = (_get(f"{ENV_PREFIX}LOG_LEVEL", AppConfig.log_level) or "INFO").upper()
    default_input_channel = _get(f"{ENV_PREFIX}DEFAULT_INPUT_CHANNEL", AppConfig.default_input_channel)
    slack_bot_token = _get(f"{ENV_PREFIX}SLACK_BOT_TOKEN", None)
    slack_app_token = _get(f"{ENV_PREFIX}SLACK_APP_TOKEN", None)
    slack_signing_secret = _get(f"{ENV_PREFIX}SLACK_SIGNING_SECRET", None)
    slack_default_channel = _get(f"{ENV_PREFIX}SLACK_DEFAULT_CHANNEL", None)
    slack_allow_channel_messages_raw = _get(f"{ENV_PREFIX}SLACK_ALLOW_CHANNEL_MESSAGES", "false")
    slack_watched_channels = _get(f"{ENV_PREFIX}SLACK_WATCHED_CHANNELS", None)
    codex_cli_binary_path = _get(f"{ENV_PREFIX}CLI_BINARY_PATH", None)
    timeout_raw = _get(f"{ENV_PREFIX}CLI_TIMEOUT_SECONDS", str(AppConfig.codex_cli_timeout_seconds))
    cli_history_path = _get(f"{ENV_PREFIX}CLI_HISTORY_PATH", None)

    try:
        timeout_seconds = int(timeout_raw) if timeout_raw is not None else AppConfig.codex_cli_timeout_seconds
    except ValueError as exc:
        raise ValueError("TEAM_PAL_CLI_TIMEOUT_SECONDS must be an integer") from exc

    return AppConfig(
        environment=str(environment),
        log_level=str(log_level),
        default_input_channel=(default_input_channel or AppConfig.default_input_channel).strip().lower() or AppConfig.default_input_channel,
        slack_bot_token=slack_bot_token if slack_bot_token else None,
        slack_app_token=slack_app_token if slack_app_token else None,
        slack_signing_secret=slack_signing_secret if slack_signing_secret else None,
        slack_default_channel=slack_default_channel if slack_default_channel else None,
        slack_allow_channel_messages=str(slack_allow_channel_messages_raw).lower() in {"true", "1", "yes", "y"},
        slack_watched_channels=slack_watched_channels if slack_watched_channels else None,
        codex_cli_binary_path=codex_cli_binary_path if codex_cli_binary_path else None,
        codex_cli_timeout_seconds=timeout_seconds,
        cli_history_path=cli_history_path if cli_history_path else None,
    )


def _load_dotenv_if_available(should_load: bool) -> None:
    global _DOTENV_LOADED
    if not should_load or _DOTENV_LOADED or load_dotenv is None:
        return
    load_dotenv()
    _DOTENV_LOADED = True


__all__ = ["AppConfig", "ENV_PREFIX", "load_config"]
