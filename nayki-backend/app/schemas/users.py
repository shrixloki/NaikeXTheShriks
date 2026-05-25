import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    id: uuid.UUID
    firebase_uid: str | None = None
    phone: str | None = None
    email: str | None = None
    display_name: str | None = None
    trust_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    phone: str | None = Field(None, description="User's phone number")
    email: EmailStr | None = Field(None, description="User's email address")
    display_name: str | None = Field(None, max_length=100, description="Display name")


class EmergencyContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=5, max_length=20)
    relationship: str | None = Field(None, max_length=50)


class EmergencyContactUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, min_length=5, max_length=20)
    relationship: str | None = Field(None, max_length=50)
    is_verified: bool | None = None


class EmergencyContactResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    phone: str
    relationship: str | None = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceCreate(BaseModel):
    fcm_token: str = Field(..., min_length=10)
    platform: str = Field(..., description="e.g. android, ios")
    device_model: str | None = Field(None, max_length=100)
    app_version: str | None = Field(None, max_length=50)


class DeviceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    fcm_token: str
    platform: str
    device_model: str | None = None
    app_version: str | None = None
    last_seen_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
