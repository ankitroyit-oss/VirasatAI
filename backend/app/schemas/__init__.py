"""Pydantic v2 validation and serialization schemas."""

from app.schemas.monument import (
    MonumentBase,
    MonumentCreate,
    MonumentRead,
    MonumentSummary,
    MonumentUpdate,
    GeoJSONFeature,
    GeoJSONFeatureCollection
)
from app.schemas.review import (
    ReviewBase,
    ReviewCreate,
    ReviewRead,
    RatingStats
)
from app.schemas.spatial import (
    SpatialNearbyQuery,
    NearbyMonumentResult,
    ProximityAlertRequest,
    ProximityAlertResponse,
    ARVectorTelemetryRequest,
    ARVectorTelemetryResponse
)

__all__ = [
    "MonumentBase",
    "MonumentCreate",
    "MonumentRead",
    "MonumentSummary",
    "MonumentUpdate",
    "GeoJSONFeature",
    "GeoJSONFeatureCollection",
    "ReviewBase",
    "ReviewCreate",
    "ReviewRead",
    "RatingStats",
    "SpatialNearbyQuery",
    "NearbyMonumentResult",
    "ProximityAlertRequest",
    "ProximityAlertResponse",
    "ARVectorTelemetryRequest",
    "ARVectorTelemetryResponse",
]
