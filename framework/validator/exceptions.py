"""Validation engine exception hierarchy for QualTest.

Provides specialized exceptions for validation failures, response mismatches,
timeouts, and execution errors.
"""


class ValidationError(Exception):
    """Base exception for all validation engine errors."""

    pass


class ResponseMismatchError(ValidationError):
    """Raised when actual response from target does not match expected response."""

    pass


class TimeoutError(ValidationError):
    """Raised when a step command execution or socket connection times out."""

    pass


class ExecutionError(ValidationError):
    """Raised when an underlying network or communication error occurs during validation."""

    pass
