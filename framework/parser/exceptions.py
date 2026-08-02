"""Exception hierarchy for QualTest parser and testcase loading.

Provides specialized framework exceptions for missing files, JSON syntax errors,
and schema or protocol validation failures.
"""


class TestCaseError(Exception):
    """Base exception for all testcase loading and parsing errors."""

    pass


class MissingTestCaseError(TestCaseError):
    """Raised when a specified testcase file does not exist or cannot be opened."""

    pass


class JSONParseError(TestCaseError):
    """Raised when a testcase file contains invalid JSON syntax."""

    pass


class InvalidSchemaError(TestCaseError):
    """Base exception raised when a testcase fails schema validation."""

    pass


class InvalidProtocolError(InvalidSchemaError):
    """Raised when a testcase specifies an unsupported network protocol."""

    pass


class InvalidConfigurationError(InvalidSchemaError):
    """Raised when testcase configuration fields (e.g. port, timeout, retry) contain invalid values."""

    pass
