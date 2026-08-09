from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers import auth, points, subthemes, themes, users

settings = get_settings()

ALEMBIC_INI_PATH = Path(__file__).resolve().parent.parent / "alembic.ini"


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
