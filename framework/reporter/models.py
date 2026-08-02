"""Report data models and metrics structures.

Provides immutable dataclass representations for report summaries, individual testcase
reports, and overall execution metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class ReportSummary:
    """Summary metrics of test suite execution for report generation.

    Attributes:
        total_testcases: Total number of testcases executed.
        passed: Count of testcases that passed validation.
        failed: Count of testcases that failed, errored, or timed out.
        execution_time_ms: Total execution time in milliseconds.
        generated_at: ISO formatted timestamp when the report was generated.
    """

    total_testcases: int
    passed: int
    failed: int
    execution_time_ms: float
    generated_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@dataclass(frozen=True)
class TestCaseReport:
    """Individual testcase execution summary for report output.

    Attributes:
        testcase_name: Name of the testcase.
        status: Execution outcome status string (PASS, FAIL, ERROR, TIMEOUT).
        execution_time_ms: Testcase execution duration in milliseconds.
        average_latency_ms: Average command response latency in milliseconds.
        failure_reason: Explanation of failure or 'None'.
    """

    testcase_name: str
    status: str
    execution_time_ms: float
    average_latency_ms: float
    failure_reason: str = "None"


@dataclass(frozen=True)
class ExecutionMetrics:
    """Calculated execution performance metrics.

    Attributes:
        pass_rate: Percentage of testcases that passed (0.0 - 100.0).
        average_latency_ms: Mean response latency across all steps.
        maximum_latency_ms: Peak response latency recorded across all steps.
        minimum_latency_ms: Lowest response latency recorded across all steps.
        total_execution_time_ms: Total wall-clock execution duration in milliseconds.
    """

    pass_rate: float
    average_latency_ms: float
    maximum_latency_ms: float
    minimum_latency_ms: float
    total_execution_time_ms: float
