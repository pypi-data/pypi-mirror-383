"""Global logger configuration for morchaos package."""

import logging
from typing import Optional

DEFAULT_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def init_logging(level: int = logging.INFO, fmt: str = DEFAULT_FMT) -> None:
    """Configure root logger once per process.

    Args:
        level: Logging level (default: INFO)
        fmt: Log message format string
    """
    logging.basicConfig(
        level=level, format=fmt, datefmt="%Y-%m-%d %H:%M:%S", force=True
    )


# Global logger instance
logger = logging.getLogger(__name__)
