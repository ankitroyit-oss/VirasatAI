"""Monument SQLAlchemy Model with GeoAlchemy2 PostGIS Point Geometry."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, Column, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.core.database import Base


class Monument(Base):
    """Heritage Monument entity with verified metadata and spatial PostGIS Point geometry."""
    
    __tablename__ = "monuments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name_hindi: Mapped[str] = mapped_column(String(255), nullable=True)
    image: Mapped[str] = mapped_column(String(1024), nullable=True)
    
    # Category & Historic Metadata
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(128), nullable=True)
    unesco: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Geographic location
    city: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    
    # PostGIS Spatial Geometry (WGS 84, SRID 4326 Point: (Longitude, Latitude))
    geom = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=True
    )

    # Narrative, Architecture & Storytelling
    significance: Mapped[str] = mapped_column(Text, nullable=True)
    history: Mapped[str] = mapped_column(Text, nullable=True)
    architecture: Mapped[str] = mapped_column(Text, nullable=True)
    emoji: Mapped[Optional[str]] = mapped_column(String(16), default="🏛️")
    color: Mapped[Optional[str]] = mapped_column(String(32), default="#FF6B35")

    # Rich Cultural JSON payloads (Supported natively in PostgreSQL)
    visit_info = mapped_column(JSONB, nullable=True, default=dict)
    cuisine = mapped_column(JSONB, nullable=True, default=list)
    artisans = mapped_column(JSONB, nullable=True, default=list)
    stories = mapped_column(JSONB, nullable=True, default=list)
    fun_facts = mapped_column(JSONB, nullable=True, default=list)
    festivals = mapped_column(JSONB, nullable=True, default=list)
    tags = mapped_column(JSONB, nullable=True, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-many relationship with visitor reviews
    reviews = relationship("Review", back_populates="monument", cascade="all, delete-orphan", lazy="selectin")

    # Compound spatial & filtering indexes
    __table_args__ = (
        Index("ix_monuments_state_category", "state", "category"),
        Index("ix_monuments_coords", "latitude", "longitude"),
    )

    def __repr__(self) -> str:
        return f"<Monument(id='{self.id}', name='{self.name}', state='{self.state}')>"
