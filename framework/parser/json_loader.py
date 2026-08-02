"""JSON Testcase loader and schema validator for QualTest framework.

Handles loading testcase configurations from JSON files, verifying file existence,
validating JSON syntax, enforcing strict schema rules, and instantiating TestCase objects.
"""

import json
from pathlib import Path
from typing import Any

from framework.logger import get_logger
from framework.parser.exceptions import (
    InvalidConfigurationError,
    InvalidProtocolError,
    InvalidSchemaError,
    JSONParseError,
    MissingTestCaseError,
)
from framework.parser.models import TestCase, TestStep

logger = get_logger("Parser.JSONLoader")

SUPPORTED_PROTOCOLS: set[str] = {"TCP", "UDP"}
REQUIRED_TOP_LEVEL_FIELDS: set[str] = {
    "name",
    "description",
    "protocol",
    "host",
    "port",
    "timeout",
    "retry",
    "steps",
}
MIN_PORT: int = 1
MAX_PORT: int = 65535


class JSONLoader:
    """Loads and validates JSON testcases from the filesystem."""

    def load(self, file_path: str | Path) -> TestCase:
        """Loads a JSON testcase file, validates its schema, and returns a TestCase model.

        Args:
            file_path: Path to the JSON testcase file.

        Returns:
            TestCase: Validated testcase object.

        Raises:
            MissingTestCaseError: If the file does not exist or is unreadable.
            JSONParseError: If the file contains malformed JSON syntax.
            InvalidProtocolError: If the specified protocol is unsupported.
            InvalidConfigurationError: If configuration values (port, timeout, retry) are out of bounds.
            InvalidSchemaError: If required fields are missing or steps are malformed.
        """
        path = Path(file_path).resolve()
        logger.info("Loading testcase from file: %s", path)

        # 1. Validate File Existence
        if not path.exists() or not path.is_file():
            msg = f"Testcase file not found or is not a file: {path}"
            logger.error("Validation failure: %s", msg)
            raise MissingTestCaseError(msg)

        # 2. Read and Parse JSON Syntax
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            msg = f"Invalid JSON syntax in testcase file {path}: {exc.msg} (line {exc.lineno}, col {exc.colno})"
            logger.error("Validation failure: %s", msg)
            raise JSONParseError(msg) from exc
        except Exception as exc:
            msg = f"Failed to read testcase file {path}: {exc!s}"
            logger.error("Validation failure: %s", msg)
            raise MissingTestCaseError(msg) from exc

        # 3. Schema Validation
        logger.info("Performing schema validation for testcase at: %s", path)
        testcase = self.validate_schema(data, source_path=path)

        logger.info(
            "Validation success: Testcase '%s' (%s) validated successfully.",
            testcase.name,
            testcase.protocol,
        )
        return testcase

    def _validate_top_level(self, data: Any) -> dict[str, Any]:
        """Validates that root element is a dict containing required top-level fields."""
        if not isinstance(data, dict):
            msg = f"Root of testcase JSON must be an object/dict, got {type(data).__name__}"
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        missing_fields = REQUIRED_TOP_LEVEL_FIELDS - set(data.keys())
        if missing_fields:
            msg = (
                f"Missing required fields in testcase schema: {sorted(missing_fields)}"
            )
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        return data

    def _validate_metadata(self, data: dict[str, Any]) -> tuple[str, str, str]:
        """Validates name, description, and protocol metadata fields."""
        name = data["name"]
        description = data["description"]
        protocol = str(data["protocol"]).upper()

        if not isinstance(name, str) or not name.strip():
            msg = "Field 'name' must be a non-empty string."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        if not isinstance(description, str):
            msg = "Field 'description' must be a string."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        if protocol not in SUPPORTED_PROTOCOLS:
            msg = f"Unsupported protocol '{protocol}'. Supported protocols: {sorted(SUPPORTED_PROTOCOLS)}"
            logger.error("Validation failure: %s", msg)
            raise InvalidProtocolError(msg)

        return name, description, protocol

    def _validate_network_config(
        self, data: dict[str, Any]
    ) -> tuple[str, int, float, int]:
        """Validates host, port, timeout, and retry network parameters."""
        host = data["host"]
        port = data["port"]
        timeout = data["timeout"]
        retry = data["retry"]

        if not isinstance(host, str) or not host.strip():
            msg = "Field 'host' must be a non-empty string."
            logger.error("Validation failure: %s", msg)
            raise InvalidConfigurationError(msg)

        if not isinstance(port, int) or isinstance(port, bool):
            msg = f"Field 'port' must be an integer, got {type(port).__name__}"
            logger.error("Validation failure: %s", msg)
            raise InvalidConfigurationError(msg)
        if not (MIN_PORT <= port <= MAX_PORT):
            msg = f"Port number {port} is out of valid range ({MIN_PORT} - {MAX_PORT})."
            logger.error("Validation failure: %s", msg)
            raise InvalidConfigurationError(msg)

        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool):
            msg = (
                f"Field 'timeout' must be a numeric value, got {type(timeout).__name__}"
            )
            logger.error("Validation failure: %s", msg)
            raise InvalidConfigurationError(msg)
        if timeout <= 0:
            msg = f"Timeout value {timeout} must be greater than 0."
            logger.error("Validation failure: %s", msg)
            raise InvalidConfigurationError(msg)

        if not isinstance(retry, int) or isinstance(retry, bool):
            msg = f"Field 'retry' must be an integer, got {type(retry).__name__}"
            logger.error("Validation failure: %s", msg)
            raise InvalidConfigurationError(msg)
        if retry < 0:
            msg = f"Retry count {retry} must be greater than or equal to 0."
            logger.error("Validation failure: %s", msg)
            raise InvalidConfigurationError(msg)

        return host, port, float(timeout), retry

    def _validate_step_entry(self, step_data: Any, idx: int) -> TestStep:
        """Validates an individual test step entry."""
        if not isinstance(step_data, dict):
            msg = f"Step #{idx} must be a dictionary object."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        if "send" not in step_data or "expect" not in step_data:
            msg = f"Step #{idx} missing required 'send' or 'expect' fields."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        send_val = step_data["send"]
        expect_val = step_data["expect"]
        delay_val = step_data.get("delay", 0.0)

        if not isinstance(send_val, str):
            msg = f"Step #{idx} 'send' must be a string."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        if not isinstance(expect_val, str):
            msg = f"Step #{idx} 'expect' must be a string."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        if not isinstance(delay_val, (int, float)) or isinstance(delay_val, bool):
            msg = f"Step #{idx} 'delay' must be a numeric value."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        if delay_val < 0:
            msg = f"Step #{idx} 'delay' cannot be negative."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        return TestStep(
            send=send_val,
            expect=expect_val,
            delay=float(delay_val),
        )

    def _validate_steps(self, raw_steps: Any) -> tuple[TestStep, ...]:
        """Validates the list of step dictionaries."""
        if not isinstance(raw_steps, list) or len(raw_steps) == 0:
            msg = "Field 'steps' must be a non-empty list."
            logger.error("Validation failure: %s", msg)
            raise InvalidSchemaError(msg)

        steps: list[TestStep] = []
        for idx, step_data in enumerate(raw_steps, start=1):
            steps.append(self._validate_step_entry(step_data, idx))

        return tuple(steps)

    def validate_schema(self, data: Any, source_path: Path) -> TestCase:
        """Validates raw dictionary structure against QualTest schema requirements.

        Args:
            data: Loaded raw JSON data.
            source_path: File path reference for error reporting.

        Returns:
            TestCase: Constructed TestCase instance.
        """
        valid_data = self._validate_top_level(data)
        name, description, protocol = self._validate_metadata(valid_data)
        host, port, timeout, retry = self._validate_network_config(valid_data)
        steps = self._validate_steps(valid_data["steps"])

        return TestCase(
            name=name,
            description=description,
            protocol=protocol,
            host=host,
            port=port,
            timeout=timeout,
            retry=retry,
            steps=steps,
        )


def load_testcase(file_path: str | Path) -> TestCase:
    """Public API function to load and validate a JSON testcase file.

    Args:
        file_path: Path to target JSON testcase file.

    Returns:
        TestCase: Validated testcase model.
    """
    loader = JSONLoader()
    return loader.load(file_path)
