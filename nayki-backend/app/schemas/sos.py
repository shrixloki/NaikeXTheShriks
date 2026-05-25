from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import SosAlertStatus, SosAlertType, SosRecipientResponse


class SosCreateRequest(BaseModel):
    lat: float
    lng: float
    alert_type: SosAlertType = SosAlertType.SOS
    metadata: dict[str, Any] | None = Field(default_factory=dict)


class SosAlertResponse(BaseModel):
    id: str
    user_id: str
    alert_type: SosAlertType
    status: SosAlertStatus
    expires_at: datetime
    recipient_count: int
    approximate_lat: float
    approximate_lng: float


class SosResponseRequest(BaseModel):
    response: SosRecipientResponse
