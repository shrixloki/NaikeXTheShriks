import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.models import User
from app.schemas.sos import SosAlertResponse, SosCreateRequest, SosResponseRequest
from app.security.dependencies import get_current_user
from app.services.sos_service import SosService

router = APIRouter(prefix="/sos", tags=["Active Emergency SOS alerts"])
sos_service = SosService()


@router.post(
    "",
    response_model=SosAlertResponse,
    status_code=status.HTTP_201_CREATED,
)
async def trigger_sos(
    request: SosCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger an emergency alert broadcast to nearby active devices within a 2000m radius.

    Exact coordinate positions are encrypted and are never exposed in log outputs.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided.",
        )
    return await sos_service.trigger_sos(db, current_user.id, request)


@router.post("/{alert_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_sos(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an active SOS trigger."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided.",
        )
    try:
        await sos_service.cancel_sos(db, current_user.id, alert_id)
        return {"status": "success", "message": "Emergency SOS alert cancelled."}
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{alert_id}/mark-safe", status_code=status.HTTP_200_OK)
async def mark_safe(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resolve an active SOS, flagging that the user is now safe."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided.",
        )
    try:
        await sos_service.mark_safe(db, current_user.id, alert_id)
        return {"status": "success", "message": "Emergency SOS resolved: user safe."}
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{alert_id}/respond", status_code=status.HTTP_200_OK)
async def respond_to_alert(
    alert_id: uuid.UUID,
    request: SosResponseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit confirmation or false alarm feedback from notified nearby recipients."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided.",
        )
    await sos_service.respond_to_alert(db, current_user.id, alert_id, request)
    return {"status": "success", "message": "Recipient response persisted."}
