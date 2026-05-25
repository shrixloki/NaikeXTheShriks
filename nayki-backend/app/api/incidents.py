import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.models import User
from app.schemas.incidents import IncidentReportCreate, IncidentReportResponse
from app.security.dependencies import get_current_user
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/reports", tags=["Crowd-sourced Safety Reports"])
incident_service = IncidentService()


@router.post(
    "",
    response_model=IncidentReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def report_incident(
    report_in: IncidentReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """File a new crowd-sourced hazard or crime incident report.

    Assessed initially as low-confidence and unverified pending dynamic review processes.
    """
    user_id = current_user.id if current_user else None
    return await incident_service.report_incident(db, user_id, report_in)


@router.get("/mine", response_model=list[IncidentReportResponse])
async def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all reports submitted by the authenticated user profile."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided.",
        )
    return await incident_service.get_my_reports(db, current_user.id)


@router.post("/{report_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Allow users to self-cancel their pending incident reports."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided.",
        )
    try:
        await incident_service.cancel_report(db, current_user.id, report_id)
        return {"status": "success", "message": "Incident report cancelled."}
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
