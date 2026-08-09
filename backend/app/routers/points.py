from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_user
from app.models import Point, SubTheme, User
from app.schemas.point import PointCreate, PointOut

router = APIRouter(prefix="/api/subthemes", tags=["points"])


@router.post("/{subtheme_id}/points", response_model=PointOut, status_code=201)
def create_point(
    subtheme_id: int,
    payload: PointCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    subtheme = db.query(SubTheme).filter(SubTheme.id == subtheme_id).first()
    if not subtheme:
        raise HTTPException(status_code=404, detail="Subtheme not found")
    point = Point(
        subtheme_id=subtheme_id,
        user_id=user.id,
        type=payload.type,
        text=payload.text,
        rating=payload.rating,
    )
    db.add(point)
    db.commit()
    db.refresh(point)
    return point
