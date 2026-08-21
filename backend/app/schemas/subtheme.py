from pydantic import BaseModel, ConfigDict

from app.schemas.point import PointOut


class SubThemeCreate(BaseModel):
    title: str


class SubThemeUpdate(BaseModel):
    title: str


class SubThemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    theme_id: int


class SubThemeWithPoints(SubThemeOut):
    points: list[PointOut]
