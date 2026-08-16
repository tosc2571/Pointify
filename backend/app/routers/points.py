from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_subtheme_access, require_user
from app.models import Point, SubTheme, User
from app.schemas.point import PointCreate, PointOut

router = APIRouter(prefix="/api/subthemes", tags=["points"])


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
