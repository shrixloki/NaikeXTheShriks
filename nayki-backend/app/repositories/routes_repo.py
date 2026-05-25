import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import RouteEvaluation


async def create_route_evaluation(
    db: AsyncSession, route_eval: RouteEvaluation
) -> RouteEvaluation:
    """Save a computed route evaluation comparison."""
    db.add(route_eval)
    await db.commit()
    await db.refresh(route_eval)
    return route_eval


async def get_route_evaluation_by_id(
    db: AsyncSession, eval_id: uuid.UUID
) -> RouteEvaluation | None:
    """Retrieve a previously calculated route evaluation by ID."""
    stmt = select(RouteEvaluation).where(RouteEvaluation.id == eval_id)
    res = await db.execute(stmt)
    return res.scalars().first()


async def get_user_route_evaluations(
    db: AsyncSession, user_id: uuid.UUID
) -> list[RouteEvaluation]:
    """Retrieve all route evaluations associated with a user profile."""
    stmt = (
        select(RouteEvaluation)
        .where(RouteEvaluation.user_id == user_id)
        .order_by(RouteEvaluation.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())
