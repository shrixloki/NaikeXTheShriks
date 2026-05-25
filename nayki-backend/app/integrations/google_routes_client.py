from typing import Any

import httpx

from app.config import settings
from app.logging import logger


class GoogleRoutesClient:
    """Client to query reference routes from Google Routes API.

    This client serves only to fetch baseline ETAs and distances; it has no
    influence on the Safety Engine calculations.
    """

    def __init__(self):
        self.api_key = settings.GOOGLE_ROUTES_API_KEY
        self.timeout = 5.0

    def is_enabled(self) -> bool:
        """Check if Google Routes API client has been configured."""
        return bool(self.api_key)

    async def get_reference_eta(
        self, origin: tuple[float, float], destination: tuple[float, float]
    ) -> dict[str, Any] | None:
        """Fetch baseline ETA and distance from Google Routes API for reference."""
        if not self.is_enabled():
            logger.info("Google Routes Client is disabled. Reference query skipped.")
            return None

        # Google Routes Preferred API Endpoint
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
        }
        
        payload = {
            "origin": {
                "location": {
                    "latLng": {"latitude": origin[0], "longitude": origin[1]}
                }
            },
            "destination": {
                "location": {
                    "latLng": {"latitude": destination[0], "longitude": destination[1]}
                }
            },
            "travelMode": "WALK",
            "routingPreference": "ROUTING_PREFERENCE_UNSPECIFIED",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    logger.error("Google Routes compute failed", status_code=response.status_code)
                    return None
                
                data = response.json()
                routes = data.get("routes", [])
                if not routes:
                    return None
                
                route = routes[0]
                duration_str = route.get("duration", "0s")  # returns like "1200s"
                duration_seconds = float(duration_str.rstrip("s"))
                distance_meters = float(route.get("distanceMeters", 0.0))

                return {
                    "reference_duration_seconds": duration_seconds,
                    "reference_distance_meters": distance_meters,
                }
        except Exception as e:
            logger.error("Error communicating with Google Routes API", error=str(e))
            return None
