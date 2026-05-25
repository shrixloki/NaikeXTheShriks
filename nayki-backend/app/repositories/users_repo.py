import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import EmergencyContact, User


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Retrieve user by their primary key UUID."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    return result.scalars().first()


async def get_user_by_firebase_uid(
    db: AsyncSession, firebase_uid: str
) -> User | None:
    """Retrieve user by their Firebase Unique Identifier."""
    result = await db.execute(
        select(User).where(
            User.firebase_uid == firebase_uid, User.deleted_at.is_(None)
        )
    )
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    firebase_uid: str | None = None,
    email: str | None = None,
    display_name: str | None = None,
    phone: str | None = None,
) -> User:
    """Create a new user in the database."""
    user = User(
        firebase_uid=firebase_uid,
        email=email,
        display_name=display_name,
        phone=phone,
        trust_score=0.5,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, update_data: dict) -> User:
    """Update user fields."""
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


# Emergency Contact Operations
async def get_emergency_contacts(
    db: AsyncSession, user_id: uuid.UUID
) -> list[EmergencyContact]:
    """Retrieve all emergency contacts for a given user."""
    result = await db.execute(
        select(EmergencyContact).where(EmergencyContact.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_emergency_contact_by_id(
    db: AsyncSession, contact_id: uuid.UUID, user_id: uuid.UUID
) -> EmergencyContact | None:
    """Retrieve a single emergency contact by id and user_id to ensure ownership."""
    result = await db.execute(
        select(EmergencyContact).where(
            EmergencyContact.id == contact_id,
            EmergencyContact.user_id == user_id,
        )
    )
    return result.scalars().first()


async def create_emergency_contact(
    db: AsyncSession, user_id: uuid.UUID, contact_data: dict
) -> EmergencyContact:
    """Create a new emergency contact for a user."""
    contact = EmergencyContact(user_id=user_id, **contact_data)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_emergency_contact(
    db: AsyncSession, contact: EmergencyContact, update_data: dict
) -> EmergencyContact:
    """Update emergency contact fields."""
    for key, value in update_data.items():
        if hasattr(contact, key):
            setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_emergency_contact(
    db: AsyncSession, contact: EmergencyContact
) -> None:
    """Remove emergency contact from database."""
    await db.delete(contact)
    await db.commit()
