from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_theme_access
from app.models import SubTheme, Theme
from app.schemas.subtheme import SubThemeCreate, SubThemeOut

router = APIRouter(prefix="/api/themes", tags=["subthemes"])


@router.post("/{theme_id}/subthemes", response_model=SubThemeOut, status_code=201)
def create_subtheme(
    payload: SubThemeCreate,
    theme: Theme = Depends(require_theme_access),
    db: Session = Depends(get_db),
):
    subtheme = SubTheme(title=payload.title, theme_id=theme.id)
    db.add(subtheme)
    db.commit()
    db.refresh(subtheme)
    return subtheme
