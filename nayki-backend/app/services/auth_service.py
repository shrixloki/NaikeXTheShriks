from datetime import UTC, datetime, timedelta

from app.config import settings
from app.domain.models import User
from app.schemas.auth import SessionMetadata, SessionResponse


def create_session_response(user: User) -> SessionResponse:
    """Generate session metadata and format the profile response upon successful login."""
    # Set session to expire in 24 hours
    expires_at = (datetime.now(UTC) + timedelta(hours=24)).isoformat()

    metadata = SessionMetadata(
        session_id=f"sess_{user.id.hex}",
        expires_at=expires_at,
        env=settings.APP_ENV,
        dev_mode_active=bool(settings.DEV_AUTH_ENABLED and settings.APP_ENV == "local"),
    )

    return SessionResponse(
        user=user,
        session_metadata=metadata,
    )
