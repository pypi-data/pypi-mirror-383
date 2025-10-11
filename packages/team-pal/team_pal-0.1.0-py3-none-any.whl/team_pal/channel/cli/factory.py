"""Dependency registration helpers for the CLI channel."""

from __future__ import annotations

import sys
from typing import TextIO

from team_pal.application.execution_service import ResultDispatcherRegistry
from team_pal.application.subcommands import TeamPalSubcommandService
from team_pal.channel.cli.dispatcher import CLIResultDispatcher, CLIResultPresenter
from team_pal.channel.cli.listener import CLIInstructionListener
from team_pal.container import DependencyContainer


def register_cli_components(
    container: DependencyContainer,
    *,
    input_source: TextIO | None = None,
    output_sink: TextIO | None = None,
    prompt: str = "$ ",
    debug: bool = False,
) -> None:
    """Register CLI-specific dependencies."""

    input_source = input_source or sys.stdin
    output_sink = output_sink or sys.stdout

    container.register_factory(
        "cli:presenter",
        lambda _c: CLIResultPresenter(debug=debug),
        scope="singleton",
    )

    container.register_factory(
        "result_dispatcher:cli",
        lambda c: _build_cli_dispatcher(c, output_sink),
        scope="singleton",
    )

    container.register_factory(
        "instruction_listener:cli",
        lambda c: CLIInstructionListener(
            subcommand_service=c.resolve("cli:subcommand_service"),
            input_source=input_source,
            output_sink=output_sink,
            prompt=prompt,
        ),
        scope="singleton",
    )

    # Ensure dispatcher is instantiated so it is registered with the registry.
    container.resolve("result_dispatcher:cli")


def _build_cli_dispatcher(container: DependencyContainer, output_sink: TextIO) -> CLIResultDispatcher:
    presenter: CLIResultPresenter = container.resolve("cli:presenter")
    dispatcher = CLIResultDispatcher(presenter=presenter, output=output_sink)
    registry: ResultDispatcherRegistry = container.resolve("application:dispatcher_registry")
    registry.register("cli", dispatcher)
    return dispatcher


__all__ = ["register_cli_components"]
