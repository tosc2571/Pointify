from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import PointType


class PointCreate(BaseModel):
    type: PointType
    text: str
    rating: int = Field(ge=1, le=5)


class PointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subtheme_id: int
    user_id: int
    type: PointType
    text: str
    rating: int
    created_at: datetime
