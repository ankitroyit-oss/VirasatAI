"""AR Camera Vector Telemetry & Spatial Occlusion Endpoints."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_monument import monument_crud
from app.schemas.spatial import ARVectorTelemetryRequest, ARVectorTelemetryResponse

router = APIRouter()


@router.post("/telemetry", response_model=ARVectorTelemetryResponse, summary="Compute AR Camera Telemetry Vector")
async def calculate_ar_telemetry(
    req: ARVectorTelemetryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AR Viewfinder Camera Telemetry & Occlusion Analysis:
    Calculates the exact angular displacement between the mobile device's camera orientation
    (compass heading) and the target monument's geodesic coordinates.

    - Determines whether the heritage site is within the device camera's horizontal FOV.
    - Generates dynamic guidance arrows (↑, ↗, →, ↘, ↙, ←, ↖) for real-time AR HUD overlay.
    - If `target_monument_id` is omitted, automatically locks onto the closest heritage site.
    """
    target = None
    if req.target_monument_id:
        target = await monument_crud.get_by_id(db, req.target_monument_id)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Monument with ID '{req.target_monument_id}' not found."
            )
    else:
        # Fallback to closest monument within 100km
        closest_list = await monument_crud.get_nearby_spatial(
            db,
            lat=req.user_latitude,
            lng=req.user_longitude,
            radius_meters=100000.0,
            limit=1
        )
        if closest_list:
            target = await monument_crud.get_by_id(db, closest_list[0].id)

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No monument found within search radius for AR telemetry."
        )

    # 1. Geodesic distance in meters
    dist_m = monument_crud.haversine_distance(
        req.user_latitude, req.user_longitude,
        target.latitude, target.longitude
    )

    # 2. Forward bearing from observer to target (0-360°)
    bearing = monument_crud.forward_azimuth(
        req.user_latitude, req.user_longitude,
        target.latitude, target.longitude
    )

    # 3. Relative bearing difference (-180° to +180°)
    diff = (bearing - req.device_heading) % 360.0
    if diff > 180.0:
        diff -= 360.0

    # 4. Field-of-View test
    half_fov = req.camera_fov_horizontal / 2.0
    is_in_fov = abs(diff) <= half_fov

    # 5. Determine direction arrows & directional guidance text
    if is_in_fov:
        arrow = "🎯"
        label = f"In Viewfinder ({int(abs(diff))}° offset)"
    elif diff > 0:
        if diff <= 45.0:
            arrow = "↗"
            label = f"Pan Right {int(diff)}°"
        elif diff <= 135.0:
            arrow = "→"
            label = f"Turn Right {int(diff)}°"
        else:
            arrow = "↘"
            label = f"Turn Around Right {int(diff)}°"
    else:
        abs_diff = abs(diff)
        if abs_diff <= 45.0:
            arrow = "↖"
            label = f"Pan Left {int(abs_diff)}°"
        elif abs_diff <= 135.0:
            arrow = "←"
            label = f"Turn Left {int(abs_diff)}°"
        else:
            arrow = "↙"
            label = f"Turn Around Left {int(abs_diff)}°"

    dist_formatted = f"{int(dist_m)} m" if dist_m < 1000 else f"{round(dist_m / 1000.0, 1)} km"

    return ARVectorTelemetryResponse(
        target_id=target.id,
        target_name=target.name,
        target_latitude=target.latitude,
        target_longitude=target.longitude,
        distance_meters=round(dist_m, 1),
        distance_formatted=dist_formatted,
        bearing_degrees=round(bearing, 1),
        relative_bearing=round(diff, 1),
        is_in_camera_fov=is_in_fov,
        direction_arrow=arrow,
        direction_label=label
    )
