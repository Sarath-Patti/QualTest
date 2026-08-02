"""Protocol log parser for JSON, CSV, and Plain Text signaling log formats."""

import csv
import json
from pathlib import Path
from typing import Any

from framework.logger import get_logger
from framework.replay.exceptions import ReplayParseError
from framework.replay.models import (
    MessageDirection,
    ProtocolMessage,
    ProtocolType,
    ReplayEvent,
)

logger = get_logger("Replay.LogParser")


class ReplayLogParser:
    """Parses protocol signaling log files into structured ReplayEvent sequences."""

    def parse(self, file_path: str | Path) -> list[ReplayEvent]:
        """Parses a protocol log file based on its extension or format content.

        Args:
            file_path: Path to target protocol log file.

        Returns:
            list[ReplayEvent]: List of parsed ReplayEvent records.

        Raises:
            ReplayParseError: If file not found, empty, or malformed.
        """
        path = Path(file_path).resolve()
        logger.info("Parsing protocol log file: %s", path)

        if not path.exists() or not path.is_file():
            msg = f"Protocol log file not found: {path}"
            logger.error("Parse failure: %s", msg)
            raise ReplayParseError(msg)

        ext = path.suffix.lower()
        try:
            if ext == ".json":
                return self._parse_json(path)
            elif ext == ".csv":
                return self._parse_csv(path)
            else:
                return self._parse_text(path)
        except ReplayParseError:
            raise
        except Exception as exc:
            msg = f"Failed to parse log file '{path}': {exc}"
            logger.error("Parse failure: %s", msg)
            raise ReplayParseError(msg) from exc

    def _infer_protocol_type(
        self, msg: ProtocolMessage, raw_proto: str
    ) -> ProtocolType:
        """Infers ProtocolType from ProtocolMessage or raw string."""
        if msg in (
            ProtocolMessage.RRC_CONNECTION_REQUEST,
            ProtocolMessage.RRC_CONNECTION_SETUP,
            ProtocolMessage.RRC_CONNECTION_SETUP_COMPLETE,
        ):
            return ProtocolType.RRC

        if msg in (
            ProtocolMessage.NAS_ATTACH_REQUEST,
            ProtocolMessage.NAS_ATTACH_ACCEPT,
            ProtocolMessage.NAS_AUTH_REQUEST,
            ProtocolMessage.NAS_AUTH_ACCEPT,
        ):
            return ProtocolType.NAS

        if msg in (
            ProtocolMessage.SERVICE_REQUEST,
            ProtocolMessage.SERVICE_ACCEPT,
            ProtocolMessage.HANDOVER_REQUEST,
            ProtocolMessage.HANDOVER_COMPLETE,
        ):
            return ProtocolType.MOBILITY

        if msg in (ProtocolMessage.DETACH_REQUEST, ProtocolMessage.DETACH_ACCEPT):
            return ProtocolType.DETACH

        clean_proto = raw_proto.strip().upper()
        for p in ProtocolType:
            if p.value == clean_proto:
                return p

        return ProtocolType.UNKNOWN

    def _create_event(
        self,
        timestamp: str,
        raw_msg: str,
        raw_proto: str = "",
        raw_dir: str = "INCOMING",
        metadata: dict[str, Any] | None = None,
    ) -> ReplayEvent:
        """Creates a validated ReplayEvent object."""
        if not timestamp or not str(timestamp).strip():
            raise ReplayParseError("Event timestamp cannot be empty.")

        msg_enum = ProtocolMessage.from_str(raw_msg)
        proto_enum = self._infer_protocol_type(msg_enum, raw_proto)
        dir_enum = MessageDirection.from_str(raw_dir)

        return ReplayEvent(
            timestamp=str(timestamp).strip(),
            protocol=proto_enum,
            message=msg_enum,
            direction=dir_enum,
            metadata=metadata or {},
        )

    def _parse_json(self, path: Path) -> list[ReplayEvent]:
        """Parses a JSON protocol log file."""
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as exc:
                raise ReplayParseError(
                    f"Invalid JSON syntax in '{path}': {exc.msg}"
                ) from exc

        events_data: list[Any] = []
        if isinstance(data, list):
            events_data = data
        elif isinstance(data, dict):
            events_data = data.get("events", data.get("messages", data.get("logs", [])))

        if not isinstance(events_data, list) or len(events_data) == 0:
            raise ReplayParseError(
                f"JSON protocol log '{path}' contains no events list."
            )

        events: list[ReplayEvent] = []
        for idx, item in enumerate(events_data, start=1):
            if not isinstance(item, dict):
                raise ReplayParseError(
                    f"Event #{idx} in '{path}' must be a JSON object."
                )

            ts = item.get("timestamp", f"00:00:{idx:02d}")
            msg = item.get("message", item.get("event", item.get("name", "")))
            proto = item.get("protocol", item.get("layer", ""))
            direction = item.get("direction", "INCOMING")
            meta = item.get("metadata", {})

            if not msg:
                raise ReplayParseError(
                    f"Event #{idx} missing required 'message' field."
                )

            events.append(
                self._create_event(str(ts), str(msg), str(proto), str(direction), meta)
            )

        return events

    def _parse_csv(self, path: Path) -> list[ReplayEvent]:
        """Parses a CSV protocol log file."""
        events: list[ReplayEvent] = []
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ReplayParseError(
                    f"CSV file '{path}' is empty or missing headers."
                )

            for idx, row in enumerate(reader, start=1):
                ts = row.get("timestamp", f"00:00:{idx:02d}")
                msg = row.get("message", row.get("event", ""))
                proto = row.get("protocol", row.get("layer", ""))
                direction = row.get("direction", "INCOMING")

                if not msg:
                    raise ReplayParseError(
                        f"CSV line #{idx} missing required 'message' column."
                    )

                events.append(
                    self._create_event(str(ts), str(msg), str(proto), str(direction))
                )

        if not events:
            raise ReplayParseError(f"CSV log file '{path}' contains zero event rows.")

        return events

    def _parse_text(self, path: Path) -> list[ReplayEvent]:
        """Parses a Plain Text protocol log file line by line."""
        events: list[ReplayEvent] = []
        with open(path, encoding="utf-8") as f:
            lines = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]

        if not lines:
            raise ReplayParseError(f"Text log file '{path}' is empty.")

        for idx, line in enumerate(lines, start=1):
            parts = line.split()
            if len(parts) == 1:
                events.append(self._create_event(f"00:00:{idx:02d}", parts[0]))
            elif len(parts) == 2:
                events.append(self._create_event(parts[0], parts[1]))
            elif len(parts) >= 3:
                events.append(self._create_event(parts[0], parts[1], parts[2]))

        return events
