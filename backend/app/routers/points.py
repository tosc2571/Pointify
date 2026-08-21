from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_subtheme_access, require_user
from app.models import Point, SubTheme, User
from app.schemas.point import PointCreate, PointOut, PointUpdate

router = APIRouter(prefix="/api/subthemes", tags=["points"])


def _get_point_or_404(subtheme: SubTheme, point_id: int, db: Session) -> Point:
    point = db.query(Point).filter(Point.id == point_id, Point.subtheme_id == subtheme.id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    return point


@router.post("/{subtheme_id}/points", response_model=PointOut, status_code=201)
def create_point(
    payload: PointCreate,
    subtheme: SubTheme = Depends(require_subtheme_access),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    point = Point(
        subtheme_id=subtheme.id,
        user_id=user.id,
        type=payload.type,
        text=payload.text,
        rating=payload.rating,
    )
    db.add(point)
    db.commit()
    db.refresh(point)
    return point


@router.patch("/{subtheme_id}/points/{point_id}", response_model=PointOut)
def update_point(
    point_id: int,
    payload: PointUpdate,
    subtheme: SubTheme = Depends(require_subtheme_access),
    db: Session = Depends(get_db),
):
    point = _get_point_or_404(subtheme, point_id, db)
    point.type = payload.type
    point.text = payload.text
    point.rating = payload.rating
    db.commit()
    db.refresh(point)
    return point


@router.delete("/{subtheme_id}/points/{point_id}", status_code=204)
def delete_point(
    point_id: int,
    subtheme: SubTheme = Depends(require_subtheme_access),
    db: Session = Depends(get_db),
):
    point = _get_point_or_404(subtheme, point_id, db)
    db.delete(point)
    db.commit()
