"""Bootstrap utilities for Phase 1."""

from __future__ import annotations

from typing import Callable

from team_pal.agent.codex_cli import CodexExecRunner, CodexRunnerProtocol
from team_pal.application.bootstrap import build_application_services
from team_pal.channel.slack.factory import SlackClientBuilder, register_slack_components
from team_pal.config.loader import AppConfig
from team_pal.container import DependencyContainer


def bootstrap_phase1(
    *,
    container: DependencyContainer,
    config: AppConfig,
    slack_client_builder: SlackClientBuilder | None = None,
    codex_runner_builder: Callable[[AppConfig], CodexRunnerProtocol] | None = None,
) -> None:
    """Register Phase 1 providers in the dependency container."""

    build_application_services(
        container=container,
        config=config,
        codex_runner_builder=codex_runner_builder,
    )

    register_slack_components(
        container,
        config,
        slack_client_builder=slack_client_builder,
        debug=False,
        log_output=None,
    )


def _default_runner_builder(config: AppConfig) -> CodexRunnerProtocol:
    if not config.codex_cli_binary_path:
        raise ValueError("codex-cli binary path is not configured")

    return CodexExecRunner(
        binary_path=config.codex_cli_binary_path,
        timeout_seconds=config.codex_cli_timeout_seconds,
    )


__all__ = ["bootstrap_phase1"]
