from typing import Any

from app.integrations.fcm_client import FcmClient
from app.logging import logger


class NotificationService:
    """Service to coordinate emergency dispatches and push notifications."""

    def __init__(self):
        self.fcm_client = FcmClient()

    async def broadcast_emergency_alert(
        self,
        device_tokens: list[str],
        alert_type: str,
        approximate_location: tuple[float, float],
    ) -> int:
        """Propagate push notifications to nearby active device tokens.

        Returns count of successfully delivered push alerts. Never claims pushes
        succeeded if FCM client is disabled or unconfigured.
        """
        if not self.fcm_client.is_enabled():
            logger.info("FCM is unconfigured. Broadcast marked skipped.")
            return 0

        title = "⚠️ Emergency Alert Nearby"
        body = f"An active {alert_type} broadcast has been triggered near your location."
        payload = {
            "type": "sos_alert",
            "alert_type": alert_type,
            "approximate_lat": str(approximate_location[0]),
            "approximate_lng": str(approximate_location[1]),
        }

        delivered_count = 0
        for token in device_tokens:
            try:
                success = await self.fcm_client.send_push_notification(
                    token, title, body, payload
                )
                if success:
                    delivered_count += 1
            except Exception as e:
                logger.error(
                    "Failed to dispatch FCM alert to token",
                    token=token[:8] + "...",
                    error=str(e),
                )

        return delivered_count

    async def notify_emergency_contacts(
        self, contacts: list[dict[str, Any]], message: str
    ) -> None:
        """Trigger communication channels (SMS/Email) to designated emergency contacts."""
        # Logs emergency alert contact broadcast details in this phase
        logger.info(
            "Dispatching alert communications to emergency contacts",
            contacts_count=len(contacts),
            message=message,
        )
