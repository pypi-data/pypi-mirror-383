"""Application service responsible for orchestrating instruction execution."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Dict

from team_pal.application.agent_session import AgentSession, AgentSessionFactory, AgentSessionError
from team_pal.application.session_manager import InstructionSessionManager
from team_pal.domain.execution import ExecutionResult, ExecutionStatus
from team_pal.domain.instruction import Instruction
from team_pal.domain.session import InstructionSession, SessionStatus
from team_pal.service.facade import ResultDispatcher


@dataclass
class ResultDispatcherRegistry:
    """Registry that resolves result dispatchers by channel."""

    default_channel: str
    dispatchers: Dict[str, ResultDispatcher]

    def get(self, channel: str | None) -> ResultDispatcher | None:
        if channel and channel in self.dispatchers:
            return self.dispatchers[channel]
        return self.dispatchers.get(self.default_channel)

    def register(self, channel: str, dispatcher: ResultDispatcher) -> None:
        self.dispatchers[channel] = dispatcher


class InstructionExecutionService:
    """High level orchestration for instruction sessions."""

    def __init__(
        self,
        *,
        session_manager: InstructionSessionManager,
        agent_session_factory: AgentSessionFactory,
        dispatcher_registry: ResultDispatcherRegistry,
        logger: logging.Logger | None = None,
    ) -> None:
        self._session_manager = session_manager
        self._agent_factory = agent_session_factory
        self._dispatcher_registry = dispatcher_registry
        self._agent_sessions: Dict[str, AgentSession] = {}
        self._lock = threading.Lock()
        self._logger = logger or logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Session lifecycle operations
    # ------------------------------------------------------------------
    def new_session(self, instruction: Instruction) -> tuple[InstructionSession, ExecutionResult]:
        self._logger.debug("Starting new session for instruction %s", instruction.instruction_id)
        agent_session = self._agent_factory.create(channel=instruction.channel or "cli", instruction=instruction)
        session = self._session_manager.create_session(instruction, agent_session_id=agent_session.get_id())
        with self._lock:
            self._agent_sessions[session.session_id] = agent_session

        result = self._send_to_agent(session.session_id, instruction)
        self._session_manager.append_history(session.session_id, instruction, result)
        self._session_manager.update_status(
            session.session_id,
            SessionStatus.ACTIVE if result.status is ExecutionStatus.SUCCESS else SessionStatus.FAILED,
        )
        self._dispatch(session, instruction, result)
        return session, result

    def execute(self, session_id: str, instruction: Instruction) -> ExecutionResult:
        self._logger.debug("Continuing session %s with instruction %s", session_id, instruction.instruction_id)
        result = self._send_to_agent(session_id, instruction)
        session = self._session_manager.get_session(session_id)
        if session is None:
            raise KeyError(session_id)
        self._session_manager.append_history(session_id, instruction, result)
        if result.status is ExecutionStatus.SUCCESS:
            self._session_manager.update_status(session_id, SessionStatus.ACTIVE)
        else:
            self._session_manager.update_status(session_id, SessionStatus.FAILED)
        self._dispatch(session, instruction, result)
        return result

    def complete(self, session_id: str, status: SessionStatus = SessionStatus.DISPATCHED) -> None:
        self._session_manager.complete(session_id, status)
        with self._lock:
            agent_session = self._agent_sessions.pop(session_id, None)
        if agent_session:
            agent_session.close()

    def abort(self, session_id: str, *, reason: str | None = None) -> None:
        self._session_manager.abort(session_id, reason=reason)
        with self._lock:
            agent_session = self._agent_sessions.pop(session_id, None)
        if agent_session:
            agent_session.close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _send_to_agent(self, session_id: str, instruction: Instruction) -> ExecutionResult:
        with self._lock:
            agent_session = self._agent_sessions.get(session_id)
        if agent_session is None:
            session = self._session_manager.get_session(session_id)
            if session is None or session.agent_session_id is None:
                raise AgentSessionError(f"Session {session_id} is not associated with an agent session")
            agent_session = self._agent_factory.create(channel=session.channel, instruction=instruction)
            with self._lock:
                self._agent_sessions[session_id] = agent_session
            self._session_manager.assign_agent_session(session_id, agent_session.get_id())
        self._logger.debug("Sending prompt to agent session %s: %s", session_id, instruction.payload)
        result = agent_session.send(instruction)
        self._logger.debug(
            "Session %s produced status %s", session_id, result.status.value
        )
        return result

    def _dispatch(self, session: InstructionSession, instruction: Instruction, result: ExecutionResult) -> None:
        dispatcher = self._dispatcher_registry.get(instruction.channel or session.channel)
        if dispatcher:
            self._logger.debug(
                "Dispatching result for session %s via dispatcher %s", session.session_id, dispatcher.__class__.__name__
            )
            dispatcher.dispatch(session.session_id, result)


__all__ = ["InstructionExecutionService", "ResultDispatcherRegistry"]
