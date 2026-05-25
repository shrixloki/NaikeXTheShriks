from typing import Any

from pydantic import BaseModel, Field

from app.schemas.incidents import IncidentReportResponse
from app.schemas.users import DeviceResponse, EmergencyContactResponse, UserProfile


class PrivacyExportResponse(BaseModel):
    profile: UserProfile
    emergency_contacts: list[EmergencyContactResponse] = Field(default_factory=list)
    devices: list[DeviceResponse] = Field(default_factory=list)
    incident_reports: list[IncidentReportResponse] = Field(default_factory=list)
    sos_metadata: list[dict[str, Any]] = Field(default_factory=list, description="Anonymized summaries of triggered SOS alerts")
    route_evaluations_metadata: list[dict[str, Any]] = Field(default_factory=list, description="Anonymized summaries of requested route calculations")
