"""Reporter package for test execution report generation and performance metrics."""

from pathlib import Path
from typing import Any, Tuple

from framework.reporter.models import (
    ExecutionMetrics,
    ReportSummary,
    TestCaseReport,
)
from framework.reporter.report_generator import ReportGenerator
from framework.reporter.reporter import ReportFormat, TestReporter


def generate_reports(summary_source: Any) -> Tuple[Path, Path]:
    """Public API helper function to generate both HTML and CSV reports.

    Args:
        summary_source: SchedulerSummary or ExecutionSummary object.

    Returns:
        Tuple[Path, Path]: (html_report_path, csv_report_path) tuple.
    """
    generator = ReportGenerator()
    return generator.generate_all(summary_source)


__all__ = [
    "ReportGenerator",
    "TestReporter",
    "ReportFormat",
    "ReportSummary",
    "TestCaseReport",
    "ExecutionMetrics",
    "generate_reports",
]
