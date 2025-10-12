"""Command line entrypoint for Team Pal."""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from dataclasses import replace
from typing import Sequence, TextIO

try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

from team_pal.bootstrap.phase2 import bootstrap_phase2
from team_pal.config.loader import AppConfig, load_config
from team_pal.container import DependencyContainer
from team_pal.logging.factory import configure_logging
from team_pal.localization import detect_language, format_message, resolve_language


def _extract_cli_language(argv: Sequence[str] | None) -> str | None:
    if not argv:
        return None
    for index, token in enumerate(argv):
        if token == "--lang":
            if index + 1 < len(argv):
                return argv[index + 1]
            return None
        if token.startswith("--lang="):
            return token.split("=", 1)[1]
    return None


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    language = resolve_language(cli_language=_extract_cli_language(argv))
    parser = argparse.ArgumentParser(
        prog="pal",
        description=format_message("cli.help.description", language),
    )
    parser.add_argument("--config", help=format_message("cli.help.config", language))
    parser.add_argument("--channel", help=format_message("cli.help.channel", language))
    parser.add_argument("--prompt", default="> ", help=format_message("cli.help.prompt", language))
    parser.add_argument("--history-path", help=format_message("cli.help.history_path", language))
    parser.add_argument("--log-level", default=None, help=format_message("cli.help.log_level", language))
    parser.add_argument(
        "--debug",
        action="store_true",
        help=format_message("cli.help.debug", language),
    )
    parser.add_argument("--slack", action="store_true", help=format_message("cli.help.slack", language))
    parser.add_argument(
        "--slack-channel",
        help=format_message("cli.help.slack_channel", language),
    )
    parser.add_argument(
        "--multi-project",
        action="store_true",
        help=format_message("cli.help.multi_project", language),
    )
    parser.add_argument("--root-dir", help=format_message("cli.help.root_dir", language))
    parser.add_argument("--lang", help=format_message("cli.help.lang", language))
    parser.add_argument(
        "--python-mode",
        dest="python_mode",
        action="store_true",
        default=None,
        help=format_message("cli.help.python_mode", language),
    )
    parser.add_argument(
        "--no-python-mode",
        dest="python_mode",
        action="store_false",
        help=format_message("cli.help.no_python_mode", language),
    )
    return parser.parse_args(argv)


def _print_debug_config(config: AppConfig, output: TextIO) -> None:
    output.write(
        "[DEBUG] configuration summary:\n"
        f"  root_directory: {config.root_directory}\n"
        f"  multi_project_enabled: {config.multi_project_enabled}\n"
        f"  python_mode_enabled: {config.python_mode_enabled} (venv path: {config.virtualenv_path})\n"
        f"  default_input_channel: {config.default_input_channel}\n"
        f"  slack_bot_token_set: {bool(config.slack_bot_token)}\n"
        f"  slack_app_token_set: {bool(config.slack_app_token)}\n"
        f"  slack_allow_channel_messages: {config.slack_allow_channel_messages}\n"
        f"  slack_watched_channels: {config.slack_watched_channels or ''}\n"
        f"  log_level: {config.log_level}\n"
        f"  language: {config.language}\n"
    )
    output.flush()


def run_cli(
    argv: Sequence[str] | None = None,
    *,
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
) -> int:
    args = _parse_args(argv)

    if args.config and load_dotenv:
        load_dotenv(args.config, override=True)

    if getattr(args, "slack_channel", None) and not getattr(args, "slack", False):
        args.slack = True

    config = load_config()
    if args.slack:
        config = replace(config, default_input_channel="slack")
    elif args.channel:
        config = replace(config, default_input_channel=args.channel.strip().lower())
    if args.history_path:
        config = replace(config, cli_history_path=args.history_path)

    log_level_override = None
    if getattr(args, "log_level", None):
        log_level_override = args.log_level.strip().upper()
        config = replace(config, log_level=log_level_override)

    root_dir_arg = getattr(args, "root_dir", None)
    root_directory = root_dir_arg or config.root_directory or os.getcwd()
    root_directory = os.path.abspath(root_directory)

    multi_project = config.multi_project_enabled or getattr(args, "multi_project", False)

    python_mode = config.python_mode_enabled
    if getattr(args, "python_mode", None) is not None:
        python_mode = bool(args.python_mode)

    config = replace(
        config,
        root_directory=root_directory,
        multi_project_enabled=multi_project,
        python_mode_enabled=python_mode,
    )
    config = detect_language(config, cli_language=getattr(args, "lang", None))

    if getattr(args, "slack_channel", None):
        watched = [c.strip() for c in args.slack_channel.split(",") if c.strip()]
        watched_str = ",".join(watched) if watched else None
        config = replace(
            config,
            slack_allow_channel_messages=bool(watched),
            slack_watched_channels=watched_str,
            default_input_channel="slack",
        )

    debug_mode = getattr(args, "debug", False)
    if debug_mode:
        if log_level_override is None:
            config = replace(config, log_level="DEBUG")
        _print_debug_config(config, output_stream or sys.stdout)

    configure_logging(config)

    container = DependencyContainer()
    bootstrap_phase2(
        container=container,
        config=config,
        input_source=input_stream or sys.stdin,
        output_sink=output_stream or sys.stdout,
        prompt=args.prompt,
        debug=debug_mode,
    )

    if getattr(args, "slack", False):
        try:
            slack_listener = container.resolve("instruction_listener:slack")
        except Exception as exc:  # pragma: no cover - configuration issue
            (output_stream or sys.stdout).write(f"Slack listener unavailable: {exc}\n")
            if debug_mode:
                traceback.print_exc(file=output_stream or sys.stdout)
            return 1

        (output_stream or sys.stdout).write("Slack listener running. Press Ctrl+C to exit.\n")
        slack_listener.start()
        try:
            while True:
                thread = getattr(slack_listener, "_thread", None)
                if thread is None or not getattr(thread, "is_alive", lambda: False)():
                    break
                thread.join(timeout=0.5)
        except KeyboardInterrupt:
            (output_stream or sys.stdout).write("\nInterrupted. Shutting down Slack listener...\n")
        finally:
            slack_listener.stop()
        return 0

    listener = container.resolve("instruction_listener:cli")

    listener.start()
    try:
        # Wait until the listener thread finishes (typically on `$exit`).
        while True:
            thread = getattr(listener, "_thread", None)
            if thread is None or not thread.is_alive():
                break
            thread.join(timeout=0.1)
    except KeyboardInterrupt:
        (output_stream or sys.stdout).write("\nInterrupted. Shutting down...\n")
    finally:
        listener.stop()

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    return run_cli(argv)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
