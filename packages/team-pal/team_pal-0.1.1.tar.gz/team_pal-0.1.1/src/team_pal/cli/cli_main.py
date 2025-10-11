"""Command line entrypoint for Team Pal."""

from __future__ import annotations

import argparse
import sys
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


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="pal", description="Team Pal CLI")
    parser.add_argument("--config", help="Path to .env file to load before starting.")
    parser.add_argument("--channel", help="Override default input channel (default: cli).")
    parser.add_argument("--prompt", default="> ", help="Prompt string shown in CLI mode.")
    parser.add_argument("--history-path", help="Override CLI history file location.")
    parser.add_argument("--log-level", default=None, help="Override logging level (e.g. DEBUG).")
    parser.add_argument("--debug", action="store_true", help="Enable verbose Codex event output (also prints Slack payloads).")
    parser.add_argument("--slack", action="store_true", help="Run Slack listener using configured tokens.")
    parser.add_argument("--slack-channel", help="When --slack is set, treat messages in these channel IDs (comma separated) as direct instructions.")
    return parser.parse_args(argv)


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

    if getattr(args, "slack_channel", None):
        watched = [c.strip() for c in args.slack_channel.split(",") if c.strip()]
        watched_str = ",".join(watched) if watched else None
        config = replace(
            config,
            slack_allow_channel_messages=bool(watched),
            slack_watched_channels=watched_str,
            default_input_channel="slack",
        )

    configure_logging(config)

    container = DependencyContainer()
    bootstrap_phase2(
        container=container,
        config=config,
        input_source=input_stream or sys.stdin,
        output_sink=output_stream or sys.stdout,
        prompt=args.prompt,
        debug=getattr(args, "debug", False),
    )

    if getattr(args, "slack", False):
        try:
            slack_listener = container.resolve("instruction_listener:slack")
        except Exception as exc:  # pragma: no cover - configuration issue
            (output_stream or sys.stdout).write(f"Slack listener unavailable: {exc}\n")
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
