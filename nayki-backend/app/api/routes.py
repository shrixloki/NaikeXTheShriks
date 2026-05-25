import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.models import User
from app.schemas.routes import (
    RouteCompareRequest,
    RouteComparisonResponse,
    RouteSafetyBreakdownResponse,
)
from app.security.dependencies import get_current_user
from app.services.routing_service import RoutingService

router = APIRouter(tags=["Safety-Routing compares"])
routing_service = RoutingService()


@router.post(
    "/routes/compare",
    response_model=RouteComparisonResponse,
    status_code=status.HTTP_200_OK,
)
async def compare_routes(
    request: RouteCompareRequest,
    current_user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare multiple route candidates between origin and destination.

    Evaluates paths against spatial PostGIS databases and returns detailed safety
    profiles without making safety guarantees.
    """
    try:
        user_id = current_user.id if current_user else None
        return await routing_service.compare_routes(db, user_id, request)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/routes/{route_evaluation_id}")
async def get_route_evaluation(
    route_evaluation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve saved parameters and shapes from a historic route evaluation."""
    evaluation = await routing_service.get_route_evaluation(db, route_evaluation_id)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route evaluation with ID {route_evaluation_id} not found.",
        )
    return {
        "id": str(evaluation.id),
        "user_id": str(evaluation.user_id) if evaluation.user_id else None,
        "selected_route_type": evaluation.selected_route_type,
        "fastest_route": evaluation.fastest_route,
        "lower_risk_route": evaluation.lower_risk_route,
        "balanced_route": evaluation.balanced_route,
        "coverage_status": evaluation.coverage_status,
        "created_at": evaluation.created_at,
    }


@router.get(
    "/safety/route/{route_evaluation_id}",
    response_model=RouteSafetyBreakdownResponse,
)
async def get_route_safety_breakdown(
    route_evaluation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve fine-grained safety engine observation breakdowns for a calculated route evaluation."""
    try:
        return await routing_service.get_route_safety_breakdown(db, route_evaluation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
