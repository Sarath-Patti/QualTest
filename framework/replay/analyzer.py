"""Protocol signaling analyzer and metrics calculation engine."""

from datetime import datetime

from framework.logger import get_logger
from framework.replay.models import (
    AnomalyType,
    ModemFSMState,
    ProtocolMessage,
    ReplayAnomaly,
    ReplayEvent,
    ReplayMetrics,
)

logger = get_logger("Replay.Analyzer")

PERCENT_MULTIPLIER: float = 100.0


class ProtocolAnalyzer:
    """Analyzes protocol signaling sequences, detects anomalies, and computes replay metrics."""

    def _parse_timestamp(self, ts_str: str) -> float:
        """Parses timestamp string to seconds float."""
        clean = ts_str.strip()
        # Attempt float conversion
        try:
            return float(clean)
        except ValueError:
            pass

        # Attempt ISO or time string parsing
        for fmt in (
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%H:%M:%S.%f",
            "%H:%M:%S",
        ):
            try:
                dt = datetime.strptime(clean, fmt)
                return dt.timestamp()
            except ValueError:
                continue

        return 0.0

    def analyze_events(
        self,
        events: list[ReplayEvent],
        transitions: list[tuple[ReplayEvent, ModemFSMState, ModemFSMState, bool]],
    ) -> tuple[list[ReplayAnomaly], ReplayMetrics]:
        """Analyzes signaling events and transitions to produce anomalies and metrics.

        Args:
            events: List of parsed ReplayEvent records.
            transitions: List of (event, prev_state, curr_state, is_valid) tuples.

        Returns:
            tuple[list[ReplayAnomaly], ReplayMetrics]: Detected anomalies and computed metrics.
        """
        logger.info("Starting protocol signaling analysis...")
        anomalies: list[ReplayAnomaly] = []

        seen_messages: set[ProtocolMessage] = set()
        attach_req_time: float | None = None
        attach_accept_time: float | None = None
        rrc_req_time: float | None = None
        registered_time: float | None = None
        handover_req_time: float | None = None
        handover_comp_time: float | None = None

        last_msg: ProtocolMessage | None = None
        valid_count = 0
        invalid_count = 0

        for event, prev_state, curr_state, is_valid in transitions:
            msg = event.message
            ts_val = self._parse_timestamp(event.timestamp)

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                anomalies.append(
                    ReplayAnomaly(
                        anomaly_type=AnomalyType.INVALID_TRANSITION,
                        message=f"Invalid transition for '{msg.value}' in state {prev_state.value}.",
                        timestamp=event.timestamp,
                        event=event,
                    )
                )

            # 1. Unknown message detection
            if msg == ProtocolMessage.UNKNOWN_MESSAGE:
                anomalies.append(
                    ReplayAnomaly(
                        anomaly_type=AnomalyType.UNKNOWN_MESSAGE,
                        message="Unknown protocol message encountered in stream.",
                        timestamp=event.timestamp,
                        event=event,
                    )
                )

            # 2. Duplicate message detection
            if msg == last_msg and msg not in (
                ProtocolMessage.SERVICE_REQUEST,
                ProtocolMessage.SERVICE_ACCEPT,
            ):
                anomalies.append(
                    ReplayAnomaly(
                        anomaly_type=AnomalyType.DUPLICATE_MESSAGE,
                        message=f"Duplicate consecutive message '{msg.value}' detected.",
                        timestamp=event.timestamp,
                        event=event,
                    )
                )
            last_msg = msg

            # 3. Unexpected Detach
            if msg == ProtocolMessage.DETACH_REQUEST and prev_state in (
                ModemFSMState.IDLE,
                ModemFSMState.RRC_CONNECTING,
            ):
                anomalies.append(
                    ReplayAnomaly(
                        anomaly_type=AnomalyType.UNEXPECTED_DETACH,
                        message=f"Unexpected DETACH_REQUEST while modem in state {prev_state.value}.",
                        timestamp=event.timestamp,
                        event=event,
                    )
                )

            # 4. Missing message check (e.g. NAS_ATTACH_ACCEPT without NAS_ATTACH_REQUEST)
            if (
                msg == ProtocolMessage.NAS_ATTACH_ACCEPT
                and ProtocolMessage.NAS_ATTACH_REQUEST not in seen_messages
            ):
                anomalies.append(
                    ReplayAnomaly(
                        anomaly_type=AnomalyType.MISSING_MESSAGE,
                        message="NAS_ATTACH_ACCEPT received without prior NAS_ATTACH_REQUEST.",
                        timestamp=event.timestamp,
                        event=event,
                    )
                )

            # 5. Authentication Failure
            if (
                msg == ProtocolMessage.NAS_ATTACH_ACCEPT
                and ProtocolMessage.NAS_AUTH_REQUEST in seen_messages
                and ProtocolMessage.NAS_AUTH_ACCEPT not in seen_messages
            ):
                anomalies.append(
                    ReplayAnomaly(
                        anomaly_type=AnomalyType.AUTHENTICATION_FAILURE,
                        message="NAS_ATTACH_ACCEPT reached without completing authentication procedure.",
                        timestamp=event.timestamp,
                        event=event,
                    )
                )

            # Track procedure timestamps
            if msg == ProtocolMessage.RRC_CONNECTION_REQUEST and rrc_req_time is None:
                rrc_req_time = ts_val
            if (
                curr_state == ModemFSMState.REGISTERED
                and registered_time is None
                and rrc_req_time is not None
            ):
                registered_time = ts_val

            if msg == ProtocolMessage.NAS_ATTACH_REQUEST and attach_req_time is None:
                attach_req_time = ts_val
            if msg == ProtocolMessage.NAS_ATTACH_ACCEPT and attach_accept_time is None:
                attach_accept_time = ts_val

            if msg == ProtocolMessage.HANDOVER_REQUEST and handover_req_time is None:
                handover_req_time = ts_val
            if msg == ProtocolMessage.HANDOVER_COMPLETE and handover_comp_time is None:
                handover_comp_time = ts_val

            seen_messages.add(msg)

        # Calculate procedure durations
        total_duration_ms = 0.0
        if events:
            first_ts = self._parse_timestamp(events[0].timestamp)
            last_ts = self._parse_timestamp(events[-1].timestamp)
            if last_ts >= first_ts:
                total_duration_ms = (last_ts - first_ts) * 1000.0

        attach_dur_ms = 0.0
        if (
            attach_req_time is not None
            and attach_accept_time is not None
            and attach_accept_time >= attach_req_time
        ):
            attach_dur_ms = (attach_accept_time - attach_req_time) * 1000.0

        reg_dur_ms = 0.0
        if (
            rrc_req_time is not None
            and registered_time is not None
            and registered_time >= rrc_req_time
        ):
            reg_dur_ms = (registered_time - rrc_req_time) * 1000.0

        ho_dur_ms = 0.0
        if (
            handover_req_time is not None
            and handover_comp_time is not None
            and handover_comp_time >= handover_req_time
        ):
            ho_dur_ms = (handover_comp_time - handover_req_time) * 1000.0

        total_msgs = len(events)
        comp_pct = (
            (valid_count / total_msgs * PERCENT_MULTIPLIER) if total_msgs > 0 else 0.0
        )

        metrics = ReplayMetrics(
            total_replay_duration_ms=total_duration_ms,
            attach_duration_ms=attach_dur_ms,
            registration_duration_ms=reg_dur_ms,
            handover_duration_ms=ho_dur_ms,
            message_count=total_msgs,
            state_transitions=valid_count,
            invalid_transitions=invalid_count,
            completion_percentage=comp_pct,
        )

        logger.info(
            "Analysis completed: %d anomalies, completion=%.1f%%, attach_dur=%.2fms",
            len(anomalies),
            metrics.completion_percentage,
            metrics.attach_duration_ms,
        )

        return anomalies, metrics
