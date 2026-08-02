"""Protocol Log Replay & Analysis Engine package for QualTest framework."""

from pathlib import Path

from framework.replay.analyzer import ProtocolAnalyzer
from framework.replay.exceptions import (
    InvalidStateTransitionError,
    ProtocolAnalysisError,
    ReplayError,
    ReplayParseError,
)
from framework.replay.log_parser import ReplayLogParser
from framework.replay.models import (
    AnomalyType,
    MessageDirection,
    ModemFSMState,
    ProtocolMessage,
    ProtocolType,
    ReplayAnomaly,
    ReplayEvent,
    ReplayMetrics,
    ReplaySummary,
    TimelineEvent,
)
from framework.replay.replay_engine import ReplayEngine
from framework.replay.state_machine import ModemFSM
from framework.replay.timeline import ReplayTimelineGenerator


def replay_log(file_path: str | Path, speed_factor: float = 1.0) -> ReplaySummary:
    """Public API helper to replay a protocol log file and return summary metrics.

    Args:
        file_path: Path to target protocol log file.
        speed_factor: Replay timing speed multiplier.

    Returns:
        ReplaySummary: Complete replay summary results.
    """
    engine = ReplayEngine(speed_factor=speed_factor)
    return engine.replay(file_path)


__all__ = [
    "AnomalyType",
    "InvalidStateTransitionError",
    "MessageDirection",
    "ModemFSM",
    "ModemFSMState",
    "ProtocolAnalysisError",
    "ProtocolAnalyzer",
    "ProtocolMessage",
    "ProtocolType",
    "ReplayAnomaly",
    "ReplayEngine",
    "ReplayError",
    "ReplayEvent",
    "ReplayLogParser",
    "ReplayMetrics",
    "ReplayParseError",
    "ReplaySummary",
    "ReplayTimelineGenerator",
    "TimelineEvent",
    "replay_log",
]
