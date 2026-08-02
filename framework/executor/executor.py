"""Test execution manager interface for QualTest v2.

Defines the contract for executing wireless modem validation test suites.
Business logic omitted as per v0.1 milestone specification.
"""

from dataclasses import dataclass, field
from typing import Any

from framework.logger import get_logger

logger = get_logger("Executor")


@dataclass(frozen=True)
class ExecutionConfig:
    """Configuration parameters for test execution."""

    suite_name: str
    parallel_jobs: int = 1
    timeout_seconds: int = 300
    stop_on_failure: bool = False
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Summary result of test suite execution."""

    suite_name: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    execution_time_seconds: float = 0.0
    details: list[dict[str, Any]] = field(default_factory=list)


class TestExecutor:
    """Interface for managing test case and suite execution.

    Responsible for orchestrating test execution flows across simulated
    or physical modem hardware targets.
    """

    def __init__(self, config: ExecutionConfig | None = None) -> None:
        """Initializes the TestExecutor interface.

        Args:
            config: Optional ExecutionConfig settings.
        """
        self.config = config
        logger.debug("TestExecutor interface initialized.")

    def run_suite(self, suite_path: str) -> ExecutionResult:
        """Executes a complete test suite.

        Args:
            suite_path: Path to the test suite definition.

        Returns:
            ExecutionResult: Summary result of suite execution.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError(
            "Test suite execution logic is not implemented in v0.1."
        )

    def run_testcase(self, testcase_id: str) -> bool:
        """Executes a single test case.

        Args:
            testcase_id: Identifier of the test case to execute.

        Returns:
            bool: True if execution succeeded.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError(
            "Test case execution logic is not implemented in v0.1."
        )
