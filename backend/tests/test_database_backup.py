import logging
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from app.services.database_backup import MAX_BACKUPS, backup_if_needed

logger = logging.getLogger(__name__)


def _backup_path(tmp_path: Path, d: date) -> Path:
    return tmp_path / "backups" / f"pointify-{d:%Y-%m-%d}.db"


def test_no_source_db_does_nothing(tmp_path):
    db_path = str(tmp_path / "pointify.db")

    backup_if_needed(db_path, logger, today=date(2026, 7, 20))

    assert not (tmp_path / "backups").exists()


def test_first_call_today_creates_dated_backup(tmp_path):
    db_path = tmp_path / "pointify.db"
    db_path.write_text("fake sqlite content")
    today = date(2026, 7, 20)

    backup_if_needed(str(db_path), logger, today=today)

    backup = _backup_path(tmp_path, today)
    assert backup.is_file()
    assert backup.read_text() == "fake sqlite content"


def test_second_call_same_day_does_not_overwrite_or_duplicate(tmp_path):
    db_path = tmp_path / "pointify.db"
    db_path.write_text("version 1")
    today = date(2026, 7, 20)
    backup_if_needed(str(db_path), logger, today=today)

    db_path.write_text("version 2 (later the same day)")
    backup_if_needed(str(db_path), logger, today=today)

    backup = _backup_path(tmp_path, today)
    assert backup.read_text() == "version 1"
    assert len(list((tmp_path / "backups").iterdir())) == 1


def test_disabled_does_nothing(tmp_path):
    db_path = tmp_path / "pointify.db"
    db_path.write_text("fake sqlite content")

    backup_if_needed(str(db_path), logger, today=date(2026, 7, 20), enabled=False)

    assert not (tmp_path / "backups").exists()


def test_next_day_creates_additional_backup(tmp_path):
    db_path = tmp_path / "pointify.db"
    db_path.write_text("day one")
    day1 = date(2026, 7, 20)
    backup_if_needed(str(db_path), logger, today=day1)

    # Explicit mtime bump, deliberately — two real writes this close together can land on the
    # same filesystem-reported mtime (seen on Windows/NTFS under pytest), which would make the
    # second backup_if_needed() call see "no change" and skip. Same reasoning as the pruning
    # test below.
    db_path.write_text("day two")
    bumped_mtime = db_path.stat().st_mtime + 5
    os.utime(db_path, (bumped_mtime, bumped_mtime))
    day2 = day1 + timedelta(days=1)
    backup_if_needed(str(db_path), logger, today=day2)

    assert _backup_path(tmp_path, day1).is_file()
    assert _backup_path(tmp_path, day2).is_file()
    assert len(list((tmp_path / "backups").iterdir())) == 2


def test_next_day_no_change_since_last_backup_skips_backup(tmp_path):
    db_path = tmp_path / "pointify.db"
    db_path.write_text("unchanged")
    day1 = date(2026, 7, 20)
    backup_if_needed(str(db_path), logger, today=day1)

    # No write to db_path happens here — the database is genuinely unchanged.
    day2 = day1 + timedelta(days=1)
    backup_if_needed(str(db_path), logger, today=day2)

    assert _backup_path(tmp_path, day1).is_file()
    assert not _backup_path(tmp_path, day2).is_file()
    assert len(list((tmp_path / "backups").iterdir())) == 1


def test_more_than_max_backups_prunes_oldest_keeping_most_recent(tmp_path):
    db_path = tmp_path / "pointify.db"
    db_path.write_text("content")
    today = date(2026, 7, 20)
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()

    # Simulate a backlog of 12 pre-existing backups (e.g. accumulated before automatic pruning
    # existed), with strictly increasing mtimes, oldest to newest — including today's, so
    # backup_if_needed takes the "already backed up today" prune-only path.
    base = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
    paths = []
    for i in range(12):
        d = today - timedelta(days=11 - i)
        path = backups_dir / f"pointify-{d:%Y-%m-%d}.db"
        path.write_text("backup")
        ts = base + i * 86400
        os.utime(path, (ts, ts))
        paths.append(path)

    backup_if_needed(str(db_path), logger, today=today)

    assert len(list(backups_dir.iterdir())) == MAX_BACKUPS
    assert not paths[0].exists()  # oldest two pruned
    assert not paths[1].exists()
    for path in paths[2:]:
        assert path.exists(), f"{path.name} (newer) should have been kept"
