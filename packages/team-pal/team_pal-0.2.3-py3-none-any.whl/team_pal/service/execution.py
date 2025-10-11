"""Instruction execution orchestration."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Protocol

from team_pal.config.loader import AppConfig
from team_pal.domain.execution import ExecutionError, ExecutionResult, ExecutionStatus
from team_pal.domain.instruction import Instruction
from team_pal.logging.factory import configure_logging
from team_pal.service.facade import ResultDispatcher


class AgentDispatcher(Protocol):
    """Protocol for agent adapters."""

    def dispatch(self, instruction: Instruction) -> ExecutionResult: ...


class InstructionExecutionService:
    """Coordinates execution between agent dispatchers and result dispatchers."""

    def __init__(
        self,
        *,
        agent_dispatcher: AgentDispatcher,
        result_dispatcher: ResultDispatcher,
        logger: logging.Logger | None = None,
    ) -> None:
        self._agent_dispatcher = agent_dispatcher
        self._result_dispatcher = result_dispatcher
        self._logger = logger or configure_logging(AppConfig(), logger_name="team_pal.execution")

    def execute(self, instruction: Instruction) -> ExecutionResult:
        self._logger.debug("Dispatching instruction %s via %s", instruction.instruction_id, instruction.channel)
        try:
            result = self._agent_dispatcher.dispatch(instruction)
            self._logger.debug(
                "Instruction %s completed with status %s", instruction.instruction_id, result.status.value
            )
            return result
        except Exception as exc:
            self._logger.exception("Agent dispatch failed for instruction %s", instruction.instruction_id)
            now = datetime.now(timezone.utc)
            return ExecutionResult(
                instruction=instruction,
                status=ExecutionStatus.FAILURE,
                output=None,
                error=ExecutionError(message=str(exc)),
                started_at=now,
                finished_at=now,
            )

    def handle_instruction(self, instruction: Instruction) -> None:
        result = self.execute(instruction)
        self._result_dispatcher.dispatch(instruction.instruction_id, result)


__all__ = ["InstructionExecutionService", "AgentDispatcher"]
