from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers import auth, points, subthemes, themes, users

settings = get_settings()

ALEMBIC_INI_PATH = Path(__file__).resolve().parent.parent / "alembic.ini"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def _run_migrations() -> None:
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_migrations()
    yield


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
app.include_router(users.router)

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
