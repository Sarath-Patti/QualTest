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
    # Main API
    "load_testcase",
    "JSONLoader",
    # Data Models
    "TestCase",
    "TestStep",
    # Exceptions
    "TestCaseError",
    "MissingTestCaseError",
    "JSONParseError",
    "InvalidSchemaError",
    "InvalidProtocolError",
    "InvalidConfigurationError",
    # Legacy / Base interfaces
    "LogParser",
    "ConfigParser",
    "ParsedLogEntry",
]
