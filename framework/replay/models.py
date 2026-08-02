"""Data models and enumerations for protocol log replay and analysis."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ProtocolType(Enum):
    """Supported LTE/5G protocol layers."""

    RRC = "RRC"
    NAS = "NAS"
    MOBILITY = "MOBILITY"
    DETACH = "DETACH"
    UNKNOWN = "UNKNOWN"


class ProtocolMessage(Enum):
    """Supported LTE/5G signaling messages."""

    # RRC
    RRC_CONNECTION_REQUEST = "RRC_CONNECTION_REQUEST"
    RRC_CONNECTION_SETUP = "RRC_CONNECTION_SETUP"
    RRC_CONNECTION_SETUP_COMPLETE = "RRC_CONNECTION_SETUP_COMPLETE"

    # NAS
    NAS_ATTACH_REQUEST = "NAS_ATTACH_REQUEST"
    NAS_ATTACH_ACCEPT = "NAS_ATTACH_ACCEPT"
    NAS_AUTH_REQUEST = "NAS_AUTH_REQUEST"
    NAS_AUTH_ACCEPT = "NAS_AUTH_ACCEPT"

    # Mobility
    SERVICE_REQUEST = "SERVICE_REQUEST"
    SERVICE_ACCEPT = "SERVICE_ACCEPT"
    HANDOVER_REQUEST = "HANDOVER_REQUEST"
    HANDOVER_COMPLETE = "HANDOVER_COMPLETE"

    # Detach
    DETACH_REQUEST = "DETACH_REQUEST"
    DETACH_ACCEPT = "DETACH_ACCEPT"

    # Unknown
    UNKNOWN_MESSAGE = "UNKNOWN_MESSAGE"

    @classmethod
    def from_str(cls, value: str) -> "ProtocolMessage":
        """Converts string name to ProtocolMessage enum safely."""
        clean_val = value.strip().upper()
        for item in cls:
            if item.value == clean_val:
                return item
        return cls.UNKNOWN_MESSAGE


class MessageDirection(Enum):
    """Direction of message transmission relative to the modem."""

    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"

    @classmethod
    def from_str(cls, value: str) -> "MessageDirection":
        """Converts string direction to MessageDirection enum."""
        clean_val = value.strip().upper()
        if clean_val in ("INCOMING", "IN", "RX", "RECEIVED"):
            return cls.INCOMING
        return cls.OUTGOING


class ModemFSMState(Enum):
    """Supported modem protocol states for Finite State Machine."""

    IDLE = "IDLE"
    RRC_CONNECTING = "RRC_CONNECTING"
    CONNECTED = "CONNECTED"
    REGISTERED = "REGISTERED"
    IN_SERVICE = "IN_SERVICE"
    HANDOVER = "HANDOVER"
    DETACHED = "DETACHED"
    ERROR = "ERROR"


class AnomalyType(Enum):
    """Classification types for protocol anomalies."""

    MISSING_MESSAGE = "MISSING_MESSAGE"
    DUPLICATE_MESSAGE = "DUPLICATE_MESSAGE"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    UNEXPECTED_DETACH = "UNEXPECTED_DETACH"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    REPLAY_TIMEOUT = "REPLAY_TIMEOUT"
    OUT_OF_ORDER_SIGNALING = "OUT_OF_ORDER_SIGNALING"
    UNKNOWN_MESSAGE = "UNKNOWN_MESSAGE"


@dataclass(frozen=True)
class ReplayEvent:
    """Represents a single parsed protocol signaling event from a log file.

    Attributes:
        timestamp: Time representation string.
        protocol: ProtocolType layer identifier.
        message: ProtocolMessage enum instance.
        direction: MessageDirection relative to modem.
        metadata: Optional metadata dictionary.
    """

    timestamp: str
    protocol: ProtocolType
    message: ProtocolMessage
    direction: MessageDirection
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimelineEvent:
    """Represents an ordered protocol timeline entry.

    Attributes:
        timestamp: Event timestamp.
        message: ProtocolMessage instance.
        previous_state: State before message processing.
        current_state: State after message processing.
        validation_result: Outcome string (PASS, FAIL, ANOMALY).
        anomaly: Optional AnomalyType if an issue occurred.
    """

    timestamp: str
    message: ProtocolMessage
    previous_state: ModemFSMState
    current_state: ModemFSMState
    validation_result: str
    anomaly: AnomalyType | None = None


@dataclass(frozen=True)
class ReplayAnomaly:
    """Detailed record of a detected protocol anomaly.

    Attributes:
        anomaly_type: Category of anomaly detected.
        message: Human-readable explanation.
        timestamp: Timestamp where anomaly occurred.
        event: Optional associated ReplayEvent record.
    """

    anomaly_type: AnomalyType
    message: str
    timestamp: str
    event: ReplayEvent | None = None


@dataclass(frozen=True)
class ReplayMetrics:
    """Immutable metrics calculated from log replay and analysis.

    Attributes:
        total_replay_duration_ms: Total duration of replayed log in milliseconds.
        attach_duration_ms: Time duration to complete NAS Attach procedure.
        registration_duration_ms: Time duration from RRC request to REGISTERED.
        handover_duration_ms: Time duration to complete Handover procedure.
        message_count: Total count of replayed protocol messages.
        state_transitions: Number of valid state transitions.
        invalid_transitions: Number of invalid state transitions.
        completion_percentage: Percentage of valid message processing (0.0 - 100.0).
    """

    total_replay_duration_ms: float
    attach_duration_ms: float
    registration_duration_ms: float
    handover_duration_ms: float
    message_count: int
    state_transitions: int
    invalid_transitions: int
    completion_percentage: float


@dataclass(frozen=True)
class ReplaySummary:
    """Aggregated outcome summary of a protocol log replay run.

    Attributes:
        log_file_path: Path to the replayed log file.
        total_events: Total number of events parsed.
        timeline: Tuple of TimelineEvent records.
        anomalies: Tuple of ReplayAnomaly records detected.
        metrics: ReplayMetrics metrics object.
        final_state: Final ModemFSMState of state machine.
    """

    log_file_path: Path
    total_events: int
    timeline: tuple[TimelineEvent, ...]
    anomalies: tuple[ReplayAnomaly, ...]
    metrics: ReplayMetrics
    final_state: ModemFSMState
