"""initial migration

Revision ID: 001_initial
Revises: None
Create Date: 2026-05-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create PostGIS Enums
    op.execute(
        "CREATE TYPE help_poi_type_enum AS ENUM ('police', 'hospital', 'pharmacy', 'public_place', 'transit', 'other');"
    )
    op.execute(
        "CREATE TYPE coverage_status_enum AS ENUM ('unavailable', 'limited', 'moderate', 'strong');"
    )
    op.execute(
        "CREATE TYPE evidence_source_enum AS ENUM ('government', 'police', 'municipal', 'osm', 'user_report', 'verified_partner', 'system');"
    )
    op.execute(
        "CREATE TYPE evidence_type_enum AS ENUM ('crime', 'lighting', 'incident', 'road_type', 'isolation', 'help_distance', 'crowd_proxy', 'sos_density');"
    )

    # 2. Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("firebase_uid", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column(
            "trust_score",
            sa.Numeric(precision=3, scale=2),
            server_default="0.5",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("firebase_uid"),
    )

    # 3. Create user_devices table
    op.create_table(
        "user_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fcm_token", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("device_model", sa.String(), nullable=True),
        sa.Column("app_version", sa.String(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_user_devices_fcm_token", "user_devices", ["fcm_token"]
    )
    op.create_index(
        "idx_user_devices_created_at", "user_devices", ["created_at"]
    )

    # 4. Create emergency_contacts table
    op.create_table(
        "emergency_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("relationship", sa.String(), nullable=True),
        sa.Column(
            "is_verified", sa.Boolean(), server_default="false", nullable=False
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 5. Create help_pois table with PostGIS Geography Point column
    op.create_table(
        "help_pois",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("source_ref", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "type",
            postgresql.ENUM(
                "police",
                "hospital",
                "pharmacy",
                "public_place",
                "transit",
                "other",
                name="help_poi_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
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
        sa.Column("open_status", sa.String(), nullable=True),
        sa.Column(
            "confidence",
            sa.Numeric(precision=3, scale=2),
            server_default="0.5",
            nullable=False,
        ),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # 6. Create safety_cells table
    op.create_table(
        "safety_cells",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("h3_index", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column(
            "risk_score", sa.Numeric(precision=5, scale=4), nullable=True
        ),
        sa.Column(
            "safety_score", sa.Numeric(precision=5, scale=4), nullable=True
        ),
        sa.Column(
            "confidence",
            sa.Numeric(precision=3, scale=2),
            server_default="0.0",
            nullable=False,
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
        sa.Column("last_computed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("h3_index"),
    )
    op.create_index("idx_safety_cells_h3_index", "safety_cells", ["h3_index"])

    # 7. Create safety_evidence table with PostGIS Geography Point column
    op.create_table(
        "safety_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("h3_index", sa.String(), nullable=True),
        sa.Column(
            "source",
            postgresql.ENUM(
                "government",
                "police",
                "municipal",
                "osm",
                "user_report",
                "verified_partner",
                "system",
                name="evidence_source_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "evidence_type",
            postgresql.ENUM(
                "crime",
                "lighting",
                "incident",
                "road_type",
                "isolation",
                "help_distance",
                "crowd_proxy",
                "sos_density",
                name="evidence_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "severity", sa.Numeric(precision=3, scale=2), nullable=False
        ),
        sa.Column(
            "confidence", sa.Numeric(precision=3, scale=2), nullable=False
        ),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeogFromText",
                name="geography",
                spatial_index=True,
            ),
            nullable=True,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_safety_evidence_h3_index", "safety_evidence", ["h3_index"]
    )
    op.create_index(
        "idx_safety_evidence_created_at", "safety_evidence", ["created_at"]
    )

    # 8. Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip_hash", sa.String(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    # Drop tables
    op.drop_table("audit_logs")
    op.drop_table("safety_evidence")
    op.drop_table("safety_cells")
    op.drop_table("help_pois")
    op.drop_table("emergency_contacts")
    op.drop_table("user_devices")
    op.drop_table("users")

    # Drop custom enums
    op.execute("DROP TYPE evidence_type_enum;")
    op.execute("DROP TYPE evidence_source_enum;")
    op.execute("DROP TYPE coverage_status_enum;")
    op.execute("DROP TYPE help_poi_type_enum;")
