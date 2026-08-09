from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class SubTheme(Base):
    __tablename__ = "subthemes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    theme_id = Column(Integer, ForeignKey("themes.id"))

    theme = relationship("Theme", back_populates="subthemes")
    points = relationship("Point", back_populates="subtheme", cascade="all, delete-orphan")
