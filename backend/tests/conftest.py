import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_db, get_db_path
from app.main import app
from app.models import Base


@pytest.fixture()
def db_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/test.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session, tmp_path):
    def override_get_db():
        yield db_session

    def override_get_db_path() -> str:
        return str(tmp_path / "test.db")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_path] = override_get_db_path
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
