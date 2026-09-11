"""PostGIS Spatial and AR Telemetry Pydantic v2 Schemas."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class SpatialNearbyQuery(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="User or observer latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="User or observer longitude")
    radius_meters: float = Field(25000.0, ge=10.0, le=1000000.0, description="Search radius in meters (default 25km)")
    category: Optional[str] = Field(None, description="Optional category filter (monument, fort, temple, etc.)")
    limit: int = Field(10, ge=1, le=100, description="Max results to return")


class NearbyMonumentResult(BaseModel):
    id: str
    name: str
    name_hindi: Optional[str] = None
    emoji: Optional[str] = None
    image: Optional[str] = None
    city: str
    state: str
    latitude: float
    longitude: float
    distance_meters: float = Field(..., description="Exact geodesic distance in meters")
    distance_km: float = Field(..., description="Distance formatted in kilometers")
    bearing_degrees: float = Field(..., description="Forward azimuth bearing from user to site (0-360°)")
    relative_direction: str = Field(..., description="Human-friendly direction (e.g. '↑ Straight Ahead', '→ Turn Right')")


class ProximityAlertRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    accuracy_meters: Optional[float] = Field(10.0, ge=0.0)
    speed_mps: Optional[float] = Field(0.0, ge=0.0, description="Speed in meters per second")
    heading_deg: Optional[float] = Field(None, ge=0.0, le=360.0, description="Direction of travel")


class ProximityAlertItem(BaseModel):
    monument_id: str
    name: str
    name_hindi: Optional[str] = None
    emoji: str
    image: Optional[str] = None
    city: str
    tier: Literal["alert", "warning", "nearby"] = Field(
        ...,
        description="'alert' (<500m), 'warning' (<2km), 'nearby' (<10km)"
    )
    distance_meters: float
    distance_formatted: str
    bearing_degrees: float
    relative_direction: str
    eta_seconds: Optional[int] = Field(None, description="Estimated time of arrival at current speed")
    notification_title: str
    notification_body: str


class ProximityAlertResponse(BaseModel):
    user_latitude: float
    user_longitude: float
    speed_kmh: float
    has_active_alerts: bool
    alerts: List[ProximityAlertItem]
    closest_monument: Optional[NearbyMonumentResult] = None


class ARVectorTelemetryRequest(BaseModel):
    user_latitude: float = Field(..., ge=-90.0, le=90.0)
    user_longitude: float = Field(..., ge=-180.0, le=180.0)
    device_heading: float = Field(..., ge=0.0, le=360.0, description="Device compass heading (degrees from North)")
    camera_fov_horizontal: float = Field(65.0, ge=10.0, le=160.0, description="Camera horizontal field of view in degrees")
    target_monument_id: Optional[str] = Field(None, description="Specific target ID, or None for closest")


class ARVectorTelemetryResponse(BaseModel):
    target_id: str
    target_name: str
    target_latitude: float
    target_longitude: float
    distance_meters: float
    distance_formatted: str
    bearing_degrees: float
    relative_bearing: float = Field(..., description="Angle difference from device heading (-180° to +180°)")
    is_in_camera_fov: bool = Field(..., description="True if target monument is within camera viewfinder frame")
    direction_arrow: str
    direction_label: str
