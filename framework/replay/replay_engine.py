"""Protocol log replay execution engine for offline signaling validation."""

import time
from pathlib import Path

from framework.logger import get_logger
from framework.replay.analyzer import ProtocolAnalyzer
from framework.replay.log_parser import ReplayLogParser
from framework.replay.models import (
    AnomalyType,
    ModemFSMState,
    ReplayEvent,
    ReplaySummary,
)
from framework.replay.state_machine import ModemFSM
from framework.replay.timeline import ReplayTimelineGenerator

logger = get_logger("Replay.Engine")


class ReplayEngine:
    """Offline protocol signaling log replay and analysis controller."""

    def __init__(self, speed_factor: float = 1.0) -> None:
        """Initializes ReplayEngine.

        Args:
            speed_factor: Replay timing speed multiplier (e.g. 1.0 = normal, 2.0 = 2x speed).
        """
        self.speed_factor = max(0.1, speed_factor)
        self._parser = ReplayLogParser()
        self._fsm = ModemFSM()
        self._timeline_gen = ReplayTimelineGenerator()
        self._analyzer = ProtocolAnalyzer()

        self._is_running: bool = False
        self._is_paused: bool = False

    @property
    def is_running(self) -> bool:
        """Indicates whether replay execution is currently active."""
        return self._is_running

    @property
    def is_paused(self) -> bool:
        """Indicates whether replay execution is currently paused."""
        return self._is_paused

    def start(self) -> None:
        """Starts or resets replay engine execution lifecycle."""
        self._is_running = True
        self._is_paused = False
        self._fsm.reset()
        logger.info("ReplayEngine started.")

    def pause(self) -> None:
        """Pauses active replay execution."""
        if self._is_running:
            self._is_paused = True
            logger.info("ReplayEngine paused.")

    def resume(self) -> None:
        """Resumes paused replay execution."""
        if self._is_running and self._is_paused:
            self._is_paused = False
            logger.info("ReplayEngine resumed.")

    def stop(self) -> None:
        """Stops active replay execution."""
        self._is_running = False
        self._is_paused = False
        logger.info("ReplayEngine stopped.")

    def replay(self, file_path: str | Path) -> ReplaySummary:
        """Parses a protocol log file, replays signaling offline, and generates ReplaySummary.

        Args:
            file_path: Path to target protocol log file.

        Returns:
            ReplaySummary: Complete replay summary results including timeline, anomalies, and metrics.
        """
        path = Path(file_path).resolve()
        logger.info("Starting offline protocol log replay for: %s", path)

        self.start()
        events = self._parser.parse(path)

        transitions: list[tuple[ReplayEvent, ModemFSMState, ModemFSMState, bool]] = []
        raw_timeline_entries: list[
            tuple[ReplayEvent, ModemFSMState, ModemFSMState, bool, AnomalyType | None]
        ] = []

        start_wall_time = time.perf_counter()

        for idx, event in enumerate(events, start=1):
            if not self._is_running:
                logger.warning("Replay interrupted at event #%d", idx)
                break

            while self._is_paused:
                time.sleep(0.05)

            logger.info(
                "Replaying event #%d/%d: [%s] %s %s (%s)",
                idx,
                len(events),
                event.timestamp,
                event.protocol.value,
                event.message.value,
                event.direction.value,
            )

            prev_state, curr_state, is_valid = self._fsm.transition(event.message)
            transitions.append((event, prev_state, curr_state, is_valid))

            anomaly: AnomalyType | None = None
            if not is_valid:
                anomaly = AnomalyType.INVALID_TRANSITION

            raw_timeline_entries.append(
                (event, prev_state, curr_state, is_valid, anomaly)
            )

        end_wall_time = time.perf_counter()
        logger.info(
            "Replay execution finished in %.2fms wall-clock time.",
            (end_wall_time - start_wall_time) * 1000.0,
        )

        # Analyze protocol events & compute metrics
        anomalies, metrics = self._analyzer.analyze_events(events, transitions)
        timeline = self._timeline_gen.build_timeline(raw_timeline_entries)
        final_state = self._fsm.current_state

        self.stop()

        summary = ReplaySummary(
            log_file_path=path,
            total_events=len(events),
            timeline=timeline,
            anomalies=tuple(anomalies),
            metrics=metrics,
            final_state=final_state,
        )

        logger.info(
            "Protocol log replay completed: '%s' -> Final State: %s (%d events, %d anomalies)",
            path.name,
            final_state.value,
            summary.total_events,
            len(anomalies),
        )

        return summary
