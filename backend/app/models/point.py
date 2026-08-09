import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class PointType(str, enum.Enum):
    PRO = "pro"
    CONTRA = "contra"


class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    subtheme_id = Column(Integer, ForeignKey("subthemes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(PointType))
    text = Column(String)
    rating = Column(Integer)  # 1-5
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="points")
    subtheme = relationship("SubTheme", back_populates="points")
