"""Unit tests for QualTest protocol log replay and analysis engine."""

from pathlib import Path

from framework.replay import (
    AnomalyType,
    ModemFSM,
    ModemFSMState,
    ProtocolMessage,
    ReplayEngine,
    ReplayLogParser,
    ReplaySummary,
    replay_log,
)


def test_fsm_valid_transitions() -> None:
    """Verifies valid state transitions in the ModemFSM."""
    fsm = ModemFSM()
    assert fsm.current_state == ModemFSMState.IDLE

    # IDLE -> RRC_CONNECTING
    prev, curr, valid = fsm.transition(ProtocolMessage.RRC_CONNECTION_REQUEST)
    assert valid is True
    assert prev == ModemFSMState.IDLE
    assert curr == ModemFSMState.RRC_CONNECTING

    # RRC_CONNECTING -> CONNECTED
    prev, curr, valid = fsm.transition(ProtocolMessage.RRC_CONNECTION_SETUP_COMPLETE)
    assert valid is True
    assert curr == ModemFSMState.CONNECTED

    # CONNECTED -> REGISTERED
    prev, curr, valid = fsm.transition(ProtocolMessage.NAS_ATTACH_ACCEPT)
    assert valid is True
    assert curr == ModemFSMState.REGISTERED

    # REGISTERED -> IN_SERVICE
    prev, curr, valid = fsm.transition(ProtocolMessage.SERVICE_ACCEPT)
    assert valid is True
    assert curr == ModemFSMState.IN_SERVICE

    # IN_SERVICE -> HANDOVER -> IN_SERVICE
    fsm.transition(ProtocolMessage.HANDOVER_REQUEST)
    assert fsm.current_state == ModemFSMState.HANDOVER
    fsm.transition(ProtocolMessage.HANDOVER_COMPLETE)
    assert fsm.current_state == ModemFSMState.IN_SERVICE

    # IN_SERVICE -> DETACHED
    fsm.transition(ProtocolMessage.DETACH_REQUEST)
    assert fsm.current_state == ModemFSMState.DETACHED


def test_fsm_invalid_transition() -> None:
    """Verifies that an invalid state transition sets state to ERROR."""
    fsm = ModemFSM()
    assert fsm.current_state == ModemFSMState.IDLE

    # HANDOVER_COMPLETE in IDLE is invalid
    prev, curr, valid = fsm.transition(ProtocolMessage.HANDOVER_COMPLETE)
    assert valid is False
    assert curr == ModemFSMState.ERROR


def test_json_log_parser() -> None:
    """Verifies parsing a JSON sample protocol log file."""
    parser = ReplayLogParser()
    sample_file = Path("logs/samples/attach_success.json")
    events = parser.parse(sample_file)
    assert len(events) == 7
    assert events[0].message == ProtocolMessage.RRC_CONNECTION_REQUEST
    assert events[-1].message == ProtocolMessage.NAS_ATTACH_ACCEPT


def test_replay_engine_attach_success() -> None:
    """Verifies offline replay engine execution for attach_success.json."""
    engine = ReplayEngine()
    summary = engine.replay("logs/samples/attach_success.json")
    assert isinstance(summary, ReplaySummary)
    assert summary.total_events == 7
    assert summary.final_state == ModemFSMState.REGISTERED
    assert len(summary.anomalies) == 0
    assert summary.metrics.completion_percentage == 100.0


def test_replay_engine_attach_failure() -> None:
    """Verifies offline replay engine anomaly detection for attach_failure.json."""
    summary = replay_log("logs/samples/attach_failure.json")
    assert len(summary.anomalies) > 0
    anomaly_types = [a.anomaly_type for a in summary.anomalies]
    assert (
        AnomalyType.INVALID_TRANSITION in anomaly_types
        or AnomalyType.MISSING_MESSAGE in anomaly_types
    )


def test_replay_engine_handover_success() -> None:
    """Verifies offline replay engine execution for handover_success.json."""
    summary = replay_log("logs/samples/handover_success.json")
    assert summary.total_events == 9
    assert summary.final_state in (ModemFSMState.IN_SERVICE, ModemFSMState.REGISTERED)
    assert summary.metrics.invalid_transitions == 0
