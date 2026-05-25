import uuid
from datetime import UTC, datetime

from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domain.enums import ReportStatus
from app.domain.models import IncidentReport
from app.repositories import incidents_repo
from app.schemas.incidents import IncidentReportCreate, IncidentReportResponse
from app.utils.h3_utils import lat_lng_to_h3


class IncidentService:
    """Service to handle crowd-sourced incident reporting pipelines."""

    async def report_incident(
        self,
        db: AsyncSession,
        user_id: uuid.UUID | None,
        report_in: IncidentReportCreate,
    ) -> IncidentReportResponse:
        """Submit a new safety incident.

        Converts geographic coordinates into spatial points and derives an H3 cell index.
        Starts with 'submitted' status and 0.25 confidence. Never auto-verifies.
        """
        # Derive H3 index
        h3_idx = lat_lng_to_h3(report_in.lat, report_in.lng, settings.H3_RESOLUTION)

        # Create Point geometry
        geom = from_shape(Point(report_in.lng, report_in.lat), srid=4326)

        db_report = IncidentReport(
            id=uuid.uuid4(),
            user_id=user_id,
            report_type=report_in.report_type,
            description=report_in.description,
            location=geom,
            h3_index=h3_idx,
            status=ReportStatus.SUBMITTED,
            confidence=0.25,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        saved = await incidents_repo.create_incident_report(db, db_report)

        return IncidentReportResponse(
            id=str(saved.id),
            user_id=str(saved.user_id) if saved.user_id else None,
            report_type=saved.report_type,
            description=saved.description,
            lat=report_in.lat,
            lng=report_in.lng,
            h3_index=saved.h3_index,
            status=saved.status,
            confidence=float(saved.confidence),
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def get_my_reports(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[IncidentReportResponse]:
        """Fetch all reports submitted by the logged-in user profile."""
        reports = await incidents_repo.get_user_incident_reports(db, user_id)
        
        response_list = []
        for r in reports:
            point = to_shape(r.location)
            response_list.append(
                IncidentReportResponse(
                    id=str(r.id),
                    user_id=str(r.user_id) if r.user_id else None,
                    report_type=r.report_type,
                    description=r.description,
                    lat=point.y,
                    lng=point.x,
                    h3_index=r.h3_index,
                    status=r.status,
                    confidence=float(r.confidence),
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
            )
        return response_list

    async def cancel_report(
        self, db: AsyncSession, user_id: uuid.UUID, report_id: uuid.UUID
    ) -> None:
        """Allow users to self-cancel their own incident reports before review completed."""
        report = await incidents_repo.get_incident_report_by_id(db, report_id)
        if not report:
            raise ValueError("Incident report not found.")

        if report.user_id != user_id:
            raise PermissionError("Access denied. You do not own this incident report.")

        if report.status in (ReportStatus.VERIFIED, ReportStatus.REJECTED):
            raise ValueError(
                f"Cannot cancel report. Report has already been {report.status}."
            )

        report.status = ReportStatus.EXPIRED
        report.updated_at = datetime.now(UTC)
        await incidents_repo.update_incident_report(db, report)
