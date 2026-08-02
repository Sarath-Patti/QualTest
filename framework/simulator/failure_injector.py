"""Failure injection engine for QualTest modem simulation.

Simulates wireless network anomalies including packet loss, artificial delay,
timeouts, connection resets, random disconnects, and malformed responses.
"""

import json
import random
import time
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any

from framework.logger import get_logger

logger = get_logger("Simulator.FailureInjector")

PERCENT_SCALE: float = 100.0
MS_TO_SEC: float = 1000.0
MALFORMED_MIN: int = 1000
MALFORMED_MAX: int = 9999


class FailureAction(Enum):
    """Supported failure action types for simulator failure injection."""

    NONE = auto()
    DROP_PACKET = auto()
    ARTIFICIAL_DELAY = auto()
    TIMEOUT = auto()
    DISCONNECT = auto()
    MALFORMED_RESPONSE = auto()


@dataclass
class FailureConfig:
    """Configuration settings for simulator failure injection.

    Attributes:
        enabled: Master toggle to enable or disable failure injection.
        packet_loss_percentage: Percentage chance to drop outgoing packet (0.0 - 100.0).
        minimum_delay_ms: Minimum artificial delay in milliseconds.
        maximum_delay_ms: Maximum artificial delay in milliseconds.
        timeout_probability: Probability of generating a timeout (0.0 - 1.0).
        disconnect_probability: Probability of triggering random disconnect (0.0 - 1.0).
        malformed_response_probability: Probability of returning malformed response (0.0 - 1.0).
    """

    enabled: bool = False
    packet_loss_percentage: float = 0.0
    minimum_delay_ms: float = 0.0
    maximum_delay_ms: float = 0.0
    timeout_probability: float = 0.0
    disconnect_probability: float = 0.0
    malformed_response_probability: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FailureConfig":
        """Builds FailureConfig from dictionary data."""
        return cls(
            enabled=bool(data.get("enabled", False)),
            packet_loss_percentage=float(data.get("packet_loss_percentage", 0.0)),
            minimum_delay_ms=float(data.get("minimum_delay_ms", 0.0)),
            maximum_delay_ms=float(data.get("maximum_delay_ms", 0.0)),
            timeout_probability=float(data.get("timeout_probability", 0.0)),
            disconnect_probability=float(data.get("disconnect_probability", 0.0)),
            malformed_response_probability=float(
                data.get("malformed_response_probability", 0.0)
            ),
        )


class FailureInjector:
    """Protocol-independent failure injection engine."""

    def __init__(self, config: FailureConfig | None = None) -> None:
        """Initializes FailureInjector.

        Args:
            config: FailureConfig instance. Defaults to disabled configuration.
        """
        self.config = config or FailureConfig()
        if self.config.enabled:
            logger.info(
                "Failure injection enabled: loss=%.1f%%, delay=[%.1f-%.1f]ms, timeout=%.2f, disconnect=%.2f, malformed=%.2f",
                self.config.packet_loss_percentage,
                self.config.minimum_delay_ms,
                self.config.maximum_delay_ms,
                self.config.timeout_probability,
                self.config.disconnect_probability,
                self.config.malformed_response_probability,
            )

    @classmethod
    def from_file(cls, path: str | Path) -> "FailureInjector":
        """Loads FailureInjector configuration from a JSON file.

        Args:
            path: Path to JSON configuration file.

        Returns:
            FailureInjector: Instantiated failure injector.
        """
        file_path = Path(path).resolve()
        if not file_path.exists():
            logger.error("Failure configuration file not found: %s", file_path)
            raise FileNotFoundError(f"Failure config file not found: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            config = FailureConfig.from_dict(data)
            return cls(config)
        except Exception as exc:
            logger.error("Failed to parse failure config from %s: %s", file_path, exc)
            raise

    @property
    def enabled(self) -> bool:
        """Indicates whether failure injection is active."""
        return self.config.enabled

    def _evaluate_disconnect(self, cmd_clean: str) -> tuple[FailureAction, Any] | None:
        """Evaluates random disconnect condition."""
        if (
            self.config.disconnect_probability > 0
            and random.random() < self.config.disconnect_probability
        ):
            logger.info(
                "Failure injected: Random disconnect triggered for command '%s'",
                cmd_clean,
            )
            return FailureAction.DISCONNECT, None
        return None

    def _evaluate_timeout(self, cmd_clean: str) -> tuple[FailureAction, Any] | None:
        """Evaluates timeout condition."""
        if (
            self.config.timeout_probability > 0
            and random.random() < self.config.timeout_probability
        ):
            logger.info(
                "Failure injected: Timeout generated for command '%s'", cmd_clean
            )
            return FailureAction.TIMEOUT, None
        return None

    def _evaluate_packet_loss(self, cmd_clean: str) -> tuple[FailureAction, Any] | None:
        """Evaluates packet drop condition."""
        if (
            self.config.packet_loss_percentage > 0
            and (random.random() * PERCENT_SCALE) < self.config.packet_loss_percentage
        ):
            logger.info("Failure injected: Packet dropped for command '%s'", cmd_clean)
            return FailureAction.DROP_PACKET, None
        return None

    def _evaluate_malformed(self, cmd_clean: str) -> tuple[FailureAction, Any] | None:
        """Evaluates malformed payload response condition."""
        if (
            self.config.malformed_response_probability > 0
            and random.random() < self.config.malformed_response_probability
        ):
            malformed_payload = f"???MALFORMED_GARBAGE_{random.randint(MALFORMED_MIN, MALFORMED_MAX)}???"
            logger.info(
                "Failure injected: Malformed response generated for command '%s' -> '%s'",
                cmd_clean,
                malformed_payload,
            )
            return FailureAction.MALFORMED_RESPONSE, malformed_payload
        return None

    def _evaluate_delay(self, cmd_clean: str) -> tuple[FailureAction, Any] | None:
        """Evaluates artificial response delay condition."""
        if (
            self.config.maximum_delay_ms > 0
            and self.config.maximum_delay_ms >= self.config.minimum_delay_ms
        ):
            delay_ms = random.uniform(
                self.config.minimum_delay_ms, self.config.maximum_delay_ms
            )
            if delay_ms > 0:
                logger.info(
                    "Failure injected: Artificial delay of %.2fms applied for command '%s'",
                    delay_ms,
                    cmd_clean,
                )
                time.sleep(delay_ms / MS_TO_SEC)
                return FailureAction.ARTIFICIAL_DELAY, delay_ms
        return None

    def evaluate_failure(self, command_str: str) -> tuple[FailureAction, Any]:
        """Evaluates configured failure conditions for an incoming command string.

        Args:
            command_str: Incoming command string.

        Returns:
            tuple[FailureAction, Any]: Selected action and associated payload/delay parameter.
        """
        if not self.config.enabled:
            return FailureAction.NONE, None

        cmd_clean = command_str.strip()

        evaluators = (
            self._evaluate_disconnect,
            self._evaluate_timeout,
            self._evaluate_packet_loss,
            self._evaluate_malformed,
            self._evaluate_delay,
        )

        for evaluator in evaluators:
            res = evaluator(cmd_clean)
            if res is not None:
                return res

        return FailureAction.NONE, None
