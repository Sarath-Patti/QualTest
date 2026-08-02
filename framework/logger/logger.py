"""Thread-safe singleton logging subsystem for QualTest v2 framework.

Provides centralized logger initialization supporting concurrent access,
console output, rotating file output, and configurable log levels.
"""

import logging
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

from framework.config.settings import Settings, get_settings


class FrameworkLogger:
    """Singleton thread-safe logger manager for QualTest v2.

    Initializes and manages root/module loggers ensuring single initialization of
    console and rotating file handlers across multiple threads.
    """

    _instance: "FrameworkLogger | None" = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "FrameworkLogger":
        """Thread-safe singleton instance instantiation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        settings: Settings | None = None,
        log_level: str | None = None,
        log_file_name: str = "qualtest.log",
    ) -> None:
        """Initializes logging handlers and configuration.

        Thread-safe method to set up console and rotating file logging handlers.

        Args:
            settings: Custom Settings instance, or loads global default.
            log_level: Log level string override (DEBUG, INFO, WARNING, ERROR).
            log_file_name: Name of rotating log file.
        """
        with self._lock:
            if self._initialized:
                if log_level:
                    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
                    logging.getLogger("QualTest").setLevel(numeric_level)
                return

            cfg = settings or get_settings()
            target_level_str = log_level or cfg.log_level
            numeric_level = getattr(logging, target_level_str.upper(), logging.INFO)

            # Ensure logs directory exists
            cfg.logs_dir.mkdir(parents=True, exist_ok=True)
            log_filepath: Path = cfg.logs_dir / log_file_name

            # Setup root QualTest logger
            root_logger = logging.getLogger("QualTest")
            root_logger.setLevel(numeric_level)
            root_logger.propagate = False

            # Formatter with ISO-like timestamp and thread info
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] [%(threadName)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            # Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

            # Rotating File Handler
            file_handler = RotatingFileHandler(
                filename=log_filepath,
                maxBytes=cfg.log_file_max_bytes,
                backupCount=cfg.log_file_backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            self._initialized = True

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Retrieves a logger instance under the QualTest hierarchy.

        Args:
            name: Sub-module or class name. If None, returns root QualTest logger.

        Returns:
            logging.Logger: Configured logger instance.
        """
        if not self._initialized:
            self.initialize()

        if not name or name == "QualTest":
            return logging.getLogger("QualTest")

        if name.startswith("QualTest."):
            return logging.getLogger(name)

        return logging.getLogger(f"QualTest.{name}")


def setup_logger(
    settings: Settings | None = None,
    log_level: str | None = None,
    log_file_name: str = "qualtest.log",
) -> None:
    """Helper function to initialize framework logging singleton.

    Args:
        settings: Optional Settings instance.
        log_level: Optional log level string.
        log_file_name: Optional log file name.
    """
    logger_manager = FrameworkLogger()
    logger_manager.initialize(
        settings=settings, log_level=log_level, log_file_name=log_file_name
    )


def get_logger(name: str | None = None) -> logging.Logger:
    """Public helper function to obtain a configured logger.

    Args:
        name: Name of module or logger domain.

    Returns:
        logging.Logger: Thread-safe configured logger.
    """
    logger_manager = FrameworkLogger()
    return logger_manager.get_logger(name)
