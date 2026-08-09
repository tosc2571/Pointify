from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.database import engine
from app.models import Base
from app.routers import auth, points, subthemes, themes, users

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO(phase 3): replace with Alembic-managed migrations applied on startup.
    Base.metadata.create_all(bind=engine)
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
