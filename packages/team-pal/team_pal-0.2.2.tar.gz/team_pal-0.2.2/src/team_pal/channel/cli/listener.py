"""CLI instruction listener implementation."""

from __future__ import annotations

import threading
from typing import TextIO

from team_pal.application.subcommands import CommandResult, TeamPalSubcommandService
from team_pal.service.facade import InstructionListener


class CLIInstructionListener(InstructionListener):
    """Listens for CLI input and dispatches subcommands."""

    def __init__(
        self,
        *,
        subcommand_service: TeamPalSubcommandService,
        input_source: TextIO,
        output_sink: TextIO,
        prompt: str = "> ",
    ) -> None:
        self._service = subcommand_service
        self._input = input_source
        self._output = output_sink
        self._prompt = prompt
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._active_session_id: str | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="CLIInstructionListener", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    # ------------------------------------------------------------------
    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self._output.write(self._prompt)
            self._output.flush()
            line = self._input.readline()
            if not line:
                break
            command = line.strip()
            if not command:
                continue
            try:
                result = self._handle_command(command)
                if result:
                    self._output.write(result.message + "\n")
                    self._output.flush()
                    if command.startswith("$exit"):
                        break
            except Exception as exc:  # pragma: no cover - defensive path
                self._output.write(f"Error: {exc}\n")
                self._output.flush()

    def _handle_command(self, command: str) -> CommandResult | None:
        if not command.startswith("$"):
            result = self._handle_default_input(command)
            self._update_active_session(result)
            return result

        parts = command.split()
        verb = parts[0]
        if verb in {"$new_session", "$new"}:
            prompt = " ".join(parts[1:])
            result = self._service.run(prompt)
            self._update_active_session(result)
            return result
        if verb in {"$continue", "$cs"} and len(parts) >= 3:
            session_id = parts[1]
            prompt = " ".join(parts[2:])
            result = self._service.continue_session(session_id, prompt)
            self._active_session_id = session_id
            self._update_active_session(result)
            return result
        if verb in {"$status", "$st"} and len(parts) >= 2:
            session_id = parts[1]
            as_json = "--json" in parts[2:]
            result = self._service.session_status(session_id, as_json=as_json)
            self._active_session_id = session_id
            self._update_active_session(result)
            return result
        if verb in {"$list", "$ls"}:
            channel = None
            as_json = False
            args = parts[1:]
            idx = 0
            while idx < len(args):
                token = args[idx]
                if token == "--json":
                    as_json = True
                elif token == "--channel" and idx + 1 < len(args):
                    channel = args[idx + 1]
                    idx += 1
                idx += 1
            result = self._service.list_sessions(channel=channel, as_json=as_json)
            self._update_active_session(result)
            return result
        if verb in {"$exit", "$quit", "$q"}:
            self._stop_event.set()
            result = self._service.exit()
            self._update_active_session(result)
            return result
        if verb in {"$project_list", "$pl"}:
            result = self._service.project_list()
            self._update_active_session(result)
            return result
        if verb in {"$project_select", "$ps"} and len(parts) >= 2:
            project_name = parts[1]
            result = self._service.project_select(project_name)
            self._update_active_session(result)
            return result

        # Unrecognized command -> treat as freeform instruction
        result = self._service.run(" ".join(parts))
        self._update_active_session(result)
        return result

    def _handle_default_input(self, prompt: str) -> CommandResult:
        if self._active_session_id:
            try:
                return self._service.continue_session(self._active_session_id, prompt)
            except KeyError:
                self._active_session_id = None
        return self._service.run(prompt)

    def _update_active_session(self, result: CommandResult | None) -> None:
        if result and result.session:
            self._active_session_id = result.session.session_id


__all__ = ["CLIInstructionListener"]
