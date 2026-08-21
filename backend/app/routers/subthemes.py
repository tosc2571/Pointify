from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_theme_access
from app.models import SubTheme, Theme
from app.schemas.subtheme import SubThemeCreate, SubThemeOut, SubThemeUpdate

router = APIRouter(prefix="/api/themes", tags=["subthemes"])


def _get_subtheme_or_404(theme: Theme, subtheme_id: int, db: Session) -> SubTheme:
    subtheme = db.query(SubTheme).filter(SubTheme.id == subtheme_id, SubTheme.theme_id == theme.id).first()
    if not subtheme:
        raise HTTPException(status_code=404, detail="Subtheme not found")
    return subtheme


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


@router.patch("/{theme_id}/subthemes/{subtheme_id}", response_model=SubThemeOut)
def update_subtheme(
    subtheme_id: int,
    payload: SubThemeUpdate,
    theme: Theme = Depends(require_theme_access),
    db: Session = Depends(get_db),
):
    subtheme = _get_subtheme_or_404(theme, subtheme_id, db)
    subtheme.title = payload.title
    db.commit()
    db.refresh(subtheme)
    return subtheme


@router.delete("/{theme_id}/subthemes/{subtheme_id}", status_code=204)
def delete_subtheme(
    subtheme_id: int,
    theme: Theme = Depends(require_theme_access),
    db: Session = Depends(get_db),
):
    subtheme = _get_subtheme_or_404(theme, subtheme_id, db)
    db.delete(subtheme)
    db.commit()
