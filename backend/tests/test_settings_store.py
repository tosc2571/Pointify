from app.services.settings_store import AppSettings, load_settings, save_settings


def test_load_no_settings_file_yet_returns_defaults(tmp_path):
    db_path = str(tmp_path / "pointify.db")

    settings = load_settings(db_path)

    assert settings.auto_backup_enabled is True


def test_save_then_load_round_trips_the_value(tmp_path):
    db_path = str(tmp_path / "pointify.db")
    save_settings(db_path, AppSettings(auto_backup_enabled=False))

    loaded = load_settings(db_path)

    assert loaded.auto_backup_enabled is False


def test_load_corrupt_settings_file_falls_back_to_defaults(tmp_path):
    db_path = str(tmp_path / "pointify.db")
    (tmp_path / "settings.json").write_text("{ not valid json")

    settings = load_settings(db_path)

    assert settings.auto_backup_enabled is True
