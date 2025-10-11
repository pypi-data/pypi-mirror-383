"""Logging helpers for Team Pal."""

from __future__ import annotations

import logging
from typing import Optional

from team_pal.config.loader import AppConfig

DEFAULT_LOGGER_NAME = "team_pal"
DEFAULT_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"


def configure_logging(config: Optional[AppConfig] = None, *, logger_name: str = DEFAULT_LOGGER_NAME) -> logging.Logger:
    """Configure and return the application logger.

    Parameters
    ----------
    config:
        Optional :class:`AppConfig` used to derive the log level.
    logger_name:
        Name of the logger to configure; defaults to ``team_pal``.
    """

    if config is None:
        level_name = AppConfig().log_level.upper()
    else:
        level_name = config.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        logger.addHandler(handler)

    logger.propagate = False
    return logger


__all__ = ["configure_logging", "DEFAULT_LOGGER_NAME", "DEFAULT_FORMAT"]
