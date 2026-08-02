"""Centralized configuration system for QualTest framework.

Provides immutable settings dataclass and environment variable parsing logic.
"""

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_LOG_MAX_BYTES: int = 10_485_760  # 10MB
DEFAULT_LOG_BACKUP_COUNT: int = 5


@dataclass(frozen=True)
class Settings:
    """Immutable configuration container for QualTest v2 framework.

    Attributes:
        app_name: Application name identifier.
        version: Framework version string.
        environment: Execution environment string (e.g. development, production).
        base_dir: Root directory path of the project.
        logs_dir: Directory path for framework log output.
        reports_dir: Directory path for test report output.
        testcases_dir: Directory path containing JSON testcases.
        log_level: Logging level string.
        log_file_max_bytes: Maximum size of log file before rotation.
        log_file_backup_count: Number of rotated log backup files to retain.
    """

    app_name: str = "QualTest v2"
    version: str = "0.8.1"
    environment: str = "development"
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    logs_dir: Path = base_dir / "logs"
    reports_dir: Path = base_dir / "reports"
    testcases_dir: Path = base_dir / "testcases"
    log_level: str = "INFO"
    log_file_max_bytes: int = DEFAULT_LOG_MAX_BYTES
    log_file_backup_count: int = DEFAULT_LOG_BACKUP_COUNT

    _instance: "Settings | None" = None

    @classmethod
    def load_from_env(cls, env_path: str | Path | None = None) -> "Settings":
        """Factory method to construct Settings from environment variables.

        Args:
            env_path: Optional path override for project base directory.

        Returns:
            Settings: Instantiated Settings instance populated from environment.
        """
        if env_path is not None:
            base_dir = Path(env_path).resolve()
        else:
            base_dir = Path(
                os.getenv(
                    "QUALTEST_BASE_DIR",
                    str(Path(__file__).resolve().parent.parent.parent),
                )
            ).resolve()

        logs_dir = Path(
            os.getenv("QUALTEST_LOGS_DIR", str(base_dir / "logs"))
        ).resolve()
        reports_dir = Path(
            os.getenv("QUALTEST_REPORTS_DIR", str(base_dir / "reports"))
        ).resolve()
        testcases_dir = Path(
            os.getenv("QUALTEST_TESTCASES_DIR", str(base_dir / "testcases"))
        ).resolve()
        log_level = os.getenv("QUALTEST_LOG_LEVEL", "INFO").upper()

        try:
            max_bytes = int(
                os.getenv("QUALTEST_LOG_MAX_BYTES", str(DEFAULT_LOG_MAX_BYTES))
            )
        except ValueError:
            max_bytes = DEFAULT_LOG_MAX_BYTES

        try:
            backup_count = int(
                os.getenv("QUALTEST_LOG_BACKUP_COUNT", str(DEFAULT_LOG_BACKUP_COUNT))
            )
        except ValueError:
            backup_count = DEFAULT_LOG_BACKUP_COUNT

        return cls(
            app_name=os.getenv("QUALTEST_APP_NAME", "QualTest v2"),
            version=os.getenv("QUALTEST_VERSION", "0.8.1"),
            environment=os.getenv("QUALTEST_ENV", "development"),
            base_dir=base_dir,
            logs_dir=logs_dir,
            reports_dir=reports_dir,
            testcases_dir=testcases_dir,
            log_level=log_level,
            log_file_max_bytes=max_bytes,
            log_file_backup_count=backup_count,
        )


def get_settings() -> Settings:
    """Retrieves the active global configuration settings instance.

    Returns:
        Settings: Global immutable settings instance.
    """
    if Settings._instance is None:
        Settings._instance = Settings.load_from_env()
    return Settings._instance


def set_settings(settings: Settings) -> None:
    """Explicitly sets the active global settings instance."""
    Settings._instance = settings


def reset_settings() -> None:
    """Resets the active global settings instance to None."""
    Settings._instance = None
