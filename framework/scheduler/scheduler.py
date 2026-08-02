"""Test job scheduling and queue management interface.

Provides task scheduling interfaces for prioritizing, queueing, and dispatching test execution jobs.
Business logic omitted as per v0.1 milestone specification.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from framework.logger import get_logger

logger = get_logger("Scheduler")


class SchedulePriority(Enum):
    """Priority levels for task scheduling."""

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class ScheduledTask:
    """Represents a scheduled test task within the execution queue."""

    task_id: str
    testcase_name: str
    priority: SchedulePriority = SchedulePriority.MEDIUM
    scheduled_time_iso: Optional[str] = None


class TestScheduler:
    """Interface for managing test job scheduling and queue operations."""

    def __init__(self) -> None:
        """Initializes the TestScheduler interface."""
        logger.debug("TestScheduler interface initialized.")

    def schedule_task(self, task: ScheduledTask) -> str:
        """Schedules a task for execution.

        Args:
            task: Task descriptor to be scheduled.

        Returns:
            str: Assigned task identifier.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("Task scheduling logic is not implemented in v0.1.")

    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Retrieves currently pending scheduled tasks.

        Returns:
            List[ScheduledTask]: List of queued tasks.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("Pending task query is not implemented in v0.1.")
