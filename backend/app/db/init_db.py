"""Database Initialization and Seeding Script."""

import asyncio
import logging
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.monument import Monument
from app.models.review import Review
from app.db.seed_data import get_seed_monuments, SAMPLE_REVIEWS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_postgis_extension(session: AsyncSession) -> None:
    """Ensure PostGIS extension is enabled in PostgreSQL."""
    try:
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        await session.commit()
        logger.info("PostGIS extension enabled or already active.")
    except Exception as e:
        logger.warning(f"Could not enable PostGIS extension (might already exist or permission restricted): {e}")
        await session.rollback()


async def seed_monuments(session: AsyncSession) -> None:
    """Seed initial verified monument records with PostGIS Point geometries."""
    result = await session.execute(select(Monument).limit(1))
    existing = result.scalar_one_or_none()
    
    if existing:
        logger.info("Monuments already exist in database. Skipping seed.")
        return

    monuments_data = get_seed_monuments()
    logger.info(f"Seeding {len(monuments_data)} monuments into PostGIS database...")

    for data in monuments_data:
        lat = data["latitude"]
        lng = data["longitude"]
        # WGS 84 SRID 4326 Point: (Longitude, Latitude)
        geom_wkt = f"SRID=4326;POINT({lng} {lat})"
        
        monument = Monument(
            id=data["id"],
            name=data["name"],
            name_hindi=data.get("name_hindi"),
            image=data.get("image"),
            category=data.get("category", "monument"),
            period=data.get("period"),
            unesco=data.get("unesco", False),
            city=data.get("city"),
            state=data.get("state"),
            latitude=lat,
            longitude=lng,
            geom=geom_wkt,
            significance=data.get("significance"),
            history=data.get("history"),
            architecture=data.get("architecture"),
            emoji=data.get("emoji", "🏛️"),
            color=data.get("color", "#FF6B35"),
            visit_info=data.get("visit_info"),
            cuisine=data.get("cuisine"),
            stories=data.get("stories"),
            fun_facts=data.get("fun_facts"),
            festivals=data.get("festivals"),
            tags=data.get("tags")
        )
        session.add(monument)

    await session.commit()
    logger.info(f"Successfully seeded {len(monuments_data)} monuments with spatial geometries.")


async def seed_reviews(session: AsyncSession) -> None:
    """Seed sample visitor reviews."""
    result = await session.execute(select(Review).limit(1))
    if result.scalar_one_or_none():
        return

    for rev in SAMPLE_REVIEWS:
        review_obj = Review(**rev)
        session.add(review_obj)

    await session.commit()
    logger.info(f"Seeded {len(SAMPLE_REVIEWS)} sample reviews.")


async def init_database() -> None:
    """Main database initialization orchestration."""
    logger.info("Connecting to database and creating tables...")
    
    async with engine.begin() as conn:
        # Create PostGIS extension if possible
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        except Exception as e:
            logger.info(f"Notice during extension check: {e}")
            
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("All database tables created successfully.")

    async with AsyncSessionLocal() as session:
        await seed_monuments(session)
        await seed_reviews(session)

    logger.info("Database initialization and seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(init_database())
