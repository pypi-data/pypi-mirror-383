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

```bash
pip install team-pal
# or, if you prefer uv
uv pip install team-pal
```

Optionally, when working from source in editable mode:

```bash
uv pip install -e .
```

### Requirements

- Python 3.10+
- `uv` (recommended) for environment and dependency management
- Codex CLI (`npm install -g @openai/codex` or `brew install codex`)

See **docs/setup.md** for environment variable configuration (Slack tokens, CLI history path, etc.).

## CLI Usage (`pal` command)

The package exposes a console script named `pal`. After installation:

```bash
pal --config path/to/.env --prompt "> "
```

CLI commands (all prefixed with `$`):
- `$run <prompt>` — send a new instruction through Codex
- `$list` — show recent sessions
- `$status <session_id>` — inspect session state (`--json` for raw data)
- `$continue <session_id> <prompt>` — resume an existing session (Codex `thread_id` is tracked automatically)
- `$exit` / `$quit` / `$q` — stop the CLI loop

Add `--debug` to the `pal` command if you need the full JSON event log instead of the default concise summary (applies to Slack mode as well).

To run the Slack listener with the configured tokens, use:

```bash
pal --slack
```

### Slack Channel (Phase 1)

Ensure Slack app tokens are configured (`TEAM_PAL_SLACK_BOT_TOKEN`, etc.), then bootstrap via `bootstrap_phase1` (see `docs/setup.md` for a full walkthrough). Slack Socket Mode integration tests are marked with `@pytest.mark.integration` and skipped automatically when credentials are missing.

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

## Roadmap

The roadmap is tracked in `docs/roadmap.md` with detailed phase specs and plans. Future phases will extend observability, persistence, and multi-channel experiences beyond CLI & Slack.

For contributing guidelines and repository-wide instructions, refer to `AGENTS.md`.
