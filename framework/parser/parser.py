"""Parser interfaces for log output and configuration files.

Defines structural interfaces for parsing test logs, AT command responses, and configuration payloads.
Business logic omitted as per v0.1 milestone specification.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

from framework.logger import get_logger

logger = get_logger("Parser")


@dataclass
class ParsedLogEntry:
    """Represents a structured entry parsed from log data."""

    timestamp: str
    log_level: str
    subsystem: str
    message: str


class LogParser:
    """Interface for parsing modem and execution log files."""

    def __init__(self) -> None:
        """Initializes LogParser interface."""
        logger.debug("LogParser interface initialized.")

    def parse_file(self, log_path: Path) -> List[ParsedLogEntry]:
        """Parses a log file into structured log entries.

        Args:
            log_path: Path to the log file.

        Returns:
            List[ParsedLogEntry]: List of parsed entries.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("Log parsing logic is not implemented in v0.1.")


class ConfigParser:
    """Interface for parsing configuration files."""

    def __init__(self) -> None:
        """Initializes ConfigParser interface."""
        logger.debug("ConfigParser interface initialized.")

    def parse(self, config_content: Union[str, Path]) -> Dict[str, Any]:
        """Parses configuration data into a dictionary structure.

        Args:
            config_content: Raw configuration string or file Path.

        Returns:
            Dict[str, Any]: Parsed configuration mapping.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("Config parsing logic is not implemented in v0.1.")
