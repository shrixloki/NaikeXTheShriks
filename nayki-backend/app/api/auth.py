from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.errors import UnauthorizedError
from app.repositories import users_repo
from app.schemas.auth import SessionRequest, SessionResponse
from app.security.firebase_auth import verify_firebase_token
from app.services import auth_service

router = APIRouter()


@router.post(
    "/session", response_model=SessionResponse, status_code=status.HTTP_200_OK
)
async def create_session(
    payload: SessionRequest, db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """Create a new backend session.

    Validates either a Firebase ID token or a dev_token (only in local dev mode).
    Creates a user database record if they are logging in for the first time.
    """
    token = payload.dev_token or payload.id_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either id_token or dev_token must be provided.",
        )

    try:
        claims = verify_firebase_token(token)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    firebase_uid = claims["uid"]

    # Check database for existing user
    user = await users_repo.get_user_by_firebase_uid(db, firebase_uid)

    if not user:
        # Provision user record on their first login
        user = await users_repo.create_user(
            db=db,
            firebase_uid=firebase_uid,
            email=claims.get("email"),
            display_name=claims.get("name"),
            phone=claims.get("phone"),
        )

    # Package response with custom session details
    return auth_service.create_session_response(user)
