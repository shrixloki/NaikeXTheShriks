import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.logging import logger

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Verifies that the API service, PostgreSQL, and Redis databases are running correctly."""
    db_status = "unhealthy"
    redis_status = "unhealthy"

    # 1. Verify PostgreSQL Database connectivity
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))

    # 2. Verify Redis connectivity
    try:
        client = aioredis.from_url(settings.REDIS_URL, socket_timeout=2.0)
        await client.ping()
        await client.close()
        redis_status = "healthy"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))

    # Determine overall status
    overall = "healthy"
    if db_status != "healthy" or redis_status != "healthy":
        overall = "degraded"

    return {
        "status": overall,
        "database": db_status,
        "redis": redis_status,
    }
