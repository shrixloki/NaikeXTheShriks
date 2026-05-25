from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import HelpPoiType
from app.domain.models import HelpPoi


async def get_pois_by_type(
    db: AsyncSession,
    poi_type: HelpPoiType | None = None,
    limit: int = 50,
) -> list[HelpPoi]:
    """Retrieve POIs from database optionally filtered by HelpPoiType."""
    stmt = select(HelpPoi)
    if poi_type:
        stmt = stmt.where(HelpPoi.type == poi_type)
    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def create_poi(db: AsyncSession, poi: HelpPoi) -> HelpPoi:
    """Create and persist a new POI location in the database."""
    db.add(poi)
    await db.commit()
    await db.refresh(poi)
    return poi
