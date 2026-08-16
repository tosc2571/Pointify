"""Persists small app-level settings as a JSON file next to the database — deliberately not a
database table, so the auto-backup toggle can be read before database_backup.backup_if_needed
touches the SQLite file for the first time (see app/main.py).
"""

from pathlib import Path

from pydantic import BaseModel


class AppSettings(BaseModel):
    auto_backup_enabled: bool = True


def _settings_path(db_path: str) -> Path:
    return Path(db_path).resolve().parent / "settings.json"


def load_settings(db_path: str) -> AppSettings:
    path = _settings_path(db_path)
    if not path.is_file():
        return AppSettings()
    try:
        return AppSettings.model_validate_json(path.read_text())
    except ValueError:
        return AppSettings()


def save_settings(db_path: str, settings: AppSettings) -> None:
    _settings_path(db_path).write_text(settings.model_dump_json())
