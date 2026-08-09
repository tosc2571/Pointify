from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_user
from app.models import SubTheme, User
from app.schemas.subtheme import SubThemeCreate, SubThemeOut

router = APIRouter(prefix="/api/themes", tags=["subthemes"])


@router.post("/{theme_id}/subthemes", response_model=SubThemeOut, status_code=201)
def create_subtheme(
    theme_id: int,
    payload: SubThemeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    subtheme = SubTheme(title=payload.title, theme_id=theme_id)
    db.add(subtheme)
    db.commit()
    db.refresh(subtheme)
    return subtheme
