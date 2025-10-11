# Team Pal CLI Orchestrator

Team Pal is an orchestration layer that receives instructions from multiple channels (Slack, terminal CLI, etc.), dispatches them to execution agents such as **codex exec**, and returns results with consistent observability. The project uses a phase-based roadmap: Phase 1 delivered Slack connectivity, Phase 2 adds a first-class CLI channel with JSON streaming support for Codex.

## Project Structure

```
src/team_pal/         # Application source (agents, services, channel adapters)
tests/                # pytest suites (phase0/phase1/phase2)
docs/                 # Specifications, plans, concept and roadmap documents
docs/setup.md         # Environment setup and CLI bootstrap guide
docs/roadmap.md       # Phase milestones
docs/phase?_spec.md   # Phase-specific requirements/design
docs/phase?_plan.md   # Phase-specific implementation checklists
docs/codex_streaming_analysis_plan.md # Analysis for Codex JSON streaming
AGENTS.md             # Repository-wide guidelines and phase pointers
```

Key highlights:
- `src/team_pal/agent/codex_cli.py`: `CodexExecRunner` integrates with `codex exec --json`.
- `src/team_pal/channel/cli/`: CLI listener & result presenter with streaming output.
- `src/team_pal/application/`: Session manager, execution service, subcommand handling.
- `tests/fixtures/codex_stream/`: Real `codex exec --json` logs (success / failure / resume) used in tests.

## Installation

### From PyPI

```bash
pip install team-pal
# or with uv
uv pip install team-pal
# alternatively, install as a standalone tool
uv tool install team-pal
```

### From source

Team Pal is developed with [uv](https://github.com/astral-sh/uv). After cloning the repository:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

### Requirements

- Python 3.12+ (packaging metadata permits >=3.10, but the project is validated on 3.12)
- `uv` (recommended) for environment and dependency management
- Codex CLI (`npm install -g @openai/codex` or `brew install codex`)
- Slack app tokens if you plan to run the Slack listener (`TEAM_PAL_SLACK_*`)

See **docs/setup.md** for environment variable configuration (Slack tokens, CLI history path, etc.).

## CLI Usage (`pal` command)

The package exposes a console script named `pal`. After installation:

```bash
pal --config path/to/.env --prompt "> "
```

Optional flags:

```bash
# enable multi-project mode with the current directory as root
pal --multi-project

# specify a custom root directory and disable python virtualenv activation
pal --multi-project --root-dir ~/workspace --no-python-mode
```

CLI commands (all prefixed with `$`; short aliases in parentheses):
- `$new_session <prompt>` (`$new`) — start a brand-new instruction session
- `$list` (`$ls`) — show recent sessions
- `$status <session_id>` (`$st`) — inspect session state (`--json` for raw data)
- `$continue <session_id> <prompt>` (`$cs`) — resume an existing session (Codex `thread_id` is tracked automatically)
- `$project_list` (`$pl`) — show available projects when multi-project mode is on
- `$project_select <name>` (`$ps`) — select the active project to run commands against
- `$exit` / `$quit` / `$q` — stop the CLI loop

Add `--debug` to the `pal` command if you need the full JSON event log instead of the default concise summary (applies to Slack mode as well).

To run the Slack listener with the configured tokens, use:

```bash
pal --slack
# limit to specific public channels using channel IDs
pal --slack --slack-channel C01234567,C08976543
```

### Slack Channel (Phase 1)

Ensure Slack app tokens are configured (`TEAM_PAL_SLACK_BOT_TOKEN`, etc.), then bootstrap via `bootstrap_phase1` (see `docs/setup.md` for a full walkthrough). Slack Socket Mode integration tests are marked with `@pytest.mark.integration` and skipped automatically when credentials are missing.

When running in channel mode, set:

```bash
TEAM_PAL_SLACK_ALLOW_CHANNEL_MESSAGES=true
TEAM_PAL_SLACK_WATCHED_CHANNELS=C01234567,C08976543
```

Slack messages that begin with CLI-style commands (e.g., `$list`/`$ls`, `$status <id>`/`$st`, `$project_list`/`$pl`) are intercepted by the Slack listener and answered directly (no Codex round-trip), so you can inspect sessions and manage projects from Slack as well.

## Testing

The project follows a TDD workflow; every function/class has accompanying pytest cases. Run all tests:

```bash
pytest
# or per phase
pytest tests/phase1
pytest tests/phase2
```

Integration tests requiring network access (Slack) are tagged, and helper scripts exist:

```bash
./scripts/run_unit_tests.sh
./scripts/run_integration_tests.sh
```

See `tests/test_list.md` for an up-to-date checklist of implemented tests.

## Codex Streaming Notes

`codex exec --json` produces JSONL events. For session continuation:

1. Capture the `thread_id` from the previous `thread.started` event.
2. Resume with `codex exec --json resume <THREAD_ID> "<follow-up prompt>"`. (`--last` cannot be combined with `--json`.)

The fixtures under `tests/fixtures/codex_stream/` contain real output for success, failure, and resume scenarios. Tests assert parser robustness and CLI presentation using these logs.

By default, `CodexExecRunner` runs Codex with full automation:

```
codex --ask-for-approval never exec --json --sandbox danger-full-access
```

Override the runner’s `extra_args` (via DI) or adjust `TEAM_PAL_CLI_BINARY_PATH` if you need a hardened policy.

## Roadmap

The roadmap is tracked in `docs/roadmap.md` with detailed phase specs and plans. Future phases will extend observability, persistence, and multi-channel experiences beyond CLI & Slack.

For contributing guidelines and repository-wide instructions, refer to `AGENTS.md`.
