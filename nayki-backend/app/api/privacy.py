from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.models import User
from app.schemas.privacy import PrivacyExportResponse
from app.security.dependencies import get_current_user
from app.services.privacy_service import PrivacyService

router = APIRouter(prefix="/privacy", tags=["GDPR Privacy Compliance"])
privacy_service = PrivacyService()


@router.get("/export", response_model=PrivacyExportResponse)
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a complete structured export of all database content associated with this user."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided.",
        )
    return await privacy_service.export_user_data(db, current_user)


@router.delete("/account", status_code=status.HTTP_200_OK)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate soft-deletion of the user profile, purges push device tokens, and redacts identification records."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided.",
        )
    await privacy_service.delete_user_account(db, current_user)
    return {"status": "success", "message": "User account soft-deletion complete."}
