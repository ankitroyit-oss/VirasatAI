"""Monument CRUD with PostGIS Spatial Geodesic Queries."""

import math
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, select, desc, cast, Float
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography, Geometry
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_MakePoint, ST_SetSRID, ST_Azimuth

from app.models.monument import Monument
from app.schemas.monument import MonumentCreate, MonumentUpdate
from app.schemas.spatial import NearbyMonumentResult


class CRUDMonument:
    @staticmethod
    def calculate_relative_direction(bearing: float, heading: Optional[float]) -> str:
        """Derive cardinal relative direction given bearing and observer heading."""
        if heading is None:
            # Fallback to cardinal direction of bearing
            dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
            return f"Heading {dirs[int(round(bearing / 22.5)) % 16]}"
        
        diff = ((bearing - heading) + 360) % 360
        if diff <= 22.5 or diff > 337.5:
            return "↑ Straight Ahead"
        elif diff <= 67.5:
            return "↗ Slight Right"
        elif diff <= 112.5:
            return "→ Turn Right"
        elif diff <= 157.5:
            return "↘ Behind Right"
        elif diff <= 202.5:
            return "↓ Behind You"
        elif diff <= 247.5:
            return "↙ Behind Left"
        elif diff <= 292.5:
            return "← Turn Left"
        else:
            return "↖ Slight Left"

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Geodesic distance in meters using the Haversine formula."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
        return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    @staticmethod
    def forward_azimuth(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate forward bearing from point 1 to point 2 in degrees (0-360°)."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lambda = math.radians(lon2 - lon1)
        y = math.sin(delta_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
        return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

    async def get_by_id(self, db: AsyncSession, monument_id: str) -> Optional[Monument]:
        """Fetch monument by primary slug ID."""
        stmt = select(Monument).where(Monument.id == monument_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        state: Optional[str] = None,
        unesco_only: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Monument], int]:
        """Query monuments with flexible filtering, search, and pagination."""
        stmt = select(Monument)
        
        if category:
            stmt = stmt.where(Monument.category == category.lower())
        if state:
            stmt = stmt.where(func.lower(Monument.state) == state.lower())
        if unesco_only is not None:
            stmt = stmt.where(Monument.unesco == unesco_only)
        if search:
            search_pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                func.lower(Monument.name).like(search_pattern) |
                func.lower(Monument.city).like(search_pattern) |
                func.lower(Monument.state).like(search_pattern)
            )

        # Total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await db.execute(count_stmt)).scalar() or 0

        # Paginated results
        stmt = stmt.order_by(Monument.name.asc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all()), total_count

    async def get_nearby_spatial(
        self,
        db: AsyncSession,
        *,
        lat: float,
        lng: float,
        radius_meters: float = 50000.0,
        limit: int = 10,
        category: Optional[str] = None,
        observer_heading: Optional[float] = None
    ) -> List[NearbyMonumentResult]:
        """
        High-performance PostGIS Spatial Query:
        Utilizes PostGIS ST_DWithin and ST_Distance on geography casting with spatial GiST indexing.
        Falls back to python spherical distance if PostGIS functions are unavailable in test DB.
        """
        user_point_geom = ST_SetSRID(ST_MakePoint(lng, lat), 4326)
        user_geog = cast(user_point_geom, Geography)

        try:
            # Query using PostGIS spatial geography functions
            dist_col = ST_Distance(cast(Monument.geom, Geography), user_geog).label("distance_m")
            stmt = (
                select(Monument, dist_col)
                .where(ST_DWithin(cast(Monument.geom, Geography), user_geog, radius_meters))
            )

            if category:
                stmt = stmt.where(Monument.category == category.lower())

            stmt = stmt.order_by(dist_col.asc()).limit(limit)
            results = (await db.execute(stmt)).all()

            output = []
            for mon, dist_meters in results:
                dist_m = float(dist_meters)
                bearing = self.forward_azimuth(lat, lng, mon.latitude, mon.longitude)
                output.append(
                    NearbyMonumentResult(
                        id=mon.id,
                        name=mon.name,
                        name_hindi=mon.name_hindi,
                        emoji=mon.emoji,
                        image=mon.image,
                        city=mon.city,
                        state=mon.state,
                        latitude=mon.latitude,
                        longitude=mon.longitude,
                        distance_meters=round(dist_m, 1),
                        distance_km=round(dist_m / 1000.0, 2),
                        bearing_degrees=round(bearing, 1),
                        relative_direction=self.calculate_relative_direction(bearing, observer_heading)
                    )
                )
            return output

        except Exception:
            # Fallback for environments where PostGIS extension is not installed
            stmt = select(Monument)
            if category:
                stmt = stmt.where(Monument.category == category.lower())
            all_monuments = (await db.execute(stmt)).scalars().all()

            computed = []
            for mon in all_monuments:
                dist_m = self.haversine_distance(lat, lng, mon.latitude, mon.longitude)
                if dist_m <= radius_meters:
                    bearing = self.forward_azimuth(lat, lng, mon.latitude, mon.longitude)
                    computed.append((mon, dist_m, bearing))

            computed.sort(key=lambda x: x[1])
            computed = computed[:limit]

            return [
                NearbyMonumentResult(
                    id=mon.id,
                    name=mon.name,
                    name_hindi=mon.name_hindi,
                    emoji=mon.emoji,
                    image=mon.image,
                    city=mon.city,
                    state=mon.state,
                    latitude=mon.latitude,
                    longitude=mon.longitude,
                    distance_meters=round(dist_m, 1),
                    distance_km=round(dist_m / 1000.0, 2),
                    bearing_degrees=round(bearing, 1),
                    relative_direction=self.calculate_relative_direction(bearing, observer_heading)
                )
                for mon, dist_m, bearing in computed
            ]

    async def create(self, db: AsyncSession, *, obj_in: MonumentCreate) -> Monument:
        """Create new monument with automatic PostGIS geometry population."""
        obj_in_data = obj_in.model_dump()
        
        # Construct PostGIS Point: (Longitude, Latitude) in SRID 4326
        lat = obj_in_data["latitude"]
        lng = obj_in_data["longitude"]
        point_geom = f"SRID=4326;POINT({lng} {lat})"
        
        db_obj = Monument(**obj_in_data, geom=point_geom)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Monument, obj_in: MonumentUpdate
    ) -> Monument:
        """Update existing monument attributes and geometry if coordinates change."""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if "latitude" in update_data or "longitude" in update_data:
            lat = update_data.get("latitude", db_obj.latitude)
            lng = update_data.get("longitude", db_obj.longitude)
            update_data["geom"] = f"SRID=4326;POINT({lng} {lat})"

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, monument_id: str) -> Optional[Monument]:
        """Delete monument by ID."""
        mon = await self.get_by_id(db, monument_id)
        if mon:
            await db.delete(mon)
            await db.flush()
        return mon


monument_crud = CRUDMonument()
