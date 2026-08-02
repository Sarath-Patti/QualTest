"""Scheduler package for concurrent test job queueing, execution, and lifecycle management."""

from pathlib import Path
from typing import Optional, Union

from framework.scheduler.concurrent_scheduler import ConcurrentScheduler
from framework.scheduler.models import (
    ExecutionResult,
    ExecutionTask,
    SchedulePriority,
    SchedulerSummary,
)
from framework.scheduler.scheduler import TestScheduler


def run_all_testcases(
    directory_path: Union[str, Path], max_workers: Optional[int] = None
) -> SchedulerSummary:
    """Public API helper function to discover and run all testcases in a directory concurrently.

    Args:
        directory_path: Directory path to scan for .json testcase files.
        max_workers: Maximum worker threads.

    Returns:
        SchedulerSummary: Execution summary results.
    """
    scheduler = TestScheduler(max_workers=max_workers)
    return scheduler.run_all(directory_path)


__all__ = [
    "TestScheduler",
    "ConcurrentScheduler",
    "ExecutionTask",
    "ExecutionResult",
    "SchedulerSummary",
    "SchedulePriority",
    "run_all_testcases",
]
