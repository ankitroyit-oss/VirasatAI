"""Health and PostGIS extension status endpoint."""

import time
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/health", summary="System Health & PostGIS Status")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check database connection and verify PostGIS spatial extension availability."""
    start_time = time.time()
    db_status = "connected"
    postgis_version = None
    
    try:
        # Check database connection
        await db.execute(text("SELECT 1;"))
        
        # Check PostGIS extension
        try:
            result = await db.execute(text("SELECT postgis_full_version();"))
            postgis_version = result.scalar()
        except Exception:
            try:
                result = await db.execute(text("SELECT postgis_version();"))
                postgis_version = result.scalar()
            except Exception:
                postgis_version = "PostGIS extension not enabled or simulated mode"
                
    except Exception as e:
        db_status = f"error: {str(e)}"

    latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "healthy" if "error" not in db_status else "degraded",
        "database": db_status,
        "postgis_version": postgis_version,
        "latency_ms": latency_ms,
        "service": "VirasatAI High-Performance Asynchronous Spatial Engine"
    }
