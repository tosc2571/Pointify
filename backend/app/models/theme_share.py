from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class ThemeShare(Base):
    __tablename__ = "theme_shares"
    __table_args__ = (UniqueConstraint("theme_id", "user_id", name="uq_theme_shares_theme_user"),)

    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    theme = relationship("Theme", back_populates="shares")
    user = relationship("User")
