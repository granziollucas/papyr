"""Logging helpers."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_file_logger(log_path: Path) -> logging.Logger:
    """Configure a DEBUG file logger for a run.

    Args:
        log_path: Path to the log file.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("papyr")
    logger.setLevel(logging.DEBUG)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        logger.addHandler(handler)
    return logger
