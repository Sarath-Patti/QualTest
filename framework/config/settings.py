"""Centralized configuration management for QualTest v2 framework.

Provides an immutable, dataclass-based configuration structure with
support for environment variable overrides and sensible default paths.
"""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

# Determine root directory of the project
ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Settings:
    """Immutable application settings dataclass.

    Attributes:
        app_name: Name of the application framework.
        version: Current framework version.
        environment: Current operating environment (e.g. development, production).
        base_dir: Absolute path to project root.
        logs_dir: Absolute path to logs directory.
        reports_dir: Absolute path to reports directory.
        testcases_dir: Absolute path to testcases directory.
        log_level: Configured logging level (e.g., DEBUG, INFO, WARNING, ERROR).
        log_file_max_bytes: Maximum log file size before rotation in bytes.
        log_file_backup_count: Number of rotating log backup files to retain.
    """

    app_name: str = "QualTest v2"
    version: str = "0.1.0"
    environment: str = "development"
    base_dir: Path = ROOT_DIR
    logs_dir: Path = ROOT_DIR / "logs"
    reports_dir: Path = ROOT_DIR / "reports"
    testcases_dir: Path = ROOT_DIR / "testcases"
    log_level: str = "INFO"
    log_file_max_bytes: int = 10 * 1024 * 1024  # 10 MB
    log_file_backup_count: int = 5

    @classmethod
    def load_from_env(cls, custom_root: Optional[Path] = None) -> "Settings":
        """Factory method to build Settings instance with environment variable overrides.

        Args:
            custom_root: Optional custom root path override.

        Returns:
            Settings: An initialized immutable Settings instance.
        """
        root = custom_root or ROOT_DIR

        # Environment variable overrides
        env_name = os.getenv("QUALTEST_ENV", "development")
        log_level = os.getenv("QUALTEST_LOG_LEVEL", "INFO").upper()

        logs_dir_str = os.getenv("QUALTEST_LOGS_DIR")
        logs_dir = Path(logs_dir_str).resolve() if logs_dir_str else root / "logs"

        reports_dir_str = os.getenv("QUALTEST_REPORTS_DIR")
        reports_dir = (
            Path(reports_dir_str).resolve() if reports_dir_str else root / "reports"
        )

        testcases_dir_str = os.getenv("QUALTEST_TESTCASES_DIR")
        testcases_dir = (
            Path(testcases_dir_str).resolve()
            if testcases_dir_str
            else root / "testcases"
        )

        try:
            max_bytes = int(
                os.getenv("QUALTEST_LOG_MAX_BYTES", str(10 * 1024 * 1024))
            )
        except ValueError:
            max_bytes = 10 * 1024 * 1024

        try:
            backup_count = int(os.getenv("QUALTEST_LOG_BACKUP_COUNT", "5"))
        except ValueError:
            backup_count = 5

        # Read version from VERSION file if present
        version_file = root / "VERSION"
        version_str = "0.1.0"
        if version_file.is_file():
            try:
                version_str = version_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass

        return cls(
            app_name="QualTest v2",
            version=version_str,
            environment=env_name,
            base_dir=root,
            logs_dir=logs_dir,
            reports_dir=reports_dir,
            testcases_dir=testcases_dir,
            log_level=log_level,
            log_file_max_bytes=max_bytes,
            log_file_backup_count=backup_count,
        )


_global_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Retrieves the active global configuration settings instance.

    Returns:
        Settings: Global immutable settings instance.
    """
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings.load_from_env()
    return _global_settings
