"""Test outcome and modem response validation interface.

Defines rules and verification interfaces for validating wireless modem test output.
Business logic omitted as per v0.1 milestone specification.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from framework.logger import get_logger

logger = get_logger("Validator")


@dataclass(frozen=True)
class ValidationRule:
    """Defines a validation rule expectation."""

    field_name: str
    expected_value: Any
    tolerance: Optional[float] = None


@dataclass
class ValidationResult:
    """Outcome of a validation check."""

    is_valid: bool
    failures: List[str]
    metadata: Dict[str, Any]


class TestValidator:
    """Interface for evaluating modem responses against validation rules."""

    def __init__(self) -> None:
        """Initializes the TestValidator interface."""
        logger.debug("TestValidator interface initialized.")

    def validate(self, actual_data: Dict[str, Any], rules: List[ValidationRule]) -> ValidationResult:
        """Validates actual response data against expected validation rules.

        Args:
            actual_data: Dictionary of actual values returned by modem.
            rules: List of ValidationRule expectations.

        Returns:
            ValidationResult: Result of validation check.

        Raises:
            NotImplementedError: Business logic deferred to future milestone.
        """
        raise NotImplementedError("Validation logic is not implemented in v0.1.")
