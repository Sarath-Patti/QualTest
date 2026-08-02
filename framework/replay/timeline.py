"""Timeline generator for protocol log replay visualization and tracking."""

from framework.logger import get_logger
from framework.replay.models import (
    AnomalyType,
    ModemFSMState,
    ReplayEvent,
    TimelineEvent,
)

logger = get_logger("Replay.Timeline")


class ReplayTimelineGenerator:
    """Generates an ordered protocol timeline from replayed events and state transitions."""

    def build_timeline(
        self,
        events_with_transitions: list[
            tuple[ReplayEvent, ModemFSMState, ModemFSMState, bool, AnomalyType | None]
        ],
    ) -> tuple[TimelineEvent, ...]:
        """Builds an ordered tuple of TimelineEvent objects.

        Args:
            events_with_transitions: List of tuples containing:
                (event, prev_state, curr_state, is_valid_transition, optional_anomaly)

        Returns:
            tuple[TimelineEvent, ...]: Ordered timeline entries.
        """
        logger.info("Generating protocol replay timeline...")
        timeline: list[TimelineEvent] = []

        for event, prev_state, curr_state, is_valid, anomaly in events_with_transitions:
            if not is_valid:
                val_result = "FAIL"
            elif anomaly is not None:
                val_result = "ANOMALY"
            else:
                val_result = "PASS"

            entry = TimelineEvent(
                timestamp=event.timestamp,
                message=event.message,
                previous_state=prev_state,
                current_state=curr_state,
                validation_result=val_result,
                anomaly=anomaly,
            )
            timeline.append(entry)

        logger.info("Generated protocol timeline with %d entries.", len(timeline))
        return tuple(timeline)
