import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.database import DB_PATH
from app.routers import auth, points, settings as settings_router, shares, subthemes, themes, users
from app.services.database_backup import backup_if_needed
from app.services.settings_store import load_settings

settings = get_settings()

# uvicorn configures its own "uvicorn"/"uvicorn.error" loggers but not the root logger, so
# without this, INFO-level messages from a plain getLogger("pointify") are silently dropped
# (root logger defaults to WARNING with no handler) rather than reaching the console — a no-op
# if something else already configured the root logger.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pointify")

ALEMBIC_INI_PATH = Path(__file__).resolve().parent.parent / "alembic.ini"
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Backups themselves are capped at one a day, so checking more often buys nothing but extra
# disk I/O — a long-running instance (e.g. Docker with restart: unless-stopped) still needs
# this, though, so a new day's backup doesn't depend on the process ever restarting.
BACKUP_CHECK_INTERVAL_SECONDS = 24 * 60 * 60


def _run_migrations() -> None:
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    command.upgrade(alembic_cfg, "head")


def _backup_check() -> None:
    app_settings = load_settings(DB_PATH)
    backup_if_needed(DB_PATH, logger, enabled=app_settings.auto_backup_enabled)


async def _periodic_backup_check() -> None:
    while True:
        await asyncio.sleep(BACKUP_CHECK_INTERVAL_SECONDS)
        _backup_check()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _backup_check()
    _run_migrations()
    task = asyncio.create_task(_periodic_backup_check())
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="Pointify", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="pointify_session",
    same_site="lax",
)

app.include_router(auth.router)
app.include_router(themes.router)
app.include_router(subthemes.router)
app.include_router(points.router)
app.include_router(shares.router)
app.include_router(users.router)
app.include_router(settings_router.router)

# Serves the built Angular SPA (copied into STATIC_DIR by the Dockerfile) when present.
# Registered last so it never shadows the /api/* routers above. In local dev without a
# built frontend, STATIC_DIR won't contain an index.html and this is skipped entirely —
# the Angular dev server + proxy handles routing instead.
if (STATIC_DIR / "index.html").is_file():

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")
