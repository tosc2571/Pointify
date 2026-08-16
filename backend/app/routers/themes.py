from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_theme_access, require_user
from app.models import PointType, Theme, ThemeShare, User
from app.schemas.subtheme import SubThemeWithPoints
from app.schemas.theme import ThemeCreate, ThemeDetailOut, ThemeOut, ThemeStats

router = APIRouter(prefix="/api/themes", tags=["themes"])


def _compute_stats(theme: Theme) -> ThemeStats:
    all_points = [p for st in theme.subthemes for p in st.points]

    def avg_rating(points_list):
        if not points_list:
            return 0
        return round(sum(p.rating for p in points_list) / len(points_list), 1)

    return ThemeStats(
        total_points=len(all_points),
        avg_rating=avg_rating(all_points),
        pro_count=len([p for p in all_points if p.type == PointType.PRO]),
        contra_count=len([p for p in all_points if p.type == PointType.CONTRA]),
    )


def _render_markdown(theme: Theme, stats: ThemeStats) -> str:
    lines = [f"# {theme.title}", ""]
    lines.append(
        f"**Stats:** {stats.total_points} points · avg rating {stats.avg_rating} · "
        f"{stats.pro_count} pro · {stats.contra_count} contra"
    )
    lines.append("")
    for subtheme in theme.subthemes:
        lines.append(f"## {subtheme.title}")
        lines.append("")
        if not subtheme.points:
            lines.append("_No points yet._")
        else:
            for point in subtheme.points:
                label = "Pro" if point.type == PointType.PRO else "Contra"
                lines.append(f"- **{label}** (★{point.rating}): {point.text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


@router.get("", response_model=list[ThemeOut])
def list_themes(db: Session = Depends(get_db), user: User = Depends(require_user)):
    shared_theme_ids = db.query(ThemeShare.theme_id).filter(ThemeShare.user_id == user.id)
    return (
        db.query(Theme)
        .filter(or_(Theme.owner_id == user.id, Theme.id.in_(shared_theme_ids)))
        .all()
    )


@router.post("", response_model=ThemeOut, status_code=201)
def create_theme(payload: ThemeCreate, db: Session = Depends(get_db), user: User = Depends(require_user)):
    theme = Theme(title=payload.title, owner_id=user.id)
    db.add(theme)
    db.commit()
    db.refresh(theme)
    return theme


@router.get("/{theme_id}", response_model=ThemeDetailOut)
def get_theme(theme: Theme = Depends(require_theme_access)):
    stats = _compute_stats(theme)
    return ThemeDetailOut(
        id=theme.id,
        title=theme.title,
        created_at=theme.created_at,
        owner_id=theme.owner_id,
        stats=stats,
        subthemes=[SubThemeWithPoints.model_validate(st) for st in theme.subthemes],
    )


@router.get("/{theme_id}/export")
def export_theme_markdown(theme: Theme = Depends(require_theme_access)):
    markdown = _render_markdown(theme, _compute_stats(theme))
    return Response(content=markdown, media_type="text/markdown; charset=utf-8")
