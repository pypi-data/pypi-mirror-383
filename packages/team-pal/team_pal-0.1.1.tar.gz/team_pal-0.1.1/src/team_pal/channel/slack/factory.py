"""Dependency injection helpers for Slack components."""

from __future__ import annotations

import sys
from typing import Callable, TextIO

from team_pal.application.execution_service import ResultDispatcherRegistry
from team_pal.channel.slack.client import SlackSocketClient
from team_pal.channel.slack.dispatcher import DefaultSlackResponseFormatter, SlackResultDispatcher
from team_pal.channel.slack.listener import SlackInstructionListener
from team_pal.config.loader import AppConfig
from team_pal.container import DependencyContainer


SlackClientBuilder = Callable[[AppConfig], SlackSocketClient]


def register_slack_components(
    container: DependencyContainer,
    config: AppConfig,
    *,
    slack_client_builder: SlackClientBuilder | None = None,
    debug: bool = False,
    log_output: TextIO | None = None,
) -> None:
    """Register Slack-specific providers in the dependency container."""

    client_builder = slack_client_builder or _default_client_builder

    container.register_factory(
        "slack:client",
        lambda _c: client_builder(config),
        scope="singleton",
    )

    def _listener_factory(c):
        watched = []
        if config.slack_watched_channels:
            watched = [channel.strip() for channel in config.slack_watched_channels.split(",") if channel.strip()]
        return SlackInstructionListener(
            slack_client=c.resolve("slack:client"),
            execution_service=c.resolve("service:instruction_execution"),
            poll_interval=0.1,
            allow_channel_messages=config.slack_allow_channel_messages,
            watched_channels=watched,
        )

    container.register_factory(
        "instruction_listener:slack",
        _listener_factory,
        scope="singleton",
    )

    container.register_factory(
        "result_dispatcher:slack",
        lambda c: _build_slack_dispatcher(c, config, debug=debug, log_output=log_output),
        scope="singleton",
    )

    container.resolve("result_dispatcher:slack")


def _default_client_builder(config: AppConfig) -> SlackSocketClient:
    if not config.slack_bot_token or not config.slack_app_token:
        raise ValueError("Slack configuration requires both bot token and app token")

    return SlackSocketClient(
        bot_token=config.slack_bot_token,
        app_token=config.slack_app_token,
        signing_secret=config.slack_signing_secret,
        default_channel=config.slack_default_channel,
    )


def _build_slack_dispatcher(
    container: DependencyContainer,
    config: AppConfig,
    *,
    debug: bool,
    log_output: TextIO | None,
) -> SlackResultDispatcher:
    dispatcher = SlackResultDispatcher(
        slack_client=container.resolve("slack:client"),
        response_formatter=DefaultSlackResponseFormatter(),
        default_channel=config.slack_default_channel,
        debug=debug,
        log_output=log_output or sys.stdout,
    )
    registry: ResultDispatcherRegistry | None = None
    try:
        registry = container.resolve("application:dispatcher_registry")
    except Exception:  # pragma: no cover - registry may not be registered (Phase 1 fallback)
        registry = None
    if registry is not None:
        registry.register("slack", dispatcher)
    return dispatcher


__all__ = ["register_slack_components", "SlackClientBuilder"]
