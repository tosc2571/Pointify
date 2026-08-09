import bcrypt
from sqlalchemy.orm import Session

from app.models import User

MAX_BCRYPT_LENGTH = 72  # bcrypt only processes the first 72 bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:MAX_BCRYPT_LENGTH]
    return bcrypt.checkpw(truncated, hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    truncated = password.encode("utf-8")[:MAX_BCRYPT_LENGTH]
    return bcrypt.hashpw(truncated, bcrypt.gensalt()).decode("utf-8")


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
