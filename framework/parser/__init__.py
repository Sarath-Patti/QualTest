"""Parser package for testcase JSON definitions, log files, and configuration payloads."""

from framework.parser.exceptions import (
    InvalidConfigurationError,
    InvalidProtocolError,
    InvalidSchemaError,
    JSONParseError,
    MissingTestCaseError,
    TestCaseError,
)
from framework.parser.json_loader import JSONLoader, load_testcase
from framework.parser.models import TestCase, TestStep
from framework.parser.parser import ConfigParser, LogParser, ParsedLogEntry

__all__ = [
    "ConfigParser",
    "InvalidConfigurationError",
    "InvalidProtocolError",
    "InvalidSchemaError",
    "JSONLoader",
    "JSONParseError",
    # Legacy / Base interfaces
    "LogParser",
    "MissingTestCaseError",
    "ParsedLogEntry",
    # Data Models
    "TestCase",
    # Exceptions
    "TestCaseError",
    "TestStep",
    # Main API
    "load_testcase",
]
