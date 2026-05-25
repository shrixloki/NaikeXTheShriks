
from pydantic import BaseModel, Field

from app.domain.enums import CoverageStatus, HelpPoiType


class PlaceSearchResponse(BaseModel):
    name: str
    address: str | None = None
    lat: float
    lng: float
    place_id: str | None = None
    types: list[str] = Field(default_factory=list)


class HelpPoiResponse(BaseModel):
    name: str
    address: str | None = None
    lat: float
    lng: float
    type: HelpPoiType
    confidence: float
    open_status: str | None = None


class HelpPoiListResponse(BaseModel):
    pois: list[HelpPoiResponse]
    coverage_status: CoverageStatus
