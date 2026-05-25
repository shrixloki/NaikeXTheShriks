from typing import Any

from app.logging import logger


class OsmOverpassClient:
    """Client to query OpenStreetMap (OSM) entities using Overpass API.

    This serves as an optional placeholder integration. It does not block
    system operations or startup if disabled or unconfigured.
    """

    def __init__(self):
        self.endpoint = "https://overpass-api.de/api/interpreter"
        self.timeout = 10.0

    def is_enabled(self) -> bool:
        """Check if OpenStreetMap overpass service integration is active."""
        return True

    async def fetch_streetlights(
        self, bbox: tuple[float, float, float, float]
    ) -> list[dict[str, Any]]:
        """Fetch streetlight markers inside a bounding box (south, west, north, east)."""
        if not self.is_enabled():
            return []

        logger.info("OSM Overpass query for streetlights triggered.", bbox=bbox)
        # Returns empty collection in this phase since OSM acts as a future/optional enhancement
        return []
