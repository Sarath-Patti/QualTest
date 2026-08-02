"""Validation engine implementation for QualTest framework.

Executes testcase steps against target modem servers, measures command latencies,
compares actual against expected responses, and produces structured ExecutionSummary results.
"""

import socket
import time
from typing import List, Optional

from framework.logger import get_logger
from framework.parser import TestCase
from framework.validator.models import (
    ExecutionSummary,
    ValidationState,
    ValidationStep,
)
from network.tcp import TCPClient, TCPClientConfig
from network.udp import UDPClient, UDPClientConfig

logger = get_logger("Validator.Engine")


class ValidationEngine:
    """Core engine for executing and validating testcases against modem targets."""

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
        step_results: List[ValidationStep] = []
        passed_count = 0
        failed_count = 0

        # Protocol client instantiation
        is_tcp = testcase.protocol.upper() == "TCP"
        tcp_client: Optional[TCPClient] = None
        udp_client: Optional[UDPClient] = None

        try:
            if is_tcp:
                tcp_client = TCPClient(
                    TCPClientConfig(
                        host=testcase.host,
                        port=testcase.port,
                        timeout_seconds=testcase.timeout,
                    )
                )
                tcp_client.connect()
            else:
                udp_client = UDPClient(
                    UDPClientConfig(
                        host=testcase.host,
                        port=testcase.port,
                        timeout_seconds=testcase.timeout,
                    )
                )
        except Exception as exc:
            logger.error(
                "Failed to establish network connection to %s://%s:%d: %s",
                testcase.protocol,
                testcase.host,
                testcase.port,
                exc,
            )
            # Record connection error across all steps
            for idx, step in enumerate(testcase.steps, start=1):
                step_results.append(
                    ValidationStep(
                        step_number=idx,
                        command_sent=step.send,
                        expected_response=step.expect,
                        actual_response="<CONNECTION_ERROR>",
                        status=ValidationState.ERROR,
                        latency_ms=0.0,
                    )
                )
                failed_count += 1

            overall_end_time = time.perf_counter()
            exec_time_ms = (overall_end_time - overall_start_time) * 1000.0
            return ExecutionSummary(
                testcase_name=testcase.name,
                total_steps=testcase.step_count,
                passed_steps=0,
                failed_steps=testcase.step_count,
                execution_time_ms=exec_time_ms,
                final_status=ValidationState.ERROR,
                step_results=tuple(step_results),
            )

        # Execute testcase steps sequentially
        try:
            for idx, step in enumerate(testcase.steps, start=1):
                if step.delay > 0:
                    time.sleep(step.delay)

                logger.info(
                    "Executing Step #%d: Send '%s' | Expect '%s'",
                    idx,
                    step.send,
                    step.expect,
                )

                send_time = time.perf_counter()
                actual_resp = ""
                status = ValidationState.UNKNOWN

                try:
                    if is_tcp and tcp_client:
                        payload = (step.send.strip() + "\n").encode("utf-8")
                        tcp_client.send(payload)
                        recv_bytes = tcp_client.receive()
                        actual_resp = recv_bytes.decode("utf-8", errors="replace").strip()
                    elif udp_client:
                        actual_resp = udp_client.send_command(step.send)

                    recv_time = time.perf_counter()
                    latency_ms = (recv_time - send_time) * 1000.0

                    logger.info(
                        "Received response: '%s' (Latency: %.2fms)",
                        actual_resp,
                        latency_ms,
                    )

                    # Compare response
                    if actual_resp == step.expect:
                        status = ValidationState.PASS
                        passed_count += 1
                    else:
                        status = ValidationState.FAIL
                        failed_count += 1

                except socket.timeout:
                    recv_time = time.perf_counter()
                    latency_ms = (recv_time - send_time) * 1000.0
                    actual_resp = "<TIMEOUT>"
                    status = ValidationState.TIMEOUT
                    failed_count += 1
                    logger.warning("Step #%d execution timed out after %.2fms", idx, latency_ms)
                except Exception as exc:
                    recv_time = time.perf_counter()
                    latency_ms = (recv_time - send_time) * 1000.0
                    actual_resp = f"<ERROR: {type(exc).__name__}>"
                    status = ValidationState.ERROR
                    failed_count += 1
                    logger.error("Step #%d execution error: %s", idx, exc)

                logger.info("Step #%d Result: %s", idx, status.value)

                step_results.append(
                    ValidationStep(
                        step_number=idx,
                        command_sent=step.send,
                        expected_response=step.expect,
                        actual_response=actual_resp,
                        status=status,
                        latency_ms=latency_ms,
                    )
                )
        finally:
            if tcp_client:
                tcp_client.disconnect()
            if udp_client:
                udp_client.close()

        overall_end_time = time.perf_counter()
        total_exec_time_ms = (overall_end_time - overall_start_time) * 1000.0

        # Determine overall final status
        if passed_count == testcase.step_count:
            final_status = ValidationState.PASS
        elif any(s.status == ValidationState.ERROR for s in step_results):
            final_status = ValidationState.ERROR
        elif any(s.status == ValidationState.TIMEOUT for s in step_results):
            final_status = ValidationState.TIMEOUT
        else:
            final_status = ValidationState.FAIL

        logger.info(
            "Execution completed: '%s' -> %s (%d/%d passed in %.2fms)",
            testcase.name,
            final_status.value,
            passed_count,
            testcase.step_count,
            total_exec_time_ms,
        )

        return ExecutionSummary(
            testcase_name=testcase.name,
            total_steps=testcase.step_count,
            passed_steps=passed_count,
            failed_steps=failed_count,
            execution_time_ms=total_exec_time_ms,
            final_status=final_status,
            step_results=tuple(step_results),
        )


def validate(testcase: TestCase) -> ExecutionSummary:
    """Public validation API function.

    Args:
        testcase: Loaded and parsed TestCase model.

    Returns:
        ExecutionSummary: Execution summary results.
    """
    engine = ValidationEngine()
    return engine.validate_testcase(testcase)
