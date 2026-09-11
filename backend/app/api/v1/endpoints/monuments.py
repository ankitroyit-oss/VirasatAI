"""Monument Resource Endpoints."""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_monument import monument_crud
from app.crud.crud_review import review_crud
from app.models.monument import Monument
from app.schemas.monument import MonumentCreate, MonumentRead, MonumentSummary, MonumentUpdate

router = APIRouter()


@router.get("/", response_model=List[MonumentSummary], summary="List and filter monuments")
async def list_monuments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category (monument, fort, temple, cave, etc.)"),
    state: Optional[str] = Query(None, description="Filter by Indian state"),
    unesco_only: Optional[bool] = Query(None, description="Filter by UNESCO status"),
    search: Optional[str] = Query(None, description="Search term in name, city, or state"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve monuments with flexible filtering, search, and pagination."""
    monuments, _ = await monument_crud.get_multi(
        db,
        skip=skip,
        limit=limit,
        category=category,
        state=state,
        unesco_only=unesco_only,
        search=search
    )
    
    # Enrich summary with rating averages
    summaries = []
    for m in monuments:
        stats = await review_crud.get_rating_stats(db, monument_id=m.id)
        s = MonumentSummary(
            id=m.id,
            name=m.name,
            name_hindi=m.name_hindi,
            image=m.image,
            category=m.category,
            period=m.period,
            unesco=m.unesco,
            city=m.city,
            state=m.state,
            latitude=m.latitude,
            longitude=m.longitude,
            emoji=m.emoji,
            rating=stats.average,
            total_reviews=stats.total
        )
        summaries.append(s)

    return summaries


@router.get("/categories", summary="Get all available heritage categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Return distinct categories across all monuments."""
    stmt = select(Monument.category, func.count(Monument.id)).group_by(Monument.category)
    results = (await db.execute(stmt)).all()
    return [{"category": cat, "count": count} for cat, count in results]


@router.get("/states", summary="Get all states with heritage sites")
async def get_states(db: AsyncSession = Depends(get_db)):
    """Return list of Indian states with their monument counts."""
    stmt = select(Monument.state, func.count(Monument.id)).group_by(Monument.state).order_by(Monument.state.asc())
    results = (await db.execute(stmt)).all()
    return [{"state": state, "monument_count": count} for state, count in results]


@router.get("/{monument_id}", response_model=MonumentRead, summary="Get full monument details")
async def get_monument(monument_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch complete verified metadata, history, architecture, stories, and visitor reviews for a monument."""
    monument = await monument_crud.get_by_id(db, monument_id)
    if not monument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monument with ID '{monument_id}' not found."
        )

    # Compute rating stats
    stats = await review_crud.get_rating_stats(db, monument_id=monument_id)
    
    # Construct response
    data = MonumentRead.model_validate(monument)
    data.rating_stats = stats
    return data


@router.post("/", response_model=MonumentRead, status_code=status.HTTP_201_CREATED, summary="Create a new monument")
async def create_monument(obj_in: MonumentCreate, db: AsyncSession = Depends(get_db)):
    """Create new monument with automatic PostGIS spatial point geometry generation."""
    existing = await monument_crud.get_by_id(db, obj_in.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Monument with ID '{obj_in.id}' already exists."
        )
    monument = await monument_crud.create(db, obj_in=obj_in)
    return monument


@router.put("/{monument_id}", response_model=MonumentRead, summary="Update monument metadata")
async def update_monument(
    monument_id: str, obj_in: MonumentUpdate, db: AsyncSession = Depends(get_db)
):
    """Update monument metadata and recalculate spatial geometry if coordinates change."""
    monument = await monument_crud.get_by_id(db, monument_id)
    if not monument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monument with ID '{monument_id}' not found."
        )
    updated = await monument_crud.update(db, db_obj=monument, obj_in=obj_in)
    return updated


@router.delete("/{monument_id}", summary="Delete monument")
async def delete_monument(monument_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a monument and its associated reviews."""
    monument = await monument_crud.delete(db, monument_id=monument_id)
    if not monument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monument with ID '{monument_id}' not found."
        )
    return {"message": f"Monument '{monument_id}' deleted successfully."}
