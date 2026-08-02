"""Validation data models and state enumerations.

Provides immutable dataclass representations for step results, validation details,
and overall execution summaries within QualTest.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class ValidationState(Enum):
    """Supported validation outcome states."""

    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ValidationStep:
    """Represents the execution and validation outcome of an individual test step.

    Attributes:
        step_number: Sequential step index (1-based).
        command_sent: Command string sent to the target.
        expected_response: Expected response string defined in testcase.
        actual_response: Actual response string received from target.
        status: ValidationState outcome (PASS, FAIL, ERROR, TIMEOUT, UNKNOWN).
        latency_ms: Command execution latency in milliseconds.
    """

    step_number: int
    command_sent: str
    expected_response: str
    actual_response: str
    status: ValidationState
    latency_ms: float


@dataclass(frozen=True)
class ValidationResult:
    """Detailed result wrapper for a single step validation check.

    Attributes:
        step: Associated ValidationStep record.
        is_success: Boolean indicating if step passed.
        error_message: Optional error description if step failed.
    """

    step: ValidationStep
    is_success: bool
    error_message: Optional[str] = None


@dataclass(frozen=True)
class ExecutionSummary:
    """Summary metrics of testcase execution and validation.

    Attributes:
        testcase_name: Name of executed testcase.
        total_steps: Total number of steps executed.
        passed_steps: Count of steps that passed validation.
        failed_steps: Count of steps that failed validation.
        execution_time_ms: Total execution wall-clock time in milliseconds.
        final_status: Final overall ValidationState outcome.
        step_results: Tuple of ValidationStep records for all steps.
    """

    testcase_name: str
    total_steps: int
    passed_steps: int
    failed_steps: int
    execution_time_ms: float
    final_status: ValidationState
    step_results: Tuple[ValidationStep, ...] = field(default_factory=tuple)
