import uuid
from datetime import UTC, datetime
from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as orm_relationship

from app.database import Base
from app.domain.enums import (
    CoverageStatus,
    EvidenceSource,
    EvidenceType,
    HelpPoiType,
    ReportStatus,
    ReportType,
    SosAlertStatus,
    SosAlertType,
    SosRecipientDeliveryStatus,
    SosRecipientResponse,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    firebase_uid: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    trust_score: Mapped[float] = mapped_column(
        Numeric(precision=3, scale=2), default=0.5
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    devices: Mapped[list["UserDevice"]] = orm_relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    emergency_contacts: Mapped[list["EmergencyContact"]] = orm_relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserDevice(Base):
    __tablename__ = "user_devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    fcm_token: Mapped[str] = mapped_column(String, index=True)
    platform: Mapped[str] = mapped_column(String)
    device_model: Mapped[str | None] = mapped_column(String, nullable=True)
    app_version: Mapped[str | None] = mapped_column(String, nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
    )

    # Relationships
    user: Mapped["User"] = orm_relationship(back_populates="devices")


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    relationship: Mapped[str | None] = mapped_column(String, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    user: Mapped["User"] = orm_relationship(back_populates="emergency_contacts")


class HelpPoi(Base):
    __tablename__ = "help_pois"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source: Mapped[str] = mapped_column(String)
    source_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[HelpPoiType] = mapped_column(
        SQLEnum(HelpPoiType, name="help_poi_type_enum"), default=HelpPoiType.OTHER
    )
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    location = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )
    open_status: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[float] = mapped_column(
        Numeric(precision=3, scale=2), default=0.5
    )
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class SafetyCell(Base):
    __tablename__ = "safety_cells"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    h3_index: Mapped[str] = mapped_column(String, unique=True, index=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(
        Numeric(precision=5, scale=4), nullable=True
    )
    safety_score: Mapped[float | None] = mapped_column(
        Numeric(precision=5, scale=4), nullable=True
    )
    confidence: Mapped[float] = mapped_column(
        Numeric(precision=3, scale=2), default=0.0
    )
    coverage_status: Mapped[CoverageStatus] = mapped_column(
        SQLEnum(CoverageStatus, name="coverage_status_enum"),
        default=CoverageStatus.UNAVAILABLE,
    )
    last_computed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class SafetyEvidence(Base):
    __tablename__ = "safety_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    h3_index: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    source: Mapped[EvidenceSource] = mapped_column(
        SQLEnum(EvidenceSource, name="evidence_source_enum")
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(
        SQLEnum(EvidenceType, name="evidence_type_enum")
    )
    severity: Mapped[float] = mapped_column(Numeric(precision=3, scale=2))
    confidence: Mapped[float] = mapped_column(Numeric(precision=3, scale=2))
    event_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    location = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=True,
    )
    evidence_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    action: Mapped[str] = mapped_column(String)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    ip_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    log_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
    )


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    report_type: Mapped[ReportType] = mapped_column(
        SQLEnum(ReportType, name="report_type_enum")
    )
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    location = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )
    h3_index: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus, name="report_status_enum"), default=ReportStatus.SUBMITTED
    )
    confidence: Mapped[float] = mapped_column(
        Numeric(precision=3, scale=2), default=0.25
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class SosAlert(Base):
    __tablename__ = "sos_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    alert_type: Mapped[SosAlertType] = mapped_column(
        SQLEnum(SosAlertType, name="sos_alert_type_enum")
    )
    status: Mapped[SosAlertStatus] = mapped_column(
        SQLEnum(SosAlertStatus, name="sos_alert_status_enum"), index=True
    )
    approximate_location = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )
    exact_location_encrypted: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    h3_index: Mapped[str] = mapped_column(String)
    radius_meters: Mapped[int] = mapped_column(default=2000)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    marked_safe_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    alert_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)


class SosRecipient(Base):
    __tablename__ = "sos_recipients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sos_alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sos_alerts.id", ondelete="CASCADE"), index=True
    )
    recipient_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_devices.id", ondelete="SET NULL"), nullable=True
    )
    delivery_status: Mapped[SosRecipientDeliveryStatus] = mapped_column(
        SQLEnum(SosRecipientDeliveryStatus, name="sos_recipient_delivery_status_enum")
    )
    response: Mapped[SosRecipientResponse | None] = mapped_column(
        SQLEnum(SosRecipientResponse, name="sos_recipient_response_enum"), nullable=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class RouteEvaluation(Base):
    __tablename__ = "route_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    origin = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )
    destination = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )
    selected_route_type: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    fastest_route: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    lower_risk_route: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    balanced_route: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    coverage_status: Mapped[CoverageStatus] = mapped_column(
        SQLEnum(CoverageStatus, name="coverage_status_enum"), default=CoverageStatus.UNAVAILABLE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )
