"""Module executed when running `python -m team_pal.cli`."""

from __future__ import annotations

import sys

from .cli_main import main


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
