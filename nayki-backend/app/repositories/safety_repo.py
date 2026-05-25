from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import CoverageStatus
from app.domain.models import HelpPoi, SafetyCell, SafetyEvidence


async def get_safety_cell_by_h3(
    db: AsyncSession, h3_index: str
) -> SafetyCell | None:
    """Retrieve aggregate safety cell details for an H3 index."""
    result = await db.execute(
        select(SafetyCell).where(SafetyCell.h3_index == h3_index)
    )
    return result.scalars().first()


async def create_safety_cell(
    db: AsyncSession,
    h3_index: str,
    city: str | None = None,
    risk_score: float | None = None,
    safety_score: float | None = None,
    confidence: float = 0.0,
    coverage_status: CoverageStatus = CoverageStatus.UNAVAILABLE,
) -> SafetyCell:
    """Create a new SafetyCell for H3 tracking."""
    cell = SafetyCell(
        h3_index=h3_index,
        city=city,
        risk_score=risk_score,
        safety_score=safety_score,
        confidence=confidence,
        coverage_status=coverage_status,
    )
    db.add(cell)
    await db.commit()
    await db.refresh(cell)
    return cell


async def update_safety_cell(
    db: AsyncSession, cell: SafetyCell, update_data: dict
) -> SafetyCell:
    """Update SafetyCell aggregated metrics."""
    for key, value in update_data.items():
        if hasattr(cell, key):
            setattr(cell, key, value)
    cell.last_computed_at = func.now()
    await db.commit()
    await db.refresh(cell)
    return cell


async def get_safety_evidence_by_h3_indices(
    db: AsyncSession, h3_indices: list[str]
) -> list[SafetyEvidence]:
    """Retrieve all safety evidence items intersecting a set of H3 indices."""
    if not h3_indices:
        return []
    result = await db.execute(
        select(SafetyEvidence).where(SafetyEvidence.h3_index.in_(h3_indices))
    )
    return list(result.scalars().all())


async def create_safety_evidence(
    db: AsyncSession,
    source: str,
    evidence_type: str,
    severity: float,
    confidence: float,
    h3_index: str | None = None,
    event_time: object | None = None,
    expires_at: object | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    metadata: dict | None = None,
) -> SafetyEvidence:
    """Ingest a new piece of safety evidence into the database."""
    # Create PostGIS Geography point if lat/lng are provided
    location_geog = None
    if latitude is not None and longitude is not None:
        location_geog = f"SRID=4326;POINT({longitude} {latitude})"

    evidence = SafetyEvidence(
        h3_index=h3_index,
        source=source,
        evidence_type=evidence_type,
        severity=severity,
        confidence=confidence,
        event_time=event_time,
        expires_at=expires_at,
        location=location_geog,
        evidence_metadata=metadata or {},
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)
    return evidence


async def get_nearby_evidence(
    db: AsyncSession,
    latitude: float,
    longitude: float,
    radius_meters: float,
) -> list[SafetyEvidence]:
    """Retrieve safety evidence within a specific geographic radius of a point.

    Uses PostGIS spatial queries.
    """
    # Create a WKT geography point representation (longitude first)
    point_wkt = f"SRID=4326;POINT({longitude} {latitude})"

    # Select evidence where distance is within radius_meters
    # Use ST_DWithin on the Geography column
    result = await db.execute(
        select(SafetyEvidence)
        .where(
            func.ST_DWithin(
                SafetyEvidence.location,
                func.ST_GeogFromText(point_wkt),
                radius_meters,
            )
        )
    )
    return list(result.scalars().all())


async def get_nearby_help_pois(
    db: AsyncSession,
    latitude: float,
    longitude: float,
    radius_meters: float,
) -> list[HelpPoi]:
    """Retrieve POIs (Police, Hospitals) within a radius for emergency routing."""
    point_wkt = f"SRID=4326;POINT({longitude} {latitude})"
    result = await db.execute(
        select(HelpPoi).where(
            func.ST_DWithin(
                HelpPoi.location, func.ST_GeogFromText(point_wkt), radius_meters
            )
        )
    )
    return list(result.scalars().all())
