"""Test execution reporting interface.

Defines the contract for compiling test execution results into reports (e.g. HTML, JSON, JUnit).
Business logic omitted as per v0.1 milestone specification.
"""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Optional

from framework.logger import get_logger

logger = get_logger("Reporter")


class ReportFormat(Enum):
    """Supported export formats for test execution reports."""

    HTML = auto()
    JSON = auto()
    JUNIT_XML = auto()


@dataclass
class ReportSummary:
    """Summary metrics of test execution for report output."""

    total: int
    passed: int
    failed: int
    duration_seconds: float


class TestReporter:
    """Interface for generating test execution reports."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        """Initializes TestReporter interface.

        Args:
            output_dir: Optional output directory path for reports.
        """
        self.output_dir = output_dir
        logger.debug("TestReporter interface initialized.")

    def generate_report(
        self,
        execution_data: Dict[str, Any],
        fmt: ReportFormat = ReportFormat.HTML,
    ) -> Path:
        """Generates a formatted report file from execution data.

        Args:
            execution_data: Dictionary containing execution statistics and case outcomes.
            fmt: Target ReportFormat format.

        Returns:
            Path: Path to generated report file.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("Report generation logic is not implemented in v0.1.")
