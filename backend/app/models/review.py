"""Visitor Feedback and Star Rating SQLAlchemy Model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Review(Base):
    """Personal feedback and 1-5 star review for a monument."""
    
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    monument_id: Mapped[str] = mapped_column(String(64), ForeignKey("monuments.id", ondelete="CASCADE"), index=True)
    
    author: Mapped[str] = mapped_column(String(128), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5 stars
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visit_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Many-to-one relationship with monument
    monument = relationship("Monument", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, monument='{self.monument_id}', rating={self.rating})>"
