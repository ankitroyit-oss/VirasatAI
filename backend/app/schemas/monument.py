"""Monument and GeoJSON Pydantic v2 Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.review import RatingStats, ReviewRead


class LocationCoordinates(BaseModel):
    state: str
    city: str
    coordinates: List[float] = Field(..., min_length=2, max_length=2, description="[latitude, longitude]")


class MonumentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    name_hindi: Optional[str] = None
    image: Optional[str] = None
    category: str = Field(..., max_length=64, description="monument, fort, temple, cave, stepwell, etc.")
    period: Optional[str] = None
    unesco: bool = False
    city: str = Field(..., max_length=128)
    state: str = Field(..., max_length=128)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    significance: Optional[str] = None
    history: Optional[str] = None
    architecture: Optional[str] = None
    emoji: Optional[str] = "🏛️"
    color: Optional[str] = "#FF6B35"
    visit_info: Optional[Dict[str, Any]] = None
    cuisine: Optional[List[Dict[str, Any]]] = None
    artisans: Optional[List[Dict[str, Any]]] = None
    stories: Optional[List[str]] = None
    fun_facts: Optional[List[str]] = None
    festivals: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class MonumentCreate(MonumentBase):
    id: str = Field(..., min_length=2, max_length=64, description="Unique slug identifier (e.g. 'taj-mahal')")


class MonumentUpdate(BaseModel):
    name: Optional[str] = None
    name_hindi: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None
    period: Optional[str] = None
    unesco: Optional[bool] = None
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    significance: Optional[str] = None
    history: Optional[str] = None
    architecture: Optional[str] = None
    emoji: Optional[str] = None
    color: Optional[str] = None
    visit_info: Optional[Dict[str, Any]] = None
    cuisine: Optional[List[Dict[str, Any]]] = None
    artisans: Optional[List[Dict[str, Any]]] = None
    stories: Optional[List[str]] = None
    fun_facts: Optional[List[str]] = None
    festivals: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class MonumentSummary(BaseModel):
    id: str
    name: str
    name_hindi: Optional[str] = None
    image: Optional[str] = None
    category: str
    period: Optional[str] = None
    unesco: bool
    city: str
    state: str
    latitude: float
    longitude: float
    emoji: Optional[str] = None
    rating: Optional[float] = 5.0
    total_reviews: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class MonumentRead(MonumentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    reviews: List[ReviewRead] = []
    rating_stats: Optional[RatingStats] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== GEOJSON SCHEMAS (RFC 7946) ====================

class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    id: str
    geometry: GeoJSONGeometry
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
