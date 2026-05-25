from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.errors import UnauthorizedError
from app.domain.models import User
from app.repositories import users_repo
from app.security.firebase_auth import verify_firebase_token

# Define standard HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to retrieve the currently authenticated user.

    Extracts Bearer token from headers, verifies it via Firebase Auth,
    and returns the User database model. Auto-provisions the user if they do
    not exist yet in PostgreSQL.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        claims = verify_firebase_token(token)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    firebase_uid = claims["uid"]

    # Retrieve user from Database
    user = await users_repo.get_user_by_firebase_uid(db, firebase_uid)

    if not user:
        # First-time sign-in auto-provisioning
        user = await users_repo.create_user(
            db=db,
            firebase_uid=firebase_uid,
            email=claims.get("email"),
            display_name=claims.get("name"),
            phone=claims.get("phone"),
        )

    return user
