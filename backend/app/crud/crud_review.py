"""Review CRUD and Star Rating Aggregation operations with resilient in-memory fallback."""

from datetime import datetime, timezone
import logging
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.schemas.review import RatingStats, ReviewCreate

logger = logging.getLogger(__name__)


class CRUDReview:
    def __init__(self):
        self._memory_reviews: List[Review] = []
        self._next_id = 1
        self._load_memory_cache()

    def _load_memory_cache(self):
        """Preload sample reviews into memory."""
        try:
            from app.db.seed_data import SAMPLE_REVIEWS
            now = datetime.now(timezone.utc)
            for rev in SAMPLE_REVIEWS:
                r = Review(
                    id=self._next_id,
                    monument_id=rev["monument_id"],
                    author=rev["author"],
                    rating=rev["rating"],
                    text=rev.get("text", ""),
                    visit_date=rev.get("visit_date", "2025-02"),
                    created_at=now
                )
                self._memory_reviews.append(r)
                self._next_id += 1
            logger.info(f"Loaded {len(self._memory_reviews)} reviews into in-memory review cache.")
        except Exception as e:
            logger.warning(f"Could not preload in-memory reviews: {e}")

    async def create(self, db: Optional[AsyncSession], *, monument_id: str, obj_in: ReviewCreate) -> Review:
        """Create a new visitor review for a monument."""
        now = datetime.now(timezone.utc)
        db_obj = Review(
            id=self._next_id,
            monument_id=monument_id,
            author=obj_in.author,
            rating=obj_in.rating,
            text=obj_in.text,
            visit_date=obj_in.visit_date,
            created_at=now
        )
        self._next_id += 1
        self._memory_reviews.append(db_obj)

        if db is not None:
            try:
                db.add(db_obj)
                await db.flush()
                await db.refresh(db_obj)
            except Exception:
                pass
        return db_obj

    async def get_multi_by_monument(
        self, db: Optional[AsyncSession], *, monument_id: str, skip: int = 0, limit: int = 50
    ) -> List[Review]:
        """Fetch reviews for a specific monument ordered by latest."""
        if db is not None:
            try:
                stmt = (
                    select(Review)
                    .where(Review.monument_id == monument_id)
                    .order_by(Review.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                )
                result = await db.execute(stmt)
                return list(result.scalars().all())
            except Exception:
                pass

        matching = [r for r in self._memory_reviews if r.monument_id == monument_id]
        matching.sort(key=lambda r: r.created_at or datetime.min, reverse=True)
        return matching[skip:skip + limit]

    async def get_rating_stats(self, db: Optional[AsyncSession], *, monument_id: str) -> RatingStats:
        """Aggregate ratings to compute average, total, and star breakdown."""
        if db is not None:
            try:
                stmt = select(
                    func.count(Review.id).label("total"),
                    func.avg(Review.rating).label("average")
                ).where(Review.monument_id == monument_id)
                row = (await db.execute(stmt)).one()
                total = row.total or 0
                avg_val = round(float(row.average), 2) if row.average else 5.0

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
            except Exception:
                pass

        matching = [r for r in self._memory_reviews if r.monument_id == monument_id]
        total = len(matching)
        if total == 0:
            return RatingStats(average=4.9, total=0, distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0})

        avg_val = round(sum(r.rating for r in matching) / total, 2)
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in matching:
            if r.rating in distribution:
                distribution[r.rating] += 1

        return RatingStats(
            average=avg_val,
            total=total,
            distribution=distribution
        )


review_crud = CRUDReview()
