"""Concurrent Test Scheduler implementation for QualTest framework.

Manages multithreaded testcase execution using ThreadPoolExecutor, task queueing,
thread-safe result aggregation, worker error isolation, and graceful lifecycle management.
"""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import threading
import time
from typing import Dict, List, Optional, Tuple, Union

from framework.config import Settings, get_settings
from framework.logger import get_logger
from framework.parser import TestCaseError, load_testcase
from framework.scheduler.models import (
    ExecutionResult,
    ExecutionTask,
    SchedulePriority,
    SchedulerSummary,
)
from framework.validator import ValidationState, validate

logger = get_logger("Scheduler.Concurrent")


class ConcurrentScheduler:
    """Thread-safe concurrent test scheduler utilizing ThreadPoolExecutor."""

    def __init__(
        self,
        max_workers: Optional[int] = None,
        queue_capacity: int = 100,
        scheduler_timeout: float = 300.0,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initializes ConcurrentScheduler.

        Args:
            max_workers: Maximum worker threads. Defaults to min(32, os.cpu_count() + 4).
            queue_capacity: Maximum task queue capacity.
            scheduler_timeout: Global timeout for waiting for task completions.
            settings: Optional Settings instance.
        """
        cfg = settings or get_settings()
        default_workers = min(32, (os.cpu_count() or 4) + 4)
        self.max_workers = max_workers or int(
            os.getenv("QUALTEST_MAX_WORKERS", str(default_workers))
        )
        self.queue_capacity = queue_capacity
        self.scheduler_timeout = scheduler_timeout

        self._executor: Optional[ThreadPoolExecutor] = None
        self._futures: List[Future[ExecutionResult]] = []
        self._tasks: List[ExecutionTask] = []
        self._results: List[ExecutionResult] = []
        self._lock: threading.Lock = threading.Lock()
        self._is_started: bool = False
        self._start_time: float = 0.0

        logger.info("Scheduler initialized with max_workers=%d, queue_capacity=%d", self.max_workers, self.queue_capacity)

    @property
    def is_running(self) -> bool:
        """Indicates if the scheduler thread pool is active."""
        return self._is_started

    def start(self) -> None:
        """Starts the ThreadPoolExecutor worker pool."""
        with self._lock:
            if self._is_started:
                logger.warning("Concurrent scheduler is already running.")
                return

            self._executor = ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix="QualTestWorker",
            )
            self._is_started = True
            self._start_time = time.perf_counter()
            logger.info("Scheduler started with %d worker threads.", self.max_workers)

    def discover_testcases(
        self, directory_path: Union[str, Path]
    ) -> List[Path]:
        """Discovers JSON testcases within a specified directory.

        Args:
            directory_path: Directory path to scan for .json files.

        Returns:
            List[Path]: Sorted list of discovered testcase file paths.
        """
        target_dir = Path(directory_path).resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            logger.error("Testcase directory does not exist or is not a directory: %s", target_dir)
            return []

        json_files = sorted(list(target_dir.glob("*.json")))
        logger.info("Discovered %d testcases in '%s'.", len(json_files), target_dir)
        return json_files

    def submit_task(
        self,
        testcase_path: Union[str, Path],
        priority: SchedulePriority = SchedulePriority.MEDIUM,
    ) -> ExecutionTask:
        """Submits a testcase task to the scheduler for execution.

        Args:
            testcase_path: Path to the JSON testcase file.
            priority: Priority level of task.

        Returns:
            ExecutionTask: Created task object.
        """

        if not self._is_started:
            self.start()

        path = Path(testcase_path).resolve()
        name = path.stem

        task = ExecutionTask(
            testcase_path=path,
            testcase_name=name,
            priority=priority,
        )

        with self._lock:
            self._tasks.append(task)
            future = self._executor.submit(self._worker_entrypoint, task)
            self._futures.append(future)

        logger.info("Testcase submitted: '%s' (%s)", task.testcase_name, task.testcase_path)
        return task

    def _worker_entrypoint(self, task: ExecutionTask) -> ExecutionResult:
        """Worker thread entry point executing an individual testcase task."""
        worker_id = threading.current_thread().name
        logger.info("Worker %s started processing testcase '%s'", worker_id, task.testcase_name)
        logger.info("Testcase execution started: '%s' on %s", task.testcase_name, worker_id)

        start_time = time.perf_counter()
        try:
            testcase = load_testcase(task.testcase_path)
            exec_summary = validate(testcase)
            end_time = time.perf_counter()
            exec_ms = (end_time - start_time) * 1000.0

            result = ExecutionResult(
                testcase_name=task.testcase_name,
                execution_status=exec_summary.final_status,
                execution_time_ms=exec_ms,
                worker_id=worker_id,
                summary=exec_summary,
            )

            logger.info(
                "Testcase completed: '%s' -> %s in %.2fms",
                task.testcase_name,
                exec_summary.final_status.value,
                exec_ms,
            )

        except TestCaseError as exc:
            end_time = time.perf_counter()
            exec_ms = (end_time - start_time) * 1000.0
            result = ExecutionResult(
                testcase_name=task.testcase_name,
                execution_status=ValidationState.ERROR,
                execution_time_ms=exec_ms,
                worker_id=worker_id,
                error_message=f"Parser Error: {str(exc)}",
            )
            logger.error("Testcase execution failed for '%s' (Parser Error): %s", task.testcase_name, exc)

        except Exception as exc:
            end_time = time.perf_counter()
            exec_ms = (end_time - start_time) * 1000.0
            result = ExecutionResult(
                testcase_name=task.testcase_name,
                execution_status=ValidationState.ERROR,
                execution_time_ms=exec_ms,
                worker_id=worker_id,
                error_message=f"Worker Error: {str(exc)}",
            )
            logger.error("Unexpected worker error executing '%s': %s", task.testcase_name, exc)

        logger.info("Worker %s finished task '%s'", worker_id, task.testcase_name)

        with self._lock:
            self._results.append(result)

        return result

    def wait_for_completion(
        self, timeout: Optional[float] = None
    ) -> SchedulerSummary:
        """Waits for all submitted testcase tasks to complete.

        Args:
            timeout: Optional wait timeout override. Defaults to scheduler_timeout.

        Returns:
            SchedulerSummary: Summary of all executed testcases.
        """
        wait_timeout = timeout or self.scheduler_timeout
        futures_copy: List[Future[ExecutionResult]] = []

        with self._lock:
            futures_copy = list(self._futures)

        for future in as_completed(futures_copy, timeout=wait_timeout):
            try:
                future.result()
            except Exception as exc:
                logger.error("Exception waiting for task completion: %s", exc)

        total_end_time = time.perf_counter()
        total_wall_time_ms = (total_end_time - self._start_time) * 1000.0

        with self._lock:
            results_tuple = tuple(self._results)
            total = len(self._tasks)
            passed = sum(1 for r in results_tuple if r.execution_status == ValidationState.PASS)
            failed = total - passed

        summary = SchedulerSummary(
            total_testcases=total,
            completed=passed,
            failed=failed,
            running=0,
            total_execution_time_ms=total_wall_time_ms,
            results=results_tuple,
        )

        logger.info(
            "Summary generated: %d total, %d passed, %d failed in %.2fms",
            summary.total_testcases,
            summary.completed,
            summary.failed,
            summary.total_execution_time_ms,
        )
        return summary

    def cancel_pending_tasks(self) -> int:
        """Cancels all pending, unstarted tasks.

        Returns:
            int: Number of tasks successfully cancelled.
        """
        cancelled_count = 0
        with self._lock:
            for future in self._futures:
                if future.cancel():
                    cancelled_count += 1
        logger.info("Cancelled %d pending tasks.", cancelled_count)
        return cancelled_count

    def shutdown(self, graceful: bool = True) -> None:
        """Shuts down the worker thread pool.

        Args:
            graceful: If True, waits for active tasks to finish before shutting down.
        """
        with self._lock:
            if not self._is_started:
                return
            self._is_started = False

        if not graceful:
            self.cancel_pending_tasks()

        if self._executor:
            self._executor.shutdown(wait=graceful)
            self._executor = None

        logger.info("Scheduler shutdown complete.")
