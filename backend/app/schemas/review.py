"""Review Pydantic v2 Schemas."""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class ReviewBase(BaseModel):
    author: str = Field(..., min_length=2, max_length=128, description="Reviewer name or pseudonym")
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    text: Optional[str] = Field(None, max_length=2000, description="Optional visitor review text")
    visit_date: Optional[str] = Field(None, max_length=32, description="Date or season of visit")


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: int
    monument_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RatingStats(BaseModel):
    average: float = Field(0.0, description="Average visitor rating (e.g. 4.8)")
    total: int = Field(0, description="Total number of reviews submitted")
    distribution: Dict[int, int] = Field(
        default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        description="Rating count per star tier"
    )
