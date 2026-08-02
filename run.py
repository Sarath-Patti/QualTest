#!/usr/bin/env python3
"""QualTest v2 CLI Entry Point.

Wireless Modem Validation & Test Automation Framework.
Handles argument parsing, configuration validation, logger initialization,
and application startup sequence.
"""

import argparse
import sys
from typing import List, Optional

from framework.config import Settings, get_settings
from framework.logger import setup_logger, get_logger


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parses command-line arguments for QualTest v2 runner.

    Args:
        args: List of argument strings to parse. Defaults to sys.argv[1:].

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="qualtest",
        description="QualTest v2: Wireless Modem Validation & Test Automation Framework",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Display framework version and exit",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=None,
        help="Path to custom configuration file",
    )

    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Override application logging level",
    )

    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="Specify runtime environment (e.g., development, staging, production)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (equivalent to --log-level DEBUG)",
    )

    return parser.parse_args(args)


def validate_config(settings: Settings) -> bool:
    """Validates framework configuration directories and settings.

    Args:
        settings: Active immutable Settings instance.

    Returns:
        bool: True if configuration is valid.
    """
    # Ensure default directories exist
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.testcases_dir.mkdir(parents=True, exist_ok=True)
    return True


def main(args: Optional[List[str]] = None) -> int:
    """CLI execution entry point.

    Args:
        args: Optional list of command-line arguments.

    Returns:
        int: Exit status code (0 for success, non-zero for failure).
    """
    parsed = parse_args(args)

    # 1. Handle Version Request
    settings = get_settings()
    if parsed.version:
        print(f"{settings.app_name} v{settings.version}")
        return 0

    # 2. Determine Log Level
    log_level = parsed.log_level
    if parsed.verbose:
        log_level = "DEBUG"

    # 3. Setup Logging
    setup_logger(settings=settings, log_level=log_level)
    logger = get_logger("Runner")

    # 4. Validate Configuration
    if not validate_config(settings):
        logger.error("Configuration validation failed.")
        return 1

    # 5. Startup Sequence Display
    logger.info("==================================================")
    logger.info("  %s v%s Initialization", settings.app_name, settings.version)
    logger.info("==================================================")
    logger.info("Operating Environment : %s", settings.environment)
    logger.info("Project Base Path     : %s", settings.base_dir)
    logger.info("Logs Directory        : %s", settings.logs_dir)
    logger.info("Reports Directory     : %s", settings.reports_dir)
    logger.info("Testcases Directory   : %s", settings.testcases_dir)
    logger.info("Log Level             : %s", log_level or settings.log_level)
    logger.info("--------------------------------------------------")
    logger.info("Framework v0.1 Project Foundation initialized.")
    logger.info("Note: Test execution logic is not implemented in v0.1.")
    logger.info("Startup sequence completed successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
