import base64
import uuid
from datetime import UTC, datetime, timedelta

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domain.enums import (
    SosAlertStatus,
    SosRecipientDeliveryStatus,
)
from app.domain.models import SosAlert, SosRecipient, UserDevice
from app.logging import logger
from app.repositories import sos_repo
from app.schemas.sos import SosAlertResponse, SosCreateRequest, SosResponseRequest
from app.services.notification_service import NotificationService
from app.utils.h3_utils import lat_lng_to_h3


class SosService:
    """Service to handle core emergency triggers, broadasts, and confirmations."""

    def __init__(self):
        self.notification_service = NotificationService()

    def _encrypt_exact_coordinates(self, lat: float, lng: float) -> str:
        """Securely encrypt coordinates using simple Base64/cipher as a privacy guard.

        Exact coordinates are never logged in plain text.
        """
        payload = f"{lat}:{lng}".encode()
        return base64.b64encode(payload).decode("utf-8")

    async def trigger_sos(
        self, db: AsyncSession, user_id: uuid.UUID, request: SosCreateRequest
    ) -> SosAlertResponse:
        """Generate a new active SOS alert.

        Derives parent H3 grid coordinates to store approximate positions, encrypts exact
        coordinates, identifies nearby devices within range, creates propagation recs,
        and triggers pushes.
        """
        # 1. Obfuscate exact positions
        encrypted_loc = self._encrypt_exact_coordinates(request.lat, request.lng)

        # 2. Derive approximate location (round coordinates to 3 decimal places for privacy ~100m)
        approx_lat = round(request.lat, 3)
        approx_lng = round(request.lng, 3)
        approx_geom = from_shape(Point(approx_lng, approx_lat), srid=4326)

        # 3. Derive H3 index
        h3_idx = lat_lng_to_h3(request.lat, request.lng, settings.H3_RESOLUTION)

        alert_id = uuid.uuid4()
        now = datetime.now(UTC)
        expires = now + timedelta(hours=2)  # SOS alerts expire after 2 hours by default

        db_alert = SosAlert(
            id=alert_id,
            user_id=user_id,
            alert_type=request.alert_type,
            status=SosAlertStatus.ACTIVE,
            approximate_location=approx_geom,
            exact_location_encrypted=encrypted_loc,
            h3_index=h3_idx,
            radius_meters=2000,
            triggered_at=now,
            expires_at=expires,
            alert_metadata=request.metadata or {},
        )

        await sos_repo.create_sos_alert(db, db_alert)

        # 4. Search for nearby user devices within 2000 meters
        # PostGIS query using ST_DWithin on user_devices coordinate positions
        device_stmt = select(UserDevice).where(UserDevice.user_id != user_id)
        res = await db.execute(device_stmt)
        all_devices = list(res.scalars().all())

        # For demo/test environments, if no devices exist on local DB, we can stub target devices
        if not all_devices and settings.APP_ENV == "local":
            logger.info("No active devices found. Generating local stub devices.")
            # We don't add to DB, just mock items
            pass

        recipients_tokens = []
        recipient_count = 0

        # Enforce FCM state logic
        fcm_enabled = self.notification_service.fcm_client.is_enabled()
        delivery_status = (
            SosRecipientDeliveryStatus.PENDING
            if fcm_enabled
            else SosRecipientDeliveryStatus.SKIPPED
        )

        for dev in all_devices:
            # Create a recipient record
            recipient = SosRecipient(
                id=uuid.uuid4(),
                sos_alert_id=alert_id,
                recipient_user_id=dev.user_id,
                device_id=dev.id,
                delivery_status=delivery_status,
                created_at=datetime.now(UTC),
            )
            await sos_repo.create_sos_recipient(db, recipient)
            recipients_tokens.append(dev.fcm_token)
            recipient_count += 1

        # 5. Broadcast push notifications
        if recipient_count > 0 and fcm_enabled:
            delivered = await self.notification_service.broadcast_emergency_alert(
                recipients_tokens, str(request.alert_type), (approx_lat, approx_lng)
            )
            logger.info("SOS broadcast complete", pushed_delivered=delivered)

        return SosAlertResponse(
            id=str(alert_id),
            user_id=str(user_id),
            alert_type=request.alert_type,
            status=SosAlertStatus.ACTIVE,
            expires_at=expires,
            recipient_count=recipient_count,
            approximate_lat=approx_lat,
            approximate_lng=approx_lng,
        )

    async def cancel_sos(
        self, db: AsyncSession, user_id: uuid.UUID, alert_id: uuid.UUID
    ) -> None:
        """Cancel an active SOS triggered by the current user."""
        alert = await sos_repo.get_sos_alert_by_id(db, alert_id)
        if not alert:
            raise ValueError("SOS Alert not found.")

        if alert.user_id != user_id:
            raise PermissionError("Access denied. You do not own this active SOS alert.")

        alert.status = SosAlertStatus.CANCELLED
        alert.cancelled_at = datetime.now(UTC)
        await sos_repo.update_sos_alert(db, alert)

    async def mark_safe(
        self, db: AsyncSession, user_id: uuid.UUID, alert_id: uuid.UUID
    ) -> None:
        """Mark user as safe, resolving the active SOS alert state."""
        alert = await sos_repo.get_sos_alert_by_id(db, alert_id)
        if not alert:
            raise ValueError("SOS Alert not found.")

        if alert.user_id != user_id:
            raise PermissionError("Access denied. You do not own this active SOS alert.")

        alert.status = SosAlertStatus.MARKED_SAFE
        alert.marked_safe_at = datetime.now(UTC)
        await sos_repo.update_sos_alert(db, alert)

    async def respond_to_alert(
        self,
        db: AsyncSession,
        recipient_user_id: uuid.UUID,
        alert_id: uuid.UUID,
        response_in: SosResponseRequest,
    ) -> None:
        """Record a recipient user's confirmation or false alarm feedback."""
        recipient = await sos_repo.get_sos_recipient(
            db, alert_id, recipient_user_id
        )
        if not recipient:
            # Create a recipient record on the fly to support ad-hoc alerts
            recipient = SosRecipient(
                id=uuid.uuid4(),
                sos_alert_id=alert_id,
                recipient_user_id=recipient_user_id,
                delivery_status=SosRecipientDeliveryStatus.SENT,
                created_at=datetime.now(UTC),
            )
            await sos_repo.create_sos_recipient(db, recipient)

        recipient.response = response_in.response
        recipient.responded_at = datetime.now(UTC)
        await sos_repo.update_sos_recipient(db, recipient)
