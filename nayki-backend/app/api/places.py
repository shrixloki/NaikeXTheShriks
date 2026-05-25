
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.enums import HelpPoiType
from app.schemas.places import HelpPoiListResponse, PlaceSearchResponse
from app.services.place_service import PlaceService

router = APIRouter(prefix="/places", tags=["Places & Help Directories"])
place_service = PlaceService()


@router.get("/search", response_model=list[PlaceSearchResponse])
async def search_places(
    q: str = Query(..., min_length=1, description="Text query (e.g. pharmacy name)"),
    lat: float = Query(..., ge=-90.0, le=90.0),
    lng: float = Query(..., ge=-180.0, le=180.0),
    db: AsyncSession = Depends(get_db),
):
    """Search for dynamic locations and POIs.

    Queries external mapping services if available, falling back onto our local
    POI tables. Returns empty outcomes if no data matches.
    """
    return await place_service.search_places(db, q, lat, lng)


@router.get("/help", response_model=HelpPoiListResponse)
async def get_nearby_help(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lng: float = Query(..., ge=-180.0, le=180.0),
    type: HelpPoiType | None = Query(None, description="Filter by agency classification"),
    radius_meters: float = Query(3000.0, ge=100.0, le=10000.0),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve nearby safety support agencies (e.g., police stations or emergency hospitals).

    Checks our local directories before enriching. Returns empty lists with
    'unavailable' coverage status if no support features reside within the search area.
    """
    return await place_service.get_nearby_help(db, lat, lng, type, radius_meters)
