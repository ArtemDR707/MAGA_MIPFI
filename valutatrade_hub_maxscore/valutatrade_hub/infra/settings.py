"""Settings loader (singleton) for project config."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings."""

    data_dir: Path
    log_dir: Path
    ttl_seconds: int
    json_logs: bool


class SettingsLoader:
    """Singleton loader to keep settings consistent across layers."""

    _instance: "SettingsLoader | None" = None

    def __new__(cls) -> "SettingsLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = None
        return cls._instance

    def load(self, project_root: Path) -> Settings:
        """Load settings from .env or defaults and cache them."""
        if self._settings is not None:
            return self._settings

        load_dotenv(project_root / ".env")

        data_dir = Path(os.getenv("VTH_DATA_DIR", project_root / "data"))
        log_dir = Path(os.getenv("VTH_LOG_DIR", project_root / "logs"))
        ttl_seconds = int(os.getenv("VTH_TTL_SECONDS", "3600"))
        json_logs = os.getenv("VTH_JSON_LOGS", "0") == "1"

        self._settings = Settings(
            data_dir=data_dir,
            log_dir=log_dir,
            ttl_seconds=ttl_seconds,
            json_logs=json_logs,
        )
        return self._settings

    @property
    def ttl_seconds(self) -> int:
        if self._settings is None:
            raise RuntimeError("Settings are not loaded.")
        return self._settings.ttl_seconds
