from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import ReportStatus, ReportType


class IncidentReportCreate(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    report_type: ReportType
    description: str | None = None


class IncidentReportResponse(BaseModel):
    id: str
    user_id: str | None = None
    report_type: ReportType
    description: str | None = None
    lat: float
    lng: float
    h3_index: str
    status: ReportStatus
    confidence: float
    created_at: datetime
    updated_at: datetime
