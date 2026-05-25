from datetime import UTC, datetime

from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import RouteEvaluation, SosAlert, User, UserDevice
from app.repositories import incidents_repo, users_repo
from app.schemas.incidents import IncidentReportResponse
from app.schemas.privacy import PrivacyExportResponse
from app.schemas.users import DeviceResponse, EmergencyContactResponse, UserProfile


class PrivacyService:
    """Service to handle GDPR privacy compliance, data export, and account soft-deletion."""

    async def export_user_data(
        self, db: AsyncSession, user: User
    ) -> PrivacyExportResponse:
        """Collate and return all data associated with a user profile."""
        user_id = user.id

        # 1. Collate Profile
        profile = UserProfile(
            id=str(user.id),
            firebase_uid=user.firebase_uid,
            phone=user.phone,
            email=user.email,
            display_name=user.display_name,
            trust_score=float(user.trust_score),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        # 2. Collate Emergency Contacts
        contacts = await users_repo.get_emergency_contacts(db, user_id)
        contacts_res = [
            EmergencyContactResponse(
                id=str(c.id),
                name=c.name,
                phone=c.phone,
                relationship=c.relationship,
                is_verified=c.is_verified,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in contacts
        ]

        # 3. Collate Device Push Tokens
        stmt_dev = select(UserDevice).where(UserDevice.user_id == user_id)
        res_dev = await db.execute(stmt_dev)
        devices = list(res_dev.scalars().all())
        devices_res = [
            DeviceResponse(
                id=str(d.id),
                fcm_token=d.fcm_token,
                platform=d.platform,
                device_model=d.device_model,
                app_version=d.app_version,
                last_seen_at=d.last_seen_at,
                created_at=d.created_at,
            )
            for d in devices
        ]

        # 4. Collate Incident Reports
        reports = await incidents_repo.get_user_incident_reports(db, user_id)
        reports_res = []
        for r in reports:
            point = to_shape(r.location)
            reports_res.append(
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

        # 5. Collate SOS Alert Summaries (Anonymized metadata)
        stmt_sos = select(SosAlert).where(SosAlert.user_id == user_id)
        res_sos = await db.execute(stmt_sos)
        sos_alerts = list(res_sos.scalars().all())
        sos_res = [
            {
                "id": str(s.id),
                "alert_type": str(s.alert_type),
                "status": str(s.status),
                "radius_meters": s.radius_meters,
                "triggered_at": s.triggered_at.isoformat(),
            }
            for s in sos_alerts
        ]

        # 6. Collate Route Calculation Summaries (Anonymized metadata)
        stmt_rt = select(RouteEvaluation).where(RouteEvaluation.user_id == user_id)
        res_rt = await db.execute(stmt_rt)
        routes = list(res_rt.scalars().all())
        routes_res = [
            {
                "id": str(rt.id),
                "selected_route_type": rt.selected_route_type,
                "coverage_status": str(rt.coverage_status),
                "created_at": rt.created_at.isoformat(),
            }
            for rt in routes
        ]

        return PrivacyExportResponse(
            profile=profile,
            emergency_contacts=contacts_res,
            devices=devices_res,
            incident_reports=reports_res,
            sos_metadata=sos_res,
            route_evaluations_metadata=routes_res,
        )

    async def delete_user_account(self, db: AsyncSession, user: User) -> None:
        """Perform GDPR-compliant account soft-deletion.

        Nulls out contact details, hashes/redacts identifiers, and purges FCM tokens.
        Audit logs remain intact but anonymized.
        """
        user_id = user.id

        # 1. Soft-delete user profile
        user.deleted_at = datetime.now(UTC)
        user.display_name = "[REDACTED]"
        user.email = None
        user.phone = None
        user.firebase_uid = None

        # 2. Purge active device push tokens
        stmt_dev = select(UserDevice).where(UserDevice.user_id == user_id)
        res_dev = await db.execute(stmt_dev)
        devices = list(res_dev.scalars().all())
        for dev in devices:
            await db.delete(dev)

        await db.commit()
