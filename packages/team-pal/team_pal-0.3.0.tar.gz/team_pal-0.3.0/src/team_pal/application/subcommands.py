"""Helpers for CLI subcommands."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import Any, Iterable

from team_pal.application.execution_service import InstructionExecutionService
from team_pal.application.session_manager import InstructionSessionManager
from team_pal.application.project_context import ProjectContextResolver
from team_pal.domain.execution import ExecutionResult
from team_pal.domain.instruction import Instruction
from team_pal.domain.session import InstructionSession, SessionHistoryEntry, SessionStatus
from team_pal.localization import format_message


@dataclass
class CommandResult:
    """Structured response returned by subcommand handlers."""

    message: str
    session: InstructionSession | None = None
    execution_result: ExecutionResult | None = None
    payload: dict[str, Any] | None = None


class CLIInstructionFactory:
    """Factory that builds CLI-originated instructions."""

    def __init__(self, *, channel: str = "cli") -> None:
        self._channel = channel

    def from_prompt(self, prompt: str) -> Instruction:
        return Instruction(
            instruction_id="",
            channel=self._channel,
            payload={"text": prompt.strip()},
            source_metadata={"source": "cli"},
        )


class TeamPalSubcommandService:
    """Application-level helper for handling CLI subcommands."""

    def __init__(
        self,
        *,
        instruction_factory: CLIInstructionFactory,
        execution_service: InstructionExecutionService,
        session_manager: InstructionSessionManager,
        project_resolver: ProjectContextResolver | None,
        language: str = "en",
    ) -> None:
        self._instruction_factory = instruction_factory
        self._execution_service = execution_service
        self._session_manager = session_manager
        self._project_resolver = project_resolver
        self._language = language

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------
    def run(self, prompt: str) -> CommandResult:
        selection_prompt = self._ensure_project_selected()
        if selection_prompt:
            return selection_prompt
        instruction = self._instruction_factory.from_prompt(prompt)
        session, result = self._execution_service.new_session(instruction)
        return CommandResult(
            message=f"Session {session.session_id} started",
            session=session,
            execution_result=result,
        )

    def continue_session(self, session_id: str, prompt: str) -> CommandResult:
        selection_prompt = self._ensure_project_selected()
        if selection_prompt:
            return selection_prompt
        session = self._require_session(session_id)
        instruction = self._instruction_factory.from_prompt(prompt)
        if instruction.channel != session.channel:
            instruction = replace(instruction, channel=session.channel)
        result = self._execution_service.execute(session_id, instruction)
        return CommandResult(
            message=f"Session {session_id} updated",
            session=session,
            execution_result=result,
        )

    def list_sessions(self, *, channel: str | None = None, as_json: bool = False) -> CommandResult:
        selection_prompt = self._ensure_project_selected()
        if selection_prompt:
            return selection_prompt
        sessions = self._session_manager.list_sessions(channel=channel)
        payload = {"sessions": [self._serialize_session(session) for session in sessions]}
        message = json.dumps(payload, indent=2) if as_json else self._format_session_table(sessions)
        return CommandResult(message=message, payload=payload)

    def session_status(self, session_id: str, *, as_json: bool = False) -> CommandResult:
        selection_prompt = self._ensure_project_selected()
        if selection_prompt:
            return selection_prompt
        session = self._require_session(session_id)
        payload = self._serialize_session(session)
        if as_json:
            message = json.dumps(payload, indent=2)
        else:
            message = self._format_session_detail(session)
        return CommandResult(message=message, session=session, payload=payload)

    def exit(self) -> CommandResult:
        return CommandResult(message="Exiting Team Pal CLI")

    def project_list(self) -> CommandResult:
        if self._project_resolver is None:
            return CommandResult(message=format_message("project.list.disabled", self._language))
        projects = self._project_resolver.list_projects()
        active_path = self._project_resolver.get_active_project()
        if not projects:
            message = format_message("project.list.empty", self._language)
        else:
            lines = []
            for name in projects:
                path = self._project_resolver.project_path_for(name)
                prefix = "*" if path == active_path else "-"
                display_name = self._format_project_display(name)
                lines.append(
                    format_message(
                        "project.list.item",
                        self._language,
                        prefix=prefix,
                        name=display_name,
                        path=path,
                    )
                )
            message = "\n".join(lines)
        return CommandResult(message=message, payload={"projects": projects, "active": str(active_path)})

    def project_select(self, project_name: str) -> CommandResult:
        if self._project_resolver is None:
            return CommandResult(message=format_message("project.select.disabled", self._language))
        project_path = self._project_resolver.select_project(project_name)
        return CommandResult(
            message=format_message("project.select.success", self._language, path=project_path),
            payload={"project": str(project_path)},
        )

    def complete_session(self, session_id: str, *, status: SessionStatus = SessionStatus.DISPATCHED) -> None:
        self._execution_service.complete(session_id, status)

    @property
    def project_resolver(self) -> ProjectContextResolver | None:
        return self._project_resolver

    @property
    def language(self) -> str:
        return self._language

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_project_selected(self) -> CommandResult | None:
        if self._project_resolver is None:
            return None
        if not self._project_resolver.is_selection_required():
            return None
        projects = self._project_resolver.list_projects()
        lines = [format_message("project.guard.header", self._language)]
        if projects:
            lines.append(format_message("project.guard.available_intro", self._language))
            for name in projects:
                display = self._format_project_display(name)
                lines.append(format_message("project.guard.available_item", self._language, name=display))
        else:
            lines.append(format_message("project.guard.none", self._language))
        lines.append(format_message("project.guard.hint", self._language))
        return CommandResult(message="\n".join(lines))

    def _format_project_display(self, name: str) -> str:
        if name == ".":
            return format_message("project.display.root", self._language)
        return name

    def _require_session(self, session_id: str) -> InstructionSession:
        session = self._session_manager.get_session(session_id)
        if session is None:
            raise KeyError(f"Session {session_id} not found")
        return session

    def _serialize_session(self, session: InstructionSession) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "channel": session.channel,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "history": [self._serialize_history(entry) for entry in session.history],
        }

    def _serialize_history(self, entry: SessionHistoryEntry) -> dict[str, Any]:
        return {
            "instruction": entry.instruction.payload,
            "status": entry.result.status.value,
            "output": entry.result.output,
            "timestamp": entry.timestamp.isoformat(),
        }

    def _format_session_table(self, sessions: Iterable[InstructionSession]) -> str:
        rows = [
            f"{session.session_id}\t{session.channel}\t{session.status.value}\t{session.updated_at.isoformat()}"
            for session in sessions
        ]
        header = "session_id\tchannel\tstatus\tupdated_at"
        return "\n".join([header, *rows]) if rows else "No sessions recorded."

    def _format_session_detail(self, session: InstructionSession) -> str:
        lines = [
            f"Session {session.session_id}",
            f"Channel: {session.channel}",
            f"Status: {session.status.value}",
            f"Updated: {session.updated_at.isoformat()}",
            "History:",
        ]
        if not session.history:
            lines.append("  (no entries)")
        else:
            for entry in session.history:
                lines.append(
                    f"  - {entry.timestamp.isoformat()} -> {entry.result.status.value}: {entry.result.output}"
                )
        return "\n".join(lines)


__all__ = ["TeamPalSubcommandService", "CommandResult", "CLIInstructionFactory"]
