from typing import Any

import httpx

from app.config import settings
from app.logging import logger


class FcmClient:
    """Client to send push notifications via Firebase Cloud Messaging (FCM).

    If credentials or keys are missing, notifications are skipped gracefully.
    We never claim notifications were successfully pushed if the service is offline or unconfigured.
    """

    def __init__(self):
        self.server_key = settings.FCM_SERVER_KEY
        self.timeout = 5.0

    def is_enabled(self) -> bool:
        """Check if FCM client has been configured."""
        return bool(self.server_key)

    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> bool:
        """Deliver a push notification to an FCM device token.

        Returns True if sent successfully, False otherwise.
        """
        if not self.is_enabled():
            logger.info(
                "FCM Client is unconfigured. Skipping push delivery.",
                device_token=device_token[:8] + "...",
            )
            return False

        # Legacy HTTP FCM endpoint (supported by key configurations)
        url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": f"key={self.server_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "to": device_token,
            "notification": {"title": title, "body": body, "sound": "default"},
            "data": data or {},
            "priority": "high",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    success = result.get("success", 0) > 0
                    if success:
                        logger.info("FCM push notification sent successfully")
                        return True
                    else:
                        logger.warn(
                            "FCM push notification rejected by server",
                            result=result,
                        )
                        return False
                else:
                    logger.error(
                        "FCM gateway returned an error",
                        status_code=response.status_code,
                        text=response.text,
                    )
                    return False
        except Exception as e:
            logger.error("Error communicating with FCM gateway", error=str(e))
            return False
