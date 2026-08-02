"""Validation engine implementation for QualTest framework.

Executes testcase steps against target modem servers, measures command latencies,
compares actual against expected responses, and produces structured ExecutionSummary results.
"""

import time

from framework.logger import get_logger
from framework.parser import TestCase, TestStep
from framework.validator.models import (
    ExecutionSummary,
    ValidationState,
    ValidationStep,
)
from network.tcp.client import TCPClient, TCPClientConfig
from network.udp.client import UDPClient, UDPClientConfig

logger = get_logger("Validator.Engine")

MS_PER_SEC: float = 1000.0


class ValidationEngine:
    """Core engine for executing and validating testcases against modem targets."""

    def _create_client(
        self, testcase: TestCase
    ) -> tuple[TCPClient | None, UDPClient | None]:
        """Instantiates TCP or UDP network client for test execution."""
        is_tcp = testcase.protocol.upper() == "TCP"
        if is_tcp:
            tcp_client = TCPClient(
                TCPClientConfig(
                    host=testcase.host,
                    port=testcase.port,
                    timeout_seconds=testcase.timeout,
                )
            )
            tcp_client.connect()
            return tcp_client, None

        udp_client = UDPClient(
            UDPClientConfig(
                host=testcase.host,
                port=testcase.port,
                timeout_seconds=testcase.timeout,
            )
        )
        return None, udp_client

    def _execute_single_step(
        self,
        idx: int,
        step: TestStep,
        is_tcp: bool,
        tcp_client: TCPClient | None,
        udp_client: UDPClient | None,
    ) -> ValidationStep:
        """Executes an individual test step and records performance and state metrics."""
        if step.delay > 0:
            time.sleep(step.delay)

        send_time = time.perf_counter()
        actual_resp = ""
        status = ValidationState.UNKNOWN

        try:
            if is_tcp and tcp_client:
                actual_resp = tcp_client.send_command(step.send)
            elif udp_client:
                actual_resp = udp_client.send_command(step.send)

            recv_time = time.perf_counter()
            latency_ms = (recv_time - send_time) * MS_PER_SEC

            logger.info(
                "Received response: '%s' (Latency: %.2fms)",
                actual_resp,
                latency_ms,
            )

            if actual_resp == step.expect:
                status = ValidationState.PASS
            else:
                status = ValidationState.FAIL

        except TimeoutError:
            recv_time = time.perf_counter()
            latency_ms = (recv_time - send_time) * MS_PER_SEC
            actual_resp = "<TIMEOUT>"
            status = ValidationState.TIMEOUT
            logger.warning("Step #%d execution timed out after %.2fms", idx, latency_ms)

        except Exception as exc:
            recv_time = time.perf_counter()
            latency_ms = (recv_time - send_time) * MS_PER_SEC
            actual_resp = f"<ERROR: {type(exc).__name__}>"
            status = ValidationState.ERROR
            logger.error("Step #%d execution error: %s", idx, exc)

        logger.info("Step #%d Result: %s", idx, status.value)

        return ValidationStep(
            step_number=idx,
            command_sent=step.send,
            expected_response=step.expect,
            actual_response=actual_resp,
            status=status,
            latency_ms=latency_ms,
        )

    def _close_clients(
        self, tcp_client: TCPClient | None, udp_client: UDPClient | None
    ) -> None:
        """Safely disconnects active network clients."""
        if tcp_client:
            tcp_client.disconnect()
        if udp_client:
            udp_client.close()

    def validate_testcase(self, testcase: TestCase) -> ExecutionSummary:
        """Executes testcase steps, performs validation checks, and returns ExecutionSummary.

        Args:
            testcase: Parsed and validated TestCase instance.

        Returns:
            ExecutionSummary: Summary of test execution and validation outcomes.
        """
        logger.info(
            "Testcase execution started: '%s' (%s://%s:%d)",
            testcase.name,
            testcase.protocol,
            testcase.host,
            testcase.port,
        )

        overall_start_time = time.perf_counter()
        step_results: list[ValidationStep] = []
        is_tcp = testcase.protocol.upper() == "TCP"

        tcp_client, udp_client = self._create_client(testcase)
        try:
            for idx, step in enumerate(testcase.steps, start=1):
                logger.info(
                    "Executing step #%d/%d: Send '%s' | Expect '%s'",
                    idx,
                    testcase.step_count,
                    step.send,
                    step.expect,
                )
                step_res = self._execute_single_step(
                    idx, step, is_tcp, tcp_client, udp_client
                )
                step_results.append(step_res)
        finally:
            self._close_clients(tcp_client, udp_client)

        passed_count = sum(1 for s in step_results if s.status == ValidationState.PASS)
        failed_count = len(step_results) - passed_count

        overall_end_time = time.perf_counter()
        total_exec_ms = (overall_end_time - overall_start_time) * MS_PER_SEC

        final_status = (
            ValidationState.PASS if failed_count == 0 else ValidationState.FAIL
        )

        summary = ExecutionSummary(
            testcase_name=testcase.name,
            total_steps=testcase.step_count,
            passed_steps=passed_count,
            failed_steps=failed_count,
            final_status=final_status,
            execution_time_ms=total_exec_ms,
            step_results=tuple(step_results),
        )

        logger.info(
            "Testcase execution completed: '%s' -> %s (%d/%d steps passed in %.2fms)",
            testcase.name,
            final_status.value,
            passed_count,
            testcase.step_count,
            total_exec_ms,
        )

        return summary


def validate(testcase: TestCase) -> ExecutionSummary:
    """Public API function to validate a TestCase instance.

    Args:
        testcase: TestCase object to validate.

    Returns:
        ExecutionSummary: Validation execution outcome.
    """
    engine = ValidationEngine()
    return engine.validate_testcase(testcase)
