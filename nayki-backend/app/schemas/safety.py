from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import ConfidenceLevel, CoverageStatus, RiskLevel


class SafetyCellResponse(BaseModel):
    h3_index: str
    city: str | None = None
    risk_score: float | None = None
    safety_score: float | None = None
    confidence: float
    confidence_level: ConfidenceLevel
    risk_level: RiskLevel
    coverage_status: CoverageStatus
    evidence_count: int
    risk_reasons: list[str]
    last_computed_at: datetime | None = None

    class Config:
        from_attributes = True


class PrivacyEvidenceAggregationResponse(BaseModel):
    h3_index: str
    evidence_count: int
    average_severity: float
    average_confidence: float
    evidence_types: list[str]
