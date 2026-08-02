"""General helper utilities for QualTest v2 framework."""

from datetime import datetime
from pathlib import Path


def generate_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """Generates a formatted timestamp string.

    Args:
        fmt: Datetime formatting string.

    Returns:
        str: Current formatted timestamp.
    """
    return datetime.now().strftime(fmt)


def ensure_directory(path: Path) -> Path:
    """Ensures a directory exists, creating parent directories if necessary.

    Args:
        path: Path to target directory.

    Returns:
        Path: Target directory path.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
