from geoalchemy2.shape import to_shape
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import CoverageStatus, HelpPoiType
from app.integrations.google_places_client import GooglePlacesClient
from app.repositories import poi_repo, safety_repo
from app.schemas.places import HelpPoiListResponse, HelpPoiResponse, PlaceSearchResponse


class PlaceService:
    """Service to search places and local help POIs using both local databases and the Google Places API."""

    def __init__(self):
        self.google_places_client = GooglePlacesClient()

    async def search_places(
        self, db: AsyncSession, query: str, lat: float, lng: float
    ) -> list[PlaceSearchResponse]:
        """Search for POIs.

        Uses Google Places API if configured, otherwise performs local text matches
        on our help_pois table. Does not invent POIs.
        """
        if self.google_places_client.is_enabled():
            places = await self.google_places_client.search_places(query, lat, lng)
            return [PlaceSearchResponse(**p) for p in places]

        # Local DB fallback
        pois = await poi_repo.get_pois_by_type(db, poi_type=None, limit=20)
        matched_pois = []
        for poi in pois:
            if query.lower() in poi.name.lower() or (poi.address and query.lower() in poi.address.lower()):
                point = to_shape(poi.location)
                matched_pois.append(
                    PlaceSearchResponse(
                        name=poi.name,
                        address=poi.address,
                        lat=point.y,
                        lng=point.x,
                        place_id=str(poi.id),
                        types=[str(poi.type)],
                    )
                )
        return matched_pois

    async def get_nearby_help(
        self,
        db: AsyncSession,
        lat: float,
        lng: float,
        poi_type: HelpPoiType | None = None,
        radius_meters: float = 3000.0,
    ) -> HelpPoiListResponse:
        """Fetch nearby help endpoints (police stations, emergency rooms).

        Prefers local help_pois database to protect user privacy. If Google Places is
        active, optionally queries Google Maps to enrich. Returns 'unavailable' coverage
        if no real POIs reside within range. Never fabricates records.
        """
        # 1. Fetch from local DB using PostGIS Geography search
        local_pois = await safety_repo.get_nearby_help_pois(db, lat, lng, radius_meters)
        
        # Filter by type if provided
        if poi_type:
            local_pois = [p for p in local_pois if p.type == poi_type]

        pois_response = []
        for poi in local_pois:
            point = to_shape(poi.location)
            pois_response.append(
                HelpPoiResponse(
                    name=poi.name,
                    address=poi.address,
                    lat=point.y,
                    lng=point.x,
                    type=poi.type,
                    confidence=float(poi.confidence),
                    open_status=poi.open_status,
                )
            )

        # 2. Enrich via Google Places API if local results are sparse and Google is enabled
        if len(pois_response) < 3 and self.google_places_client.is_enabled() and poi_type:
            google_pois = await self.google_places_client.search_nearby_help(
                lat, lng, str(poi_type), radius_meters
            )
            for gp in google_pois:
                # Deduplicate by approximate coordinates
                if not any(abs(gp["lat"] - pr.lat) < 0.0005 and abs(gp["lng"] - pr.lng) < 0.0005 for pr in pois_response):
                    pois_response.append(HelpPoiResponse(**gp))

        # 3. Assess coverage status based on results found
        if not pois_response:
            coverage = CoverageStatus.UNAVAILABLE
        elif len(pois_response) < 3:
            coverage = CoverageStatus.LIMITED
        elif len(pois_response) < 8:
            coverage = CoverageStatus.MODERATE
        else:
            coverage = CoverageStatus.STRONG

        return HelpPoiListResponse(pois=pois_response, coverage_status=coverage)
