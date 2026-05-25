import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.models import User
from app.repositories import devices_repo, users_repo
from app.schemas.users import (
    DeviceCreate,
    DeviceResponse,
    EmergencyContactCreate,
    EmergencyContactResponse,
    EmergencyContactUpdate,
    UserProfile,
    UserUpdate,
)
from app.security.dependencies import get_current_user

router = APIRouter()


# --- User Profile Endpoints ---
@router.get("", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    """Retrieve the current user's profile information."""
    return current_user


@router.put("", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update the current user's profile details."""
    update_data = payload.model_dump(exclude_unset=True)
    return await users_repo.update_user(db, current_user, update_data)


# --- Emergency Contacts Endpoints ---
@router.get(
    "/emergency-contacts",
    response_model=list[EmergencyContactResponse],
    status_code=status.HTTP_200_OK,
)
async def list_emergency_contacts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    """Retrieve the current user's list of registered emergency contacts."""
    return await users_repo.get_emergency_contacts(db, current_user.id)


@router.post(
    "/emergency-contacts",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_emergency_contact(
    payload: EmergencyContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmergencyContactResponse:
    """Create and register a new emergency contact for the user."""
    contact_data = payload.model_dump()
    return await users_repo.create_emergency_contact(
        db, current_user.id, contact_data
    )


@router.put(
    "/emergency-contacts/{contact_id}",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_200_OK,
)
async def modify_emergency_contact(
    contact_id: uuid.UUID,
    payload: EmergencyContactUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmergencyContactResponse:
    """Update an existing emergency contact's details."""
    contact = await users_repo.get_emergency_contact_by_id(
        db, contact_id, current_user.id
    )
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    return await users_repo.update_emergency_contact(db, contact, update_data)


@router.delete(
    "/emergency-contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_emergency_contact(
    contact_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a registered emergency contact."""
    contact = await users_repo.get_emergency_contact_by_id(
        db, contact_id, current_user.id
    )
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found.",
        )

    await users_repo.delete_emergency_contact(db, contact)


# --- Devices Endpoints ---
@router.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_device(
    payload: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    """Register or update a push notification token (FCM token) for the user's active device."""
    device_data = payload.model_dump()
    return await devices_repo.create_device(db, current_user.id, device_data)


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_device(
    device_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Unregister/delete a user's device and push token."""
    device = await devices_repo.get_device_by_id(db, device_id, current_user.id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    await devices_repo.delete_device(db, device)
