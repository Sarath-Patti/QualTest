"""Test execution reporting interface.

Defines the contract for compiling test execution results into reports (e.g. HTML, CSV).
Delegates to ReportGenerator for concrete report generation.
"""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any

from framework.logger import get_logger
from framework.reporter.report_generator import ReportGenerator

logger = get_logger("Reporter")


class ReportFormat(Enum):
    """Supported export formats for test execution reports."""

    HTML = auto()
    CSV = auto()
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

    def __init__(self, output_dir: Path | None = None) -> None:
        """Initializes TestReporter interface.

        Args:
            output_dir: Optional output directory path for reports.
        """
        self.output_dir = output_dir
        self._generator = ReportGenerator()
        logger.debug("TestReporter interface initialized.")

    def generate_report(
        self,
        execution_data: Any,
        fmt: ReportFormat = ReportFormat.HTML,
    ) -> Path:
        """Generates a formatted report file from execution data.

        Args:
            execution_data: SchedulerSummary or ExecutionSummary object.
            fmt: Target ReportFormat format (HTML or CSV).

        Returns:
            Path: Path to generated report file.
        """
        if fmt == ReportFormat.CSV:
            _, csv_path = self._generator.generate_all(execution_data)
            return csv_path
        else:
            html_path, _ = self._generator.generate_all(execution_data)
            return html_path
