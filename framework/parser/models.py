"""Data models representing testcases and execution steps.

Provides structured, immutable dataclasses for testcase representations within
the QualTest framework.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(frozen=True)
class TestStep:
    """Represents a single command-response interaction step.

    Attributes:
        send: The command payload string to send to the target.
        expect: The expected response string from the target.
        delay: Optional delay in seconds before executing the step.
    """

    send: str
    expect: str
    delay: float = 0.0


@dataclass(frozen=True)
class TestCase:
    """Represents a validated testcase configuration.

    Attributes:
        name: Short descriptive name of the testcase.
        description: Full summary description of test objective.
        protocol: Network protocol (e.g. 'TCP', 'UDP').
        host: Target hostname or IP address.
        port: Target network port number.
        timeout: Execution timeout in seconds (must be > 0).
        retry: Number of retry attempts on failure (must be >= 0).
        steps: List of TestStep objects defining the execution sequence.
    """

    name: str
    description: str
    protocol: str
    host: str
    port: int
    timeout: float
    retry: int
    steps: Tuple[TestStep, ...] = field(default_factory=tuple)

    @property
    def step_count(self) -> int:
        """Returns the number of steps in the testcase.

        Returns:
            int: Total step count.
        """
        return len(self.steps)
