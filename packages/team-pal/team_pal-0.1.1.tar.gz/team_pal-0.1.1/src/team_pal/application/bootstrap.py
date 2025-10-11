"""Utilities to bootstrap application layer services."""

from __future__ import annotations

from typing import Callable

from team_pal.agent.codex_cli import CodexCliAgentAdapter, CodexExecRunner, CodexRunnerProtocol
from team_pal.agent.codex_cli_session import CodexAgentSessionFactory, CodexProcessController
from team_pal.application.agent_session import AgentSessionFactory
from team_pal.application.execution_service import InstructionExecutionService, ResultDispatcherRegistry
from team_pal.application.session_manager import InstructionSessionManager, SessionManagerConfig
from team_pal.application.subcommands import CLIInstructionFactory, TeamPalSubcommandService
from team_pal.config.loader import AppConfig
from team_pal.container import DependencyContainer
from team_pal.repository.session import InMemoryInstructionSessionRepository, InstructionSessionRepository


def build_application_services(
    *,
    container: DependencyContainer,
    config: AppConfig,
    session_repository: InstructionSessionRepository | None = None,
    codex_runner_builder: Callable[[AppConfig], CodexRunnerProtocol] | None = None,
) -> None:
    """Initialise core application services used across channels."""

    repository = session_repository or InMemoryInstructionSessionRepository()
    container.register_instance("session:repository", repository)

    session_manager = InstructionSessionManager(
        repository,
        config=SessionManagerConfig(default_channel=config.default_input_channel),
    )
    container.register_instance("session:manager", session_manager)

    runner_builder = codex_runner_builder or _default_runner_builder
    codex_runner = runner_builder(config)
    codex_adapter = CodexCliAgentAdapter(codex_runner)
    process_controller = CodexProcessController(codex_adapter)
    agent_session_factory: AgentSessionFactory = CodexAgentSessionFactory(process_controller)
    container.register_instance("agent:session_factory", agent_session_factory)

    dispatcher_registry = ResultDispatcherRegistry(
        default_channel=config.default_input_channel,
        dispatchers={}
    )
    container.register_instance("application:dispatcher_registry", dispatcher_registry)

    execution_service = InstructionExecutionService(
        session_manager=session_manager,
        agent_session_factory=agent_session_factory,
        dispatcher_registry=dispatcher_registry,
    )
    container.register_instance("service:instruction_execution", execution_service)

    subcommand_service = TeamPalSubcommandService(
        instruction_factory=CLIInstructionFactory(channel=config.default_input_channel),
        execution_service=execution_service,
        session_manager=session_manager,
    )
    container.register_instance("cli:subcommand_service", subcommand_service)


def _default_runner_builder(config: AppConfig) -> CodexRunnerProtocol:
    if not config.codex_cli_binary_path:
        raise ValueError("codex-cli binary path is not configured")

    return CodexExecRunner(
        binary_path=config.codex_cli_binary_path,
        timeout_seconds=config.codex_cli_timeout_seconds,
    )


__all__ = ["build_application_services"]
