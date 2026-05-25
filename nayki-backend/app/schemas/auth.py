
from pydantic import BaseModel

from app.schemas.users import UserProfile


class SessionRequest(BaseModel):
    id_token: str | None = None
    dev_token: str | None = None


class SessionMetadata(BaseModel):
    session_id: str
    expires_at: str
    env: str
    dev_mode_active: bool


class SessionResponse(BaseModel):
    user: UserProfile
    session_metadata: SessionMetadata
