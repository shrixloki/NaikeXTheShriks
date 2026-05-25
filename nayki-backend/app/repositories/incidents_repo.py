import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import IncidentReport


async def create_incident_report(
    db: AsyncSession, report: IncidentReport
) -> IncidentReport:
    """Persist a new incident report to the database."""
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_incident_report_by_id(
    db: AsyncSession, report_id: uuid.UUID
) -> IncidentReport | None:
    """Retrieve an incident report by its unique ID."""
    stmt = select(IncidentReport).where(IncidentReport.id == report_id)
    res = await db.execute(stmt)
    return res.scalars().first()


async def get_user_incident_reports(
    db: AsyncSession, user_id: uuid.UUID
) -> list[IncidentReport]:
    """Retrieve all reports submitted by a specific user."""
    stmt = (
        select(IncidentReport)
        .where(IncidentReport.user_id == user_id)
        .order_by(IncidentReport.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def update_incident_report(
    db: AsyncSession, report: IncidentReport
) -> IncidentReport:
    """Save changes made to an incident report."""
    await db.commit()
    await db.refresh(report)
    return report
