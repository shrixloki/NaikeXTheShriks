from typing import Any

import httpx

from app.config import settings
from app.logging import logger


class GooglePlacesClient:
    """Client to query local points of interest and enrichment from the Google Places API."""

    def __init__(self):
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        self.timeout = 5.0

    def is_enabled(self) -> bool:
        """Check if Google Places API client has been configured."""
        return bool(self.api_key)

    async def search_places(
        self, query: str, lat: float, lng: float, radius_meters: float = 5000.0
    ) -> list[dict[str, Any]]:
        """Search for public places around a coordinate using text search."""
        if not self.is_enabled():
            logger.info("Google Places Client is disabled. Skipping query.")
            return []

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "location": f"{lat},{lng}",
            "radius": radius_meters,
            "key": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    logger.error("Google Places search failed", status_code=response.status_code)
                    return []
                
                data = response.json()
                results = data.get("results", [])
                
                places = []
                for res in results:
                    loc = res.get("geometry", {}).get("location", {})
                    places.append({
                        "name": res.get("name", ""),
                        "address": res.get("formatted_address", ""),
                        "lat": loc.get("lat"),
                        "lng": loc.get("lng"),
                        "place_id": res.get("place_id"),
                        "types": res.get("types", []),
                    })
                return places
        except Exception as e:
            logger.error("Error communicating with Google Places API", error=str(e))
            return []

    async def search_nearby_help(
        self, lat: float, lng: float, place_type: str, radius_meters: float = 3000.0
    ) -> list[dict[str, Any]]:
        """Search for specific help agencies (police, hospital, transit) using Google Nearby Search."""
        if not self.is_enabled():
            logger.info("Google Places Client is disabled. Nearby help search skipped.")
            return []

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        # Map Nayki types to Google Place types
        # Nayki: police, hospital, pharmacy, public_place, transit
        type_mapping = {
            "police": "police",
            "hospital": "hospital",
            "pharmacy": "pharmacy",
            "transit": "transit_station",
            "public_place": "library",
        }
        google_type = type_mapping.get(place_type, "police")

        params = {
            "location": f"{lat},{lng}",
            "radius": radius_meters,
            "type": google_type,
            "key": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    logger.error("Google Places nearby search failed", status_code=response.status_code)
                    return []

                data = response.json()
                results = data.get("results", [])
                
                help_pois = []
                for res in results:
                    loc = res.get("geometry", {}).get("location", {})
                    help_pois.append({
                        "name": res.get("name", ""),
                        "address": res.get("vicinity", ""),
                        "lat": loc.get("lat"),
                        "lng": loc.get("lng"),
                        "type": place_type,
                        "confidence": 0.85,
                        "open_status": "open" if res.get("opening_hours", {}).get("open_now") else "unknown",
                    })
                return help_pois
        except Exception as e:
            logger.error("Error communicating with Google Places API (nearby help)", error=str(e))
            return []
