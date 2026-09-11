"""FastAPI Main Application Entrypoint."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.db.init_db import init_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management: Database connection & initialization on startup."""
    logger.info("Initializing VirasatAI Spatial REST Engine...")
    try:
        await init_database()
        logger.info("Database and PostGIS spatial tables ready.")
    except Exception as e:
        logger.warning(f"Database startup check skipped or deferred: {e}")

    yield

    logger.info("Disposing database connection pool...")
    await engine.dispose()
    logger.info("Shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production-Grade Asynchronous REST Spatial Engine for Live Monument Exploration & AR Tourism.\n\n"
        "Powered by Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), GeoAlchemy2, and PostgreSQL with PostGIS.\n"
        "Features:\n"
        "- 🛰️ PostGIS GiST-indexed spatial queries (`ST_DWithin`, `ST_Distance`, `ST_Azimuth`)\n"
        "- 📍 Real-time dynamic proximity alert detector (<500m alert, <2km warning, <10km nearby)\n"
        "- 📱 AR Camera horizontal FOV occlusion vector & bearing calculation\n"
        "- ⭐ Visitor review and 1–5 star rating aggregation\n"
        "- 🗺️ RFC 7946 GeoJSON FeatureCollections for Mapbox & Leaflet"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS for seamless frontend web & mobile integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"], summary="API Root Status")
async def root():
    """Service metadata, health ping, and interactive documentation links."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": f"{settings.API_V1_STR}/openapi.json"
        },
        "endpoints": {
            "health": f"{settings.API_V1_STR}/health",
            "monuments": f"{settings.API_V1_STR}/monuments",
            "spatial_nearby": f"{settings.API_V1_STR}/spatial/nearby",
            "proximity_detect": f"{settings.API_V1_STR}/spatial/proximity-detect",
            "geojson": f"{settings.API_V1_STR}/spatial/geojson",
            "ar_telemetry": f"{settings.API_V1_STR}/ar/telemetry"
        }
    }


# Mount API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
