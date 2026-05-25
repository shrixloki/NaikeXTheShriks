import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import UserDevice


async def get_device_by_id(
    db: AsyncSession, device_id: uuid.UUID, user_id: uuid.UUID
) -> UserDevice | None:
    """Retrieve a device by its ID and verify it belongs to the user."""
    result = await db.execute(
        select(UserDevice).where(
            UserDevice.id == device_id, UserDevice.user_id == user_id
        )
    )
    return result.scalars().first()


async def get_devices_by_user_id(
    db: AsyncSession, user_id: uuid.UUID
) -> list[UserDevice]:
    """Retrieve all devices registered to a specific user."""
    result = await db.execute(
        select(UserDevice).where(UserDevice.user_id == user_id)
    )
    return list(result.scalars().all())


async def create_device(
    db: AsyncSession, user_id: uuid.UUID, device_data: dict
) -> UserDevice:
    """Register a new device for a user.

    If a device with the same FCM token exists for the user, update last_seen_at.
    """
    # Check if this token is already registered for this user
    fcm_token = device_data.get("fcm_token")
    result = await db.execute(
        select(UserDevice).where(
            UserDevice.user_id == user_id, UserDevice.fcm_token == fcm_token
        )
    )
    existing_device = result.scalars().first()

    if existing_device:
        for key, value in device_data.items():
            if hasattr(existing_device, key):
                setattr(existing_device, key, value)
        await db.commit()
        await db.refresh(existing_device)
        return existing_device

    device = UserDevice(user_id=user_id, **device_data)
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


async def delete_device(db: AsyncSession, device: UserDevice) -> None:
    """Unregister/delete a user's device."""
    await db.delete(device)
    await db.commit()
