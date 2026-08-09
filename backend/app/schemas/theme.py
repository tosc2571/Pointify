from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ThemeCreate(BaseModel):
    title: str


class ThemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime


class ThemeStats(BaseModel):
    total_points: int
    avg_rating: float
    pro_count: int
    contra_count: int


class ThemeDetailOut(ThemeOut):
    stats: ThemeStats
