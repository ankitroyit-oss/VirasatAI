"""Visitor Reviews and Star Ratings Endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_monument import monument_crud
from app.crud.crud_review import review_crud
from app.schemas.review import RatingStats, ReviewCreate, ReviewRead

router = APIRouter()


@router.get(
    "/monuments/{monument_id}/reviews",
    response_model=List[ReviewRead],
    summary="List reviews for a monument"
)
async def list_monument_reviews(
    monument_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve visitor reviews for a specific monument, ordered from latest to oldest."""
    monument = await monument_crud.get_by_id(db, monument_id)
    if not monument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monument with ID '{monument_id}' not found."
        )
    return await review_crud.get_multi_by_monument(db, monument_id=monument_id, skip=skip, limit=limit)


@router.post(
    "/monuments/{monument_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a visitor review and rating"
)
async def create_monument_review(
    monument_id: str,
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a visitor review and 1-5 star rating for a monument.
    Updates the monument's aggregated rating in real-time.
    """
    monument = await monument_crud.get_by_id(db, monument_id)
    if not monument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monument with ID '{monument_id}' not found."
        )

    review = await review_crud.create(db, monument_id=monument_id, obj_in=review_in)
    await db.commit()
    await db.refresh(review)
    return review


@router.get(
    "/monuments/{monument_id}/ratings",
    response_model=RatingStats,
    summary="Get aggregated rating stats for a monument"
)
async def get_monument_ratings(
    monument_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated rating statistics for a monument:
    - Average star rating (1.0 to 5.0)
    - Total review count
    - Distribution breakdown per star rating (1 to 5)
    """
    monument = await monument_crud.get_by_id(db, monument_id)
    if not monument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monument with ID '{monument_id}' not found."
        )
    return await review_crud.get_rating_stats(db, monument_id=monument_id)
