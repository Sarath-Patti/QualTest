"""Scheduler data models for concurrent test execution.

Provides immutable dataclasses for task representation, execution results,
and aggregated scheduler summaries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

from framework.validator.models import ExecutionSummary, ValidationState


class SchedulePriority(Enum):
    """Priority levels for task scheduling."""

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass(frozen=True)
class ExecutionTask:
    """Represents an individual testcase task queued for execution.

    Attributes:
        testcase_path: Absolute path to the JSON testcase file.
        testcase_name: Name of the testcase.
        priority: Priority level of the task.
        created_time: ISO timestamp when the task was created.
    """

    testcase_path: Path
    testcase_name: str
    priority: SchedulePriority = SchedulePriority.MEDIUM
    created_time: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@dataclass(frozen=True)
class ExecutionResult:
    """Outcome of an individual testcase task execution by a worker.

    Attributes:
        testcase_name: Name of the executed testcase.
        execution_status: ValidationState outcome (PASS, FAIL, ERROR, TIMEOUT).
        execution_time_ms: Wall-clock execution time in milliseconds.
        worker_id: Identifier string of the worker thread.
        summary: Optional detailed ExecutionSummary from the validator.
        error_message: Optional error message if execution failed.
    """

    testcase_name: str
    execution_status: ValidationState
    execution_time_ms: float
    worker_id: str
    summary: ExecutionSummary | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class SchedulerSummary:
    """Aggregated summary of concurrent test scheduler execution.

    Attributes:
        total_testcases: Total number of testcase tasks discovered and submitted.
        completed: Count of testcases that completed with PASS status.
        failed: Count of testcases that failed, errored, or timed out.
        running: Count of testcases currently running (0 after completion).
        total_execution_time_ms: Overall wall-clock scheduler execution time in milliseconds.
        results: Tuple of individual ExecutionResult records.
    """

    total_testcases: int
    completed: int
    failed: int
    running: int
    total_execution_time_ms: float
    results: tuple[ExecutionResult, ...] = field(default_factory=tuple)
