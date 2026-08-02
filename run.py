#!/usr/bin/env python3
"""QualTest CLI Entry Point.

Wireless Modem Validation & Test Automation Framework.
Handles argument parsing, configuration validation, logger initialization,
JSON testcase loading, modem network simulation, failure injection, testcase execution validation,
concurrent testcase scheduling, and HTML/CSV report generation.
"""

import argparse
import socket
import sys
import time
from pathlib import Path

from framework.config import Settings, get_settings
from framework.logger import get_logger, setup_logger
from framework.parser import TestCaseError, load_testcase
from framework.reporter import generate_reports
from framework.scheduler import run_all_testcases
from framework.simulator import FailureInjector, NetworkSimulator
from framework.validator import ValidationState, validate

DEFAULT_TCP_PORT: int = 8080
DEFAULT_UDP_PORT: int = 8081
SLEEP_SIMULATOR_START: float = 0.2
SLEEP_SIMULATOR_LOOP: float = 0.5


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
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
        help="Path to single JSON testcase file to execute and validate",
    )

    parser.add_argument(
        "--run-all",
        type=str,
        default=None,
        help="Directory path containing JSON testcases to execute concurrently",
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML and CSV execution reports upon completion",
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
        "--failure-config",
        type=str,
        default=None,
        help="Path to failure injection JSON configuration file",
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
        return True

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((host, port))
            return True
    except Exception:
        return False


def _handle_test_option(parsed: argparse.Namespace, settings: Settings) -> int:
    """Handles JSON testcase schema check (--test option)."""
    logger = get_logger("Runner")
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


def _handle_run_option(parsed: argparse.Namespace, settings: Settings) -> int:
    """Handles single testcase execution & validation (--run option)."""
    logger = get_logger("Runner")
    logger.info("QualTest v%s Test Execution Engine", settings.version)
    try:
        testcase = load_testcase(parsed.run)
    except TestCaseError as exc:
        logger.error("Failed to load testcase '%s': %s", parsed.run, str(exc))
        return 1

    sim_instance: NetworkSimulator | None = None
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
        time.sleep(SLEEP_SIMULATOR_START)

    try:
        summary = validate(testcase)
    finally:
        if sim_instance:
            sim_instance.stop()

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

    if parsed.report:
        html_path, csv_path = generate_reports(summary)
        print(f"[+] HTML Report : {html_path}")
        print(f"[+] CSV Report  : {csv_path}")

    return 0 if summary.final_status == ValidationState.PASS else 1


def _handle_run_all_option(parsed: argparse.Namespace, settings: Settings) -> int:
    """Handles concurrent batch execution (--run-all option)."""
    logger = get_logger("Runner")
    logger.info("QualTest v%s Concurrent Test Scheduler", settings.version)
    target_dir = Path(parsed.run_all).resolve()

    tcp_sim: NetworkSimulator | None = None
    udp_sim: NetworkSimulator | None = None

    if not is_port_open("127.0.0.1", DEFAULT_TCP_PORT, is_tcp=True):
        tcp_sim = NetworkSimulator(
            protocol="TCP", port=DEFAULT_TCP_PORT, settings=settings
        )
        tcp_sim.start()

    if not is_port_open("127.0.0.1", DEFAULT_UDP_PORT, is_tcp=False):
        udp_sim = NetworkSimulator(
            protocol="UDP", port=DEFAULT_UDP_PORT, settings=settings
        )
        udp_sim.start()

    time.sleep(SLEEP_SIMULATOR_START)

    try:
        sched_summary = run_all_testcases(target_dir)
    finally:
        if tcp_sim:
            tcp_sim.stop()
        if udp_sim:
            udp_sim.stop()

    logger.info("==================================================")
    logger.info("  CONCURRENT SCHEDULER SUMMARY")
    logger.info("==================================================")
    logger.info("Total Testcases : %d", sched_summary.total_testcases)
    logger.info("Completed (PASS): %d", sched_summary.completed)
    logger.info("Failed/Errors   : %d", sched_summary.failed)
    logger.info("Total Wall Time : %.2f ms", sched_summary.total_execution_time_ms)
    logger.info("--------------------------------------------------")
    for res in sched_summary.results:
        logger.info(
            "Task '%s' [%s] | Worker: %s | Execution Time: %.2fms %s",
            res.testcase_name,
            res.execution_status.value,
            res.worker_id,
            res.execution_time_ms,
            f"({res.error_message})" if res.error_message else "",
        )
    logger.info("==================================================")

    if parsed.report:
        html_path, csv_path = generate_reports(sched_summary)
        print(f"[+] HTML Report : {html_path}")
        print(f"[+] CSV Report  : {csv_path}")

    return 0 if sched_summary.failed == 0 else 1


def _handle_simulator_option(parsed: argparse.Namespace, settings: Settings) -> int:
    """Handles network simulator execution (--simulator option)."""
    logger = get_logger("Runner")
    proto = parsed.simulator.upper()
    failure_injector: FailureInjector | None = None

    if parsed.failure_config:
        try:
            failure_injector = FailureInjector.from_file(parsed.failure_config)
        except Exception as exc:
            logger.error(
                "Failed to load failure config '%s': %s", parsed.failure_config, exc
            )
            return 1

    sim = NetworkSimulator(
        protocol=proto,
        failure_injector=failure_injector,
        settings=settings,
    )
    logger.info("==================================================")
    logger.info("  %s %s SIMULATOR STARTUP", settings.app_name, sim.protocol)
    logger.info("==================================================")
    logger.info("Listening Protocol  : %s", sim.protocol)
    logger.info("Target Binding      : %s:%d", sim.host, sim.port)
    logger.info("Simulated Delay     : %.1f ms", sim.response_delay_ms)
    logger.info(
        "Failure Injection   : %s",
        "ENABLED" if failure_injector and failure_injector.enabled else "DISABLED",
    )
    logger.info("Press Ctrl+C to stop the simulator gracefully.")
    logger.info("--------------------------------------------------")

    sim.start()
    try:
        while sim.is_running:
            time.sleep(SLEEP_SIMULATOR_LOOP)
    except KeyboardInterrupt:
        logger.info(
            "Received interrupt signal (Ctrl+C). Initiating graceful shutdown..."
        )
    finally:
        sim.stop()
        logger.info("Simulator shutdown complete.")
    return 0


def _handle_default_startup(settings: Settings, log_level: str | None) -> int:
    """Handles default framework startup info display."""
    logger = get_logger("Runner")
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
    logger.info(
        "Use '--run-all <dir> [--report]' to execute testcases in parallel with reports."
    )
    logger.info(
        "Use '--run <path> [--report]' to execute and validate a single testcase."
    )
    logger.info("Use '--test <path>' to load and validate a JSON testcase schema.")
    logger.info("Use '--simulator tcp|udp' to start the modem network simulator.")
    logger.info("Startup sequence completed.")
    return 0


def main(args: list[str] | None = None) -> int:
    """CLI execution entry point.

    Args:
        args: Optional list of command-line arguments.

    Returns:
        int: Exit status code (0 for success, non-zero for failure).
    """
    parsed = parse_args(args)

    settings = get_settings()
    if parsed.version:
        print(f"{settings.app_name} v{settings.version}")
        return 0

    log_level = "DEBUG" if parsed.verbose else parsed.log_level
    setup_logger(settings=settings, log_level=log_level)
    logger = get_logger("Runner")

    if not validate_config(settings):
        logger.error("Configuration validation failed.")
        return 1

    if parsed.test:
        ret = _handle_test_option(parsed, settings)
    elif parsed.run:
        ret = _handle_run_option(parsed, settings)
    elif parsed.run_all:
        ret = _handle_run_all_option(parsed, settings)
    elif parsed.simulator:
        ret = _handle_simulator_option(parsed, settings)
    else:
        ret = _handle_default_startup(settings, log_level)

    return ret


if __name__ == "__main__":
    sys.exit(main())
