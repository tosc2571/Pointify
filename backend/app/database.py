from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Filesystem path of the SQLite file, resolved from the SQLAlchemy URL — used by the backup
# service and settings store, which operate on the file directly rather than through a session.
DB_PATH = make_url(settings.database_url).database
