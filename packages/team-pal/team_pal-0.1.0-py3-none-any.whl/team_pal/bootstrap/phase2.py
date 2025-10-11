"""Bootstrap utilities for Phase 2 (CLI channel)."""

from __future__ import annotations

import sys
from typing import Callable, TextIO

from team_pal.application.bootstrap import build_application_services
from team_pal.channel.cli.factory import register_cli_components
from team_pal.channel.slack.factory import register_slack_components
from team_pal.config.loader import AppConfig
from team_pal.container import DependencyContainer


def bootstrap_phase2(
    *,
    container: DependencyContainer,
    config: AppConfig,
    input_source=None,
    output_sink=None,
    prompt: str = "$ ",
    codex_runner_builder: Callable[[AppConfig], object] | None = None,
    debug: bool = False,
) -> None:
    """Configure services and channels for Phase 2."""

    build_application_services(
        container=container,
        config=config,
        codex_runner_builder=codex_runner_builder,
    )

    register_cli_components(
        container,
        input_source=input_source,
        output_sink=output_sink,
        prompt=prompt,
        debug=debug,
    )

    # Slack remains optional; only register if tokens are provided.
    if config.slack_bot_token and config.slack_app_token:
        register_slack_components(
            container,
            config,
            debug=debug,
            log_output=output_sink or sys.stdout,
        )


__all__ = ["bootstrap_phase2"]
