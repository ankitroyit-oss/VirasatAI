"""Review CRUD and Star Rating Aggregation operations."""

from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.schemas.review import RatingStats, ReviewCreate


class CRUDReview:
    async def create(self, db: AsyncSession, *, monument_id: str, obj_in: ReviewCreate) -> Review:
        """Create a new visitor review for a monument."""
        db_obj = Review(
            monument_id=monument_id,
            author=obj_in.author,
            rating=obj_in.rating,
            text=obj_in.text,
            visit_date=obj_in.visit_date
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_monument(
        self, db: AsyncSession, *, monument_id: str, skip: int = 0, limit: int = 50
    ) -> List[Review]:
        """Fetch reviews for a specific monument ordered by latest."""
        stmt = (
            select(Review)
            .where(Review.monument_id == monument_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_rating_stats(self, db: AsyncSession, *, monument_id: str) -> RatingStats:
        """Aggregate ratings to compute average, total, and star breakdown."""
        # Total and Average
        stmt = select(
            func.count(Review.id).label("total"),
            func.avg(Review.rating).label("average")
        ).where(Review.monument_id == monument_id)
        
        row = (await db.execute(stmt)).one()
        total = row.total or 0
        avg_val = round(float(row.average), 2) if row.average else 5.0

        # Distribution count per star rating (1 to 5)
        dist_stmt = (
            select(Review.rating, func.count(Review.id))
            .where(Review.monument_id == monument_id)
            .group_by(Review.rating)
        )
        dist_rows = (await db.execute(dist_stmt)).all()
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating_val, count in dist_rows:
            if rating_val in distribution:
                distribution[rating_val] = count

        return RatingStats(
            average=avg_val,
            total=total,
            distribution=distribution
        )


review_crud = CRUDReview()
