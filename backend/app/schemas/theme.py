from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.subtheme import SubThemeWithPoints


class ThemeCreate(BaseModel):
    title: str


class ThemeUpdate(BaseModel):
    title: str | None = None
    notes: str | None = None


class ThemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    owner_id: int


class ThemeStats(BaseModel):
    total_points: int
    avg_rating: float
    pro_count: int
    contra_count: int


class ThemeDetailOut(ThemeOut):
    stats: ThemeStats
    subthemes: list[SubThemeWithPoints]
    notes: str
