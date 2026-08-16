"""Copies the SQLite database to a dated file in a "backups" folder next to it — at most once
per calendar day (UTC), and only if the database actually changed since the last backup, so
an idle instance doesn't accumulate identical daily copies. Keeps only the most recent
MAX_BACKUPS; older ones are pruned automatically. Called once at startup (main.py, before the
database is touched by Alembic) and again periodically so a long-running process — e.g. a
Docker container that's never restarted — doesn't miss days.
"""

import shutil
from datetime import date as date_cls
from datetime import datetime, timezone
from logging import Logger
from pathlib import Path

MAX_BACKUPS = 10


def backup_if_needed(
    db_path: str, logger: Logger, today: date_cls | None = None, enabled: bool = True
) -> None:
    if not enabled:
        return

    source = Path(db_path)
    if not source.is_file():
        return  # fresh install — nothing to back up yet

    backup_date = today or datetime.now(timezone.utc).date()
    backups_dir = source.resolve().parent / "backups"
    backup_path = backups_dir / f"pointify-{backup_date:%Y-%m-%d}.db"

    if backup_path.exists():
        _prune(backups_dir, logger)  # already backed up today — still enforce retention
        return

    db_mtime = source.stat().st_mtime
    last_backed_up = _latest_backup_source_time(backups_dir)
    if last_backed_up is not None and db_mtime <= last_backed_up:
        _prune(backups_dir, logger)  # nothing changed since the last backup
        return

    try:
        backups_dir.mkdir(parents=True, exist_ok=True)
        # copy2 (unlike copy) preserves the source's mtime on the copy, so a later check can
        # tell whether the DB changed since *this* backup without a separate state file.
        shutil.copy2(source, backup_path)
        logger.info("Created daily database backup at %s", backup_path)
    except OSError:
        # A failed backup must never prevent the app from starting.
        logger.warning("Failed to create daily database backup at %s", backup_path, exc_info=True)
        return

    _prune(backups_dir, logger)


def _latest_backup_source_time(backups_dir: Path) -> float | None:
    if not backups_dir.is_dir():
        return None
    files = list(backups_dir.glob("pointify-*.db"))
    if not files:
        return None
    return max(f.stat().st_mtime for f in files)


def _prune(backups_dir: Path, logger: Logger) -> None:
    """Keeps only the MAX_BACKUPS most recently written backups; deletes the rest."""
    if not backups_dir.is_dir():
        return

    files = sorted(backups_dir.glob("pointify-*.db"), key=lambda f: f.stat().st_mtime, reverse=True)
    for stale in files[MAX_BACKUPS:]:
        try:
            stale.unlink()
            logger.info("Pruned old database backup %s", stale)
        except OSError:
            logger.warning("Failed to prune old database backup %s", stale, exc_info=True)
