"""Logging bootstrap for unity3d-mcp."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_level: str | None = None) -> None:
    """Configure stderr, rotating file, and optional JSON format for Loki."""
    level_name = (log_level or os.getenv("UNITY3D_MCP_LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(level)
    stderr.setFormatter(fmt)
    root.addHandler(stderr)

    log_dir = Path(__file__).resolve().parents[3] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "unity3d-mcp.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    if os.getenv("UNITY3D_MCP_LOG_FORMAT", "").strip().lower() == "json":
        from unity3d_mcp.utils.structured_logging import configure_json_logging

        configure_json_logging(root)

    logging.getLogger(__name__).info(
        "Logging initialized level=%s json=%s file=%s",
        level_name,
        os.getenv("UNITY3D_MCP_LOG_FORMAT", "").strip().lower() == "json",
        log_dir / "unity3d-mcp.log",
    )
