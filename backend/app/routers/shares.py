from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_theme_owner
from app.models import Theme, ThemeShare, User
from app.schemas.share import ShareCreate, ShareOut

router = APIRouter(prefix="/api/themes", tags=["shares"])


@router.get("/{theme_id}/shares", response_model=list[ShareOut])
def list_shares(theme: Theme = Depends(require_theme_owner), db: Session = Depends(get_db)):
    shares = db.query(ThemeShare).filter(ThemeShare.theme_id == theme.id).all()
    return [ShareOut(user_id=s.user_id, username=s.user.username) for s in shares]


@router.post("/{theme_id}/shares", response_model=ShareOut, status_code=201)
def create_share(
    payload: ShareCreate,
    theme: Theme = Depends(require_theme_owner),
    db: Session = Depends(get_db),
):
    target = db.query(User).filter(User.username == payload.username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == theme.owner_id:
        raise HTTPException(status_code=400, detail="Theme owner already has access")
    existing = (
        db.query(ThemeShare)
        .filter(ThemeShare.theme_id == theme.id, ThemeShare.user_id == target.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already shared with this user")
    share = ThemeShare(theme_id=theme.id, user_id=target.id)
    db.add(share)
    db.commit()
    return ShareOut(user_id=target.id, username=target.username)


@router.delete("/{theme_id}/shares/{user_id}", status_code=204)
def delete_share(
    user_id: int,
    theme: Theme = Depends(require_theme_owner),
    db: Session = Depends(get_db),
):
    share = (
        db.query(ThemeShare)
        .filter(ThemeShare.theme_id == theme.id, ThemeShare.user_id == user_id)
        .first()
    )
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    db.delete(share)
    db.commit()
