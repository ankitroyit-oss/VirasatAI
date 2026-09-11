"""PostGIS Spatial Intelligence & Proximity Detection Endpoints."""

import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_monument import monument_crud
from app.models.monument import Monument
from app.schemas.monument import GeoJSONFeature, GeoJSONFeatureCollection, GeoJSONGeometry
from app.schemas.spatial import (
    NearbyMonumentResult,
    ProximityAlertItem,
    ProximityAlertRequest,
    ProximityAlertResponse
)

router = APIRouter()


@router.get("/nearby", response_model=List[NearbyMonumentResult], summary="Find nearby monuments via PostGIS")
async def get_nearby_monuments(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="User or center latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="User or center longitude"),
    radius_meters: float = Query(50000.0, ge=10.0, le=2000000.0, description="Search radius in meters (default 50km)"),
    limit: int = Query(10, ge=1, le=100, description="Max monuments to return"),
    category: Optional[str] = Query(None, description="Optional category filter (monument, fort, temple, etc.)"),
    heading: Optional[float] = Query(None, ge=0.0, le=360.0, description="Observer compass heading in degrees"),
    db: Optional[AsyncSession] = Depends(get_db)
):
    """
    High-Performance PostGIS Spatial Radius Query:
    Computes exact geodesic surface distances and azimuth forward bearings using PostGIS
    ST_DWithin and ST_Distance indexed with spatial GiST trees.
    """
    return await monument_crud.get_nearby_spatial(
        db,
        lat=latitude,
        lng=longitude,
        radius_meters=radius_meters,
        limit=limit,
        category=category,
        observer_heading=heading
    )


@router.post("/proximity-detect", response_model=ProximityAlertResponse, summary="Real-time proximity alert detector")
async def detect_proximity_alerts(
    req: ProximityAlertRequest,
    db: Optional[AsyncSession] = Depends(get_db)
):
    """
    Dynamic Proximity Engine for Live AR & Mobile Geolocation Streams:
    Evaluates user position against all heritage sites and generates tiered notifications:
    - 🔴 Alert (< 500m): 'Monument in Range!'
    - 🟡 Warning (< 2km): 'Approaching Monument'
    - 🔵 Nearby (< 10km): 'Nearby Heritage Site'
    Includes estimated time of arrival (ETA) based on streaming velocity.
    """
    nearby_sites = await monument_crud.get_nearby_spatial(
        db,
        lat=req.latitude,
        lng=req.longitude,
        radius_meters=10000.0,
        limit=10,
        observer_heading=req.heading_deg
    )

    alerts: List[ProximityAlertItem] = []
    speed_kmh = round(req.speed_mps * 3.6, 1)

    for item in nearby_sites:
        dist_m = item.distance_meters
        tier = None
        title = ""
        body = ""

        if dist_m <= 500:
            tier = "alert"
            title = f"Monument in Range: {item.name}"
            body = f"You are within {int(dist_m)} meters of {item.name}! Point your camera to explore in AR."
        elif dist_m <= 2000:
            tier = "warning"
            title = f"Approaching {item.name}"
            body = f"{item.name} is {round(dist_m / 1000.0, 1)} km away ({item.relative_direction})."
        elif dist_m <= 10000:
            tier = "nearby"
            title = f"Nearby Site: {item.name}"
            body = f"Located {round(dist_m / 1000.0, 1)} km away in {item.city}."

        if tier:
            eta_sec = None
            if req.speed_mps > 0.5:
                eta_sec = int(dist_m / req.speed_mps)

            dist_formatted = f"{int(dist_m)} m" if dist_m < 1000 else f"{round(dist_m / 1000.0, 1)} km"

            alerts.append(
                ProximityAlertItem(
                    monument_id=item.id,
                    name=item.name,
                    name_hindi=item.name_hindi,
                    emoji=item.emoji or "🏛️",
                    image=item.image,
                    city=item.city,
                    tier=tier,
                    distance_meters=dist_m,
                    distance_formatted=dist_formatted,
                    bearing_degrees=item.bearing_degrees,
                    relative_direction=item.relative_direction,
                    eta_seconds=eta_sec,
                    notification_title=title,
                    notification_body=body
                )
            )

    closest = nearby_sites[0] if nearby_sites else None

    return ProximityAlertResponse(
        user_latitude=req.latitude,
        user_longitude=req.longitude,
        speed_kmh=speed_kmh,
        has_active_alerts=len(alerts) > 0,
        alerts=alerts,
        closest_monument=closest
    )


@router.get("/geojson", response_model=GeoJSONFeatureCollection, summary="Get RFC 7946 GeoJSON FeatureCollection")
async def get_monuments_geojson(
    category: Optional[str] = Query(None, description="Optional category filter"),
    state: Optional[str] = Query(None, description="Optional state filter"),
    db: Optional[AsyncSession] = Depends(get_db)
):
    """
    Returns spatial GeoJSON FeatureCollection of monuments for direct rendering on
    Mapbox, Leaflet, Google Maps, or SVG cartography layers.
    """
    monuments = []
    if db is not None:
        try:
            stmt = select(Monument)
            if category:
                stmt = stmt.where(Monument.category == category.lower())
            if state:
                stmt = stmt.where(Monument.state.ilike(state))
            result = await db.execute(stmt)
            monuments = list(result.scalars().all())
        except Exception:
            pass

    if not monuments:
        monuments = list(monument_crud._memory_monuments.values())
        if category:
            monuments = [m for m in monuments if m.category and m.category.lower() == category.lower()]
        if state:
            monuments = [m for m in monuments if m.state and m.state.lower() == state.lower()]

    features = []
    for m in monuments:
        features.append(
            GeoJSONFeature(
                id=m.id,
                geometry=GeoJSONGeometry(
                    type="Point",
                    coordinates=[m.longitude, m.latitude]
                ),
                properties={
                    "id": m.id,
                    "name": m.name,
                    "name_hindi": m.name_hindi,
                    "category": m.category,
                    "city": m.city,
                    "state": m.state,
                    "unesco": m.unesco,
                    "period": m.period,
                    "emoji": m.emoji,
                    "image": m.image
                }
            )
        )

    return GeoJSONFeatureCollection(features=features)
