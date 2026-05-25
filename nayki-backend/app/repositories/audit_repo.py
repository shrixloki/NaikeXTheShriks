import hashlib
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import AuditLog


def hash_ip(ip_address: str | None) -> str | None:
    """Securely hash an IP address using SHA-256."""
    if not ip_address:
        return None
    # We strip any whitespace and hash the IP address
    return hashlib.sha256(ip_address.strip().encode("utf-8")).hexdigest()


async def create_audit_log(
    db: AsyncSession,
    action: str,
    entity_type: str,
    actor_user_id: uuid.UUID | None = None,
    entity_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    """Create a securely anonymized audit log in the database."""
    ip_hash = hash_ip(ip_address)
    log = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_hash=ip_hash,
        metadata=metadata or {},
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log
