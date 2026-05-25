"""routes incidents sos

Revision ID: 002_routes_incidents_sos
Revises: 001_initial
Create Date: 2026-05-22 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = "002_routes_incidents_sos"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums for Part 2
    op.execute(
        "CREATE TYPE report_type_enum AS ENUM ('poor_lighting', 'suspicious_activity', 'accident', 'harassment', 'road_blocked', 'medical_emergency', 'other');"
    )
    op.execute(
        "CREATE TYPE report_status_enum AS ENUM ('submitted', 'under_review', 'verified', 'rejected', 'expired');"
    )
    op.execute(
        "CREATE TYPE sos_alert_type_enum AS ENUM ('sos', 'caution', 'accident', 'medical');"
    )
    op.execute(
        "CREATE TYPE sos_alert_status_enum AS ENUM ('active', 'cancelled', 'marked_safe', 'expired');"
    )
    op.execute(
        "CREATE TYPE sos_recipient_delivery_status_enum AS ENUM ('pending', 'sent', 'failed', 'skipped');"
    )
    op.execute(
        "CREATE TYPE sos_recipient_response_enum AS ENUM ('confirmed', 'false_alarm', 'ignored');"
    )

    # 2. Create incident_reports table
    op.create_table(
        "incident_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "report_type",
            postgresql.ENUM(
                "poor_lighting",
                "suspicious_activity",
                "accident",
                "harassment",
                "road_blocked",
                "medical_emergency",
                "other",
                name="report_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeogFromText",
                name="geography",
                spatial_index=True,
            ),
            nullable=False,
        ),
        sa.Column("h3_index", sa.String(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "submitted",
                "under_review",
                "verified",
                "rejected",
                "expired",
                name="report_status_enum",
                create_type=False,
            ),
            server_default="submitted",
            nullable=False,
        ),
        sa.Column(
            "confidence",
            sa.Numeric(precision=3, scale=2),
            server_default="0.25",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_incident_reports_h3_index", "incident_reports", ["h3_index"]
    )

    # 3. Create sos_alerts table
    op.create_table(
        "sos_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "alert_type",
            postgresql.ENUM(
                "sos",
                "caution",
                "accident",
                "medical",
                name="sos_alert_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active",
                "cancelled",
                "marked_safe",
                "expired",
                name="sos_alert_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "approximate_location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeogFromText",
                name="geography",
                spatial_index=True,
            ),
            nullable=False,
        ),
        sa.Column("exact_location_encrypted", sa.String(), nullable=True),
        sa.Column("h3_index", sa.String(), nullable=False),
        sa.Column("radius_meters", sa.Integer(), server_default="2000", nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("marked_safe_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_sos_alerts_status", "sos_alerts", ["status"])

    # 4. Create sos_recipients table
    op.create_table(
        "sos_recipients",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sos_alert_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "delivery_status",
            postgresql.ENUM(
                "pending",
                "sent",
                "failed",
                "skipped",
                name="sos_recipient_delivery_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "response",
            postgresql.ENUM(
                "confirmed",
                "false_alarm",
                "ignored",
                name="sos_recipient_response_enum",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sos_alert_id"], ["sos_alerts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["recipient_user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["device_id"], ["user_devices.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_sos_recipients_sos_alert_id", "sos_recipients", ["sos_alert_id"]
    )

    # 5. Create route_evaluations table
    op.create_table(
        "route_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "origin",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeogFromText",
                name="geography",
                spatial_index=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "destination",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeogFromText",
                name="geography",
                spatial_index=True,
            ),
            nullable=False,
        ),
        sa.Column("selected_route_type", sa.String(), nullable=True),
        sa.Column(
            "fastest_route",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "lower_risk_route",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "balanced_route",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "coverage_status",
            postgresql.ENUM(
                "unavailable",
                "limited",
                "moderate",
                "strong",
                name="coverage_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_route_evaluations_created_at", "route_evaluations", ["created_at"]
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table("route_evaluations")
    op.drop_table("sos_recipients")
    op.drop_table("sos_alerts")
    op.drop_table("incident_reports")

    # Drop custom enums
    op.execute("DROP TYPE sos_recipient_response_enum;")
    op.execute("DROP TYPE sos_recipient_delivery_status_enum;")
    op.execute("DROP TYPE sos_alert_status_enum;")
    op.execute("DROP TYPE sos_alert_type_enum;")
    op.execute("DROP TYPE report_status_enum;")
    op.execute("DROP TYPE report_type_enum;")
