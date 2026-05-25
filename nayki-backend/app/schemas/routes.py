from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import ConfidenceLevel, CoverageStatus, RiskLevel


class RouteCoordinate(BaseModel):
    lat: float
    lng: float


class RouteCompareRequest(BaseModel):
    origin: RouteCoordinate
    destination: RouteCoordinate
    departure_time: datetime | None = None
    max_extra_time_percent: float | None = Field(default=30.0, description="Upper threshold allowance for extra time on risk-avoiding paths")


class RouteGeometry(BaseModel):
    type: str = "LineString"
    coordinates: list[list[float]] = Field(..., description="Array of [lng, lat] coordinate pairs")


class EvaluatedRouteDetail(BaseModel):
    route_type: str
    distance_meters: float
    duration_seconds: float
    geometry: RouteGeometry
    instructions: list[str] = Field(default_factory=list)
    safety_score: float | None = None
    confidence_level: ConfidenceLevel
    risk_level: RiskLevel
    risk_reasons: list[str] = Field(default_factory=list)


class RouteComparisonResponse(BaseModel):
    fastest_route: EvaluatedRouteDetail | None = None
    lower_risk_route: EvaluatedRouteDetail | None = None
    balanced_route: EvaluatedRouteDetail | None = None
    coverage_status: CoverageStatus
    explanation: str
    route_evaluation_id: str


class RouteSafetyBreakdownResponse(BaseModel):
    route_evaluation_id: str
    route_level_risk: float
    safety_score: float | None = None
    confidence: float
    confidence_level: ConfidenceLevel
    coverage_status: CoverageStatus
    evidence_count: int
    risk_reasons: list[str]
    high_risk_segments: list[dict[str, Any]] = Field(default_factory=list)
