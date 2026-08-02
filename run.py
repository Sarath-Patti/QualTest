#!/usr/bin/env python3
"""QualTest CLI Entry Point.

Wireless Modem Validation & Test Automation Framework.
Handles argument parsing, configuration validation, logger initialization,
JSON testcase loading, modem network simulation, and testcase execution validation.
"""

import argparse
import socket
import sys
import time
from typing import List, Optional

from framework.config import Settings, get_settings
from framework.logger import get_logger, setup_logger
from framework.parser import TestCaseError, load_testcase
from framework.simulator import NetworkSimulator
from framework.validator import ValidationState, validate


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parses command-line arguments for QualTest runner.

    Args:
        args: List of argument strings to parse. Defaults to sys.argv[1:].

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="qualtest",
        description="QualTest: Wireless Modem Validation & Test Automation Framework",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Display framework version and exit",
    )

    parser.add_argument(
        "-t",
        "--test",
        type=str,
        default=None,
        help="Path to JSON testcase file to load and validate schema",
    )

    parser.add_argument(
        "-r",
        "--run",
        type=str,
        default=None,
        help="Path to JSON testcase file to load, execute, and validate",
    )

    parser.add_argument(
        "-s",
        "--simulator",
        type=str,
        choices=["tcp", "udp"],
        default=None,
        help="Start modem network simulator for specified protocol (tcp or udp)",
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
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.testcases_dir.mkdir(parents=True, exist_ok=True)
    return True


def is_port_open(host: str, port: int, is_tcp: bool = True) -> bool:
    """Checks whether a target port is listening."""
    if not is_tcp:
        return True  # UDP is connectionless

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((host, port))
            return True
    except Exception:
        return False


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

    # 5. Handle Testcase Schema Check (--test option)
    if parsed.test:
        logger.info("QualTest v%s JSON Testcase Loader", settings.version)
        try:
            testcase = load_testcase(parsed.test)
        except TestCaseError as exc:
            logger.error("Failed to load testcase '%s': %s", parsed.test, str(exc))
            return 1

        logger.info("==================================================")
        logger.info("  TESTCASE SUMMARY")
        logger.info("==================================================")
        logger.info("Name         : %s", testcase.name)
        logger.info("Description  : %s", testcase.description)
        logger.info("Protocol     : %s", testcase.protocol)
        logger.info("Target       : %s:%d", testcase.host, testcase.port)
        logger.info("Timeout      : %.1f seconds", testcase.timeout)
        logger.info("Retry Limit  : %d", testcase.retry)
        logger.info("Total Steps  : %d", testcase.step_count)
        logger.info("--------------------------------------------------")
        for idx, step in enumerate(testcase.steps, start=1):
            logger.info(
                "Step #%d     : Send '%s' | Expect '%s' | Delay: %.2fs",
                idx,
                step.send,
                step.expect,
                step.delay,
            )
        logger.info("==================================================")
        logger.info("Testcase loaded and validated successfully.")
        return 0

    # 6. Handle Testcase Execution & Validation (--run option)
    if parsed.run:
        logger.info("QualTest v%s Test Execution Engine", settings.version)
        try:
            testcase = load_testcase(parsed.run)
        except TestCaseError as exc:
            logger.error("Failed to load testcase '%s': %s", parsed.run, str(exc))
            return 1

        # Auto-start local simulator if target host is loopback and not currently listening
        sim_instance: Optional[NetworkSimulator] = None
        is_tcp = testcase.protocol.upper() == "TCP"

        if testcase.host in ("127.0.0.1", "localhost") and not is_port_open(
            testcase.host, testcase.port, is_tcp=is_tcp
        ):
            logger.info(
                "Target %s:%d is not active. Auto-starting embedded %s simulator...",
                testcase.host,
                testcase.port,
                testcase.protocol,
            )
            sim_instance = NetworkSimulator(
                protocol=testcase.protocol,
                host=testcase.host,
                port=testcase.port,
                settings=settings,
            )
            sim_instance.start()
            time.sleep(0.2)

        try:
            summary = validate(testcase)
        finally:
            if sim_instance:
                sim_instance.stop()

        # Display Concise Execution Summary
        logger.info("==================================================")
        logger.info("  EXECUTION SUMMARY: %s", summary.testcase_name)
        logger.info("==================================================")
        logger.info("Final Status : %s", summary.final_status.value)
        logger.info("Total Steps  : %d", summary.total_steps)
        logger.info("Passed Steps : %d", summary.passed_steps)
        logger.info("Failed Steps : %d", summary.failed_steps)
        logger.info("Wall Time    : %.2f ms", summary.execution_time_ms)
        logger.info("--------------------------------------------------")
        for step_res in summary.step_results:
            logger.info(
                "Step #%d [%s] | Sent: '%s' | Expect: '%s' | Actual: '%s' | Latency: %.2fms",
                step_res.step_number,
                step_res.status.value,
                step_res.command_sent,
                step_res.expected_response,
                step_res.actual_response,
                step_res.latency_ms,
            )
        logger.info("==================================================")

        return 0 if summary.final_status == ValidationState.PASS else 1

    # 7. Handle Network Simulator (--simulator option)
    if parsed.simulator:
        proto = parsed.simulator.upper()
        sim = NetworkSimulator(protocol=proto, settings=settings)
        logger.info("==================================================")
        logger.info("  %s %s SIMULATOR STARTUP", settings.app_name, sim.protocol)
        logger.info("==================================================")
        logger.info("Listening Protocol  : %s", sim.protocol)
        logger.info("Target Binding      : %s:%d", sim.host, sim.port)
        logger.info("Simulated Delay     : %.1f ms", sim.response_delay_ms)
        logger.info("Press Ctrl+C to stop the simulator gracefully.")
        logger.info("--------------------------------------------------")

        sim.start()
        try:
            while sim.is_running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal (Ctrl+C). Initiating graceful shutdown...")
        finally:
            sim.stop()
            logger.info("Simulator shutdown complete.")
        return 0

    # 8. Default Startup Sequence Display
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
    logger.info("Framework initialized successfully.")
    logger.info("Use '--run <path>' to execute and validate a JSON testcase.")
    logger.info("Use '--test <path>' to load and validate a JSON testcase schema.")
    logger.info("Use '--simulator tcp|udp' to start the modem network simulator.")
    logger.info("Startup sequence completed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
