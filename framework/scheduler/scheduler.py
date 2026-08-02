"""Test job scheduling and queue management interface.

Provides task scheduling interfaces for prioritizing, queueing, and dispatching test execution jobs.
Delegates to ConcurrentScheduler for multithreaded test execution.
"""

from pathlib import Path
from typing import List, Optional, Union

from framework.logger import get_logger
from framework.scheduler.concurrent_scheduler import ConcurrentScheduler
from framework.scheduler.models import (
    ExecutionResult,
    ExecutionTask,
    SchedulePriority,
    SchedulerSummary,
)

logger = get_logger("Scheduler")


class TestScheduler:
    """Interface for managing test job scheduling and queue operations."""

    def __init__(self, max_workers: Optional[int] = None) -> None:
        """Initializes the TestScheduler interface.

        Args:
            max_workers: Maximum worker threads.
        """
        self._scheduler = ConcurrentScheduler(max_workers=max_workers)
        logger.debug("TestScheduler interface initialized.")

    def schedule_task(
        self,
        testcase_path: Union[str, Path],
        priority: SchedulePriority = SchedulePriority.MEDIUM,
    ) -> ExecutionTask:
        """Schedules a testcase task for execution.

        Args:
            testcase_path: Path to target testcase file.
            priority: Priority level.

        Returns:
            ExecutionTask: Created task object.
        """
        return self._scheduler.submit_task(testcase_path, priority=priority)

    def run_all(self, directory_path: Union[str, Path]) -> SchedulerSummary:
        """Discovers and runs all testcases within a directory concurrently.

        Args:
            directory_path: Target directory path containing JSON testcases.

        Returns:
            SchedulerSummary: Summary of execution results.
        """
        testcase_paths = self._scheduler.discover_testcases(directory_path)
        if not testcase_paths:
            logger.warning("No testcases found to execute in %s", directory_path)
            return SchedulerSummary(
                total_testcases=0,
                completed=0,
                failed=0,
                running=0,
                total_execution_time_ms=0.0,
            )

        self._scheduler.start()
        for path in testcase_paths:
            self._scheduler.submit_task(path)

        summary = self._scheduler.wait_for_completion()
        self._scheduler.shutdown(graceful=True)
        return summary
