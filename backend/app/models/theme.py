from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Theme(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User")
    subthemes = relationship("SubTheme", back_populates="theme", cascade="all, delete-orphan")
    shares = relationship("ThemeShare", back_populates="theme", cascade="all, delete-orphan")
