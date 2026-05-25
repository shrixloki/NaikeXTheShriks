import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import SosAlertStatus
from app.domain.models import SosAlert, SosRecipient


async def create_sos_alert(db: AsyncSession, alert: SosAlert) -> SosAlert:
    """Create and persist a new active SOS alert."""
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def get_sos_alert_by_id(
    db: AsyncSession, alert_id: uuid.UUID
) -> SosAlert | None:
    """Retrieve an SOS alert by its ID."""
    stmt = select(SosAlert).where(SosAlert.id == alert_id)
    res = await db.execute(stmt)
    return res.scalars().first()


async def update_sos_alert(db: AsyncSession, alert: SosAlert) -> SosAlert:
    """Save updates (cancel/expire/mark-safe) for an SOS alert."""
    await db.commit()
    await db.refresh(alert)
    return alert


async def create_sos_recipient(
    db: AsyncSession, recipient: SosRecipient
) -> SosRecipient:
    """Persist an SOS propagation target recipient."""
    db.add(recipient)
    await db.commit()
    await db.refresh(recipient)
    return recipient


async def get_sos_recipient(
    db: AsyncSession, alert_id: uuid.UUID, recipient_user_id: uuid.UUID
) -> SosRecipient | None:
    """Look up an SOS recipient track record."""
    stmt = select(SosRecipient).where(
        SosRecipient.sos_alert_id == alert_id,
        SosRecipient.recipient_user_id == recipient_user_id,
    )
    res = await db.execute(stmt)
    return res.scalars().first()


async def update_sos_recipient(
    db: AsyncSession, recipient: SosRecipient
) -> SosRecipient:
    """Update delivery or response values on an SOS recipient trace."""
    await db.commit()
    await db.refresh(recipient)
    return recipient


async def get_active_sos_alerts(db: AsyncSession) -> list[SosAlert]:
    """Find all currently active SOS alerts."""
    stmt = (
        select(SosAlert)
        .where(SosAlert.status == SosAlertStatus.ACTIVE)
        .order_by(SosAlert.triggered_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())
