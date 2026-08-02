"""Replay subsystem exceptions for QualTest framework."""


class ReplayError(Exception):
    """Base exception class for all protocol log replay failures."""


class ReplayParseError(ReplayError):
    """Raised when a protocol log file contains malformed or unparseable content."""


class InvalidStateTransitionError(ReplayError):
    """Raised when an invalid state transition occurs in the modem state machine."""


class ProtocolAnalysisError(ReplayError):
    """Raised when protocol analysis encounters a critical validation error."""
