from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    username = request.session.get("user")
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user
