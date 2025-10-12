"""Message catalog for localization."""

from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
    "cli.help.description": {
        "en": "Team Pal CLI orchestrates Codex sessions and multi-channel inputs.",
        "ja": "Team Pal CLI は Codex セッションと複数チャネル入力を仲介します。",
    },
    "cli.help.config": {
        "en": "Path to a .env file to load before starting.",
        "ja": "起動前に読み込む .env ファイルのパス。",
    },
    "cli.help.channel": {
        "en": "Override the default input channel (default: cli).",
        "ja": "既定の入力チャネルを上書きします（デフォルト: cli）。",
    },
    "cli.help.prompt": {
        "en": "Prompt string shown in CLI mode.",
        "ja": "CLI モードで表示するプロンプト文字列。",
    },
    "cli.help.history_path": {
        "en": "Override CLI history file location.",
        "ja": "CLI 履歴ファイルの保存先を上書きします。",
    },
    "cli.help.log_level": {
        "en": "Override logging level (e.g. DEBUG).",
        "ja": "ログレベルを上書きします（例: DEBUG）。",
    },
    "cli.help.debug": {
        "en": "Enable verbose Codex event output (also prints Slack payloads).",
        "ja": "Codex イベントを詳細表示します（Slack ペイロードも出力）。",
    },
    "cli.help.slack": {
        "en": "Run Slack listener using configured tokens.",
        "ja": "設定済みトークンで Slack リスナーを起動します。",
    },
    "cli.help.slack_channel": {
        "en": "When --slack is set, treat messages in these channel IDs (comma separated) as direct instructions.",
        "ja": "Slack モード時に、指定したチャネル ID（カンマ区切り）の投稿を指示として扱います。",
    },
    "cli.help.multi_project": {
        "en": "Enable multi-project mode (scan the root directory for projects).",
        "ja": "マルチプロジェクトモードを有効化します（ルートディレクトリを走査）。",
    },
    "cli.help.root_dir": {
        "en": "Root directory containing project subdirectories (defaults to current working directory).",
        "ja": "プロジェクトを含むルートディレクトリ（未指定時はカレントディレクトリ）。",
    },
    "cli.help.lang": {
        "en": "Interface language override (ja or en).",
        "ja": "インターフェース言語を指定します（ja / en）。",
    },
    "cli.help.python_mode": {
        "en": "Enable Python virtualenv activation before running agents (default).",
        "ja": "エージェント実行前に Python 仮想環境を自動アクティベートします（デフォルト）。",
    },
    "cli.help.no_python_mode": {
        "en": "Disable Python virtualenv activation.",
        "ja": "Python 仮想環境の自動アクティベーションを無効化します。",
    },
    "project.guard.header": {
        "en": "No project selected. Select a project before running commands.",
        "ja": "プロジェクトが選択されていません。コマンドを実行する前にプロジェクトを選択してください。",
    },
    "project.guard.available_intro": {
        "en": "Available projects:",
        "ja": "利用可能なプロジェクト:",
    },
    "project.guard.available_item": {
        "en": "  - {name}",
        "ja": "  - {name}",
    },
    "project.guard.none": {
        "en": "No projects discovered under the configured root directory.",
        "ja": "設定されたルートディレクトリにプロジェクトが見つかりません。",
    },
    "project.guard.hint": {
        "en": "Use `$ps <project_name>` to select a project or `$pl` to view details.",
        "ja": "`$ps <project_name>` でプロジェクトを選択、`$pl` で一覧を表示できます。",
    },
    "project.list.disabled": {
        "en": "Multi-project mode is disabled.",
        "ja": "マルチプロジェクトモードは無効です。",
    },
    "project.list.empty": {
        "en": "No projects discovered under the root directory.",
        "ja": "ルートディレクトリにプロジェクトが見つかりません。",
    },
    "project.list.item": {
        "en": "{prefix} {name} -> {path}",
        "ja": "{prefix} {name} -> {path}",
    },
    "project.select.success": {
        "en": "Active project set to {path}",
        "ja": "アクティブプロジェクトを {path} に設定しました。",
    },
    "project.select.disabled": {
        "en": "Multi-project mode is disabled.",
        "ja": "マルチプロジェクトモードは無効です。",
    },
    "project.display.root": {
        "en": ". (root)",
        "ja": ". (root)",
    },
}


__all__ = ["MESSAGES"]
