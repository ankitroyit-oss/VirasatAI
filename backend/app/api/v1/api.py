"""V1 API Router Aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import ar, health, monuments, reviews, spatial

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(monuments.router, prefix="/monuments", tags=["monuments"])
api_router.include_router(spatial.router, prefix="/spatial", tags=["spatial"])
api_router.include_router(ar.router, prefix="/ar", tags=["ar"])
api_router.include_router(reviews.router, tags=["reviews"])
