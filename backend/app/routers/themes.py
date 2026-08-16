from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_user
from app.models import PointType, Theme, User
from app.schemas.subtheme import SubThemeWithPoints
from app.schemas.theme import ThemeCreate, ThemeDetailOut, ThemeOut, ThemeStats

router = APIRouter(prefix="/api/themes", tags=["themes"])


@router.get("", response_model=list[ThemeOut])
def list_themes(db: Session = Depends(get_db), user: User = Depends(require_user)):
    return db.query(Theme).all()


@router.post("", response_model=ThemeOut, status_code=201)
def create_theme(payload: ThemeCreate, db: Session = Depends(get_db), user: User = Depends(require_user)):
    theme = Theme(title=payload.title)
    db.add(theme)
    db.commit()
    db.refresh(theme)
    return theme


@router.get("/{theme_id}", response_model=ThemeDetailOut)
def get_theme(theme_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    all_points = [p for st in theme.subthemes for p in st.points]

    def avg_rating(points_list):
        if not points_list:
            return 0
        return round(sum(p.rating for p in points_list) / len(points_list), 1)

    stats = ThemeStats(
        total_points=len(all_points),
        avg_rating=avg_rating(all_points),
        pro_count=len([p for p in all_points if p.type == PointType.PRO]),
        contra_count=len([p for p in all_points if p.type == PointType.CONTRA]),
    )
    return ThemeDetailOut(
        id=theme.id,
        title=theme.title,
        created_at=theme.created_at,
        stats=stats,
        subthemes=[SubThemeWithPoints.model_validate(st) for st in theme.subthemes],
    )
