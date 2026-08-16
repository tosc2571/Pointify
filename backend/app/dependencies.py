from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import DB_PATH, SessionLocal
from app.models import SubTheme, Theme, ThemeShare, User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_path() -> str:
    return DB_PATH


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


def _has_theme_access(theme: Theme, user: User, db: Session) -> bool:
    if theme.owner_id == user.id:
        return True
    return (
        db.query(ThemeShare)
        .filter(ThemeShare.theme_id == theme.id, ThemeShare.user_id == user.id)
        .first()
        is not None
    )


def require_theme_access(theme_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)) -> Theme:
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme or not _has_theme_access(theme, user, db):
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme


def require_theme_owner(theme: Theme = Depends(require_theme_access), user: User = Depends(require_user)) -> Theme:
    if theme.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the owner can manage sharing")
    return theme


def require_subtheme_access(
    subtheme_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)
) -> SubTheme:
    subtheme = db.query(SubTheme).filter(SubTheme.id == subtheme_id).first()
    if not subtheme or not _has_theme_access(subtheme.theme, user, db):
        raise HTTPException(status_code=404, detail="Subtheme not found")
    return subtheme
