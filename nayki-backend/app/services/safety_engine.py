from datetime import UTC, datetime
from typing import Any

from app.domain.enums import (
    ConfidenceLevel,
    CoverageStatus,
    EvidenceSource,
    EvidenceType,
    RiskLevel,
)
from app.utils.time import get_freshness_factor, is_night_time


def get_val(obj: Any, attr: str, default: Any = None) -> Any:
    """Helper to safely get attributes from either dicts or object models."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def calculate_segment_risk(
    evidence_items: list[Any],
    time_of_day: datetime | None = None,
    help_distance_meters: float | None = None,
) -> float:
    """Calculate raw risk score based on evidence, time, and nearest help distance.

    Risk starts at a baseline of 0.0 and accumulates based on:
    - Evidence item severity, weighted by confidence and freshness.
    - Night penalty (+0.2) if it's currently night.
    - Isolation penalty (up to +0.2) if nearest help POI is far away (>1000m).
    """
    raw_risk = 0.0

    # 1. Accumulate risk from evidence
    for item in evidence_items:
        severity = float(get_val(item, "severity", 0.0))
        confidence = float(get_val(item, "confidence", 1.0))
        event_time = get_val(item, "event_time")

        # Freshness decays older evidence
        freshness = get_freshness_factor(event_time, max_age_hours=72.0)

        # Severe recent incidents weight heavier
        item_risk = severity * confidence * freshness
        raw_risk += item_risk

    # 2. Night-time risk premium (Night increases risk)
    if is_night_time(time_of_day):
        raw_risk += 0.20

    # 3. Help POI distance penalty (isolated area)
    if help_distance_meters is not None:
        if help_distance_meters > 1000.0:
            # Scale distance penalty linearly between 1000m and 5000m up to 0.20 max
            excess_distance = help_distance_meters - 1000.0
            distance_penalty = min(0.20, excess_distance / 20000.0)
            raw_risk += distance_penalty

    return raw_risk


def normalize_risk(raw_risk: float) -> float:
    """Clamps a raw risk score to the range [0.0, 1.0]."""
    return min(1.0, max(0.0, raw_risk))


def calculate_safety_score(normalized_risk: float) -> float:
    """Computes the safety score, which is strictly the inverse of normalized risk."""
    return 1.0 - normalized_risk


def calculate_confidence(
    evidence_items: list[Any],
    source_diversity: float | None = None,
    freshness: float | None = None,
) -> float:
    """Calculate data confidence from 0.0 to 1.0.

    Confidence metrics:
    - Evidence count (40% weight): scales up with more items.
    - Source diversity (30% weight): number of unique sources.
    - Freshness (30% weight): average freshness of evidence.
    """
    if not evidence_items:
        return 0.0

    # 1. Evidence count component
    count = len(evidence_items)
    count_score = min(1.0, count / 5.0)  # 5+ pieces of evidence max out count score

    # 2. Source diversity component
    if source_diversity is None:
        sources: set[str] = set()
        for item in evidence_items:
            src = get_val(item, "source")
            if src:
                sources.add(str(src))
        source_diversity = min(1.0, len(sources) / 3.0)  # 3+ sources max out diversity

    # 3. Freshness component
    if freshness is None:
        freshness_sum = 0.0
        for item in evidence_items:
            event_time = get_val(item, "event_time")
            freshness_sum += get_freshness_factor(event_time, max_age_hours=72.0)
        freshness = freshness_sum / count

    # Weighted calculation
    confidence = (count_score * 0.4) + (source_diversity * 0.3) + (freshness * 0.3)
    return min(1.0, max(0.0, confidence))


def map_confidence_level(confidence_score: float) -> ConfidenceLevel:
    """Map numeric confidence score to enum ConfidenceLevel."""
    if confidence_score < 0.3:
        return ConfidenceLevel.LOW
    elif confidence_score < 0.7:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.HIGH


def map_risk_level(normalized_risk: float, confidence_score: float) -> RiskLevel:
    """Map risk score to RiskLevel enum. Returns UNKNOWN if confidence is extremely low."""
    if confidence_score < 0.15:
        return RiskLevel.UNKNOWN

    if normalized_risk < 0.35:
        return RiskLevel.LOWER
    elif normalized_risk < 0.70:
        return RiskLevel.MODERATE
    return RiskLevel.HIGHER


def map_coverage_status(
    evidence_items: list[Any], confidence_score: float
) -> CoverageStatus:
    """Determine the spatial data coverage status."""
    if not evidence_items or confidence_score < 0.15:
        return CoverageStatus.UNAVAILABLE
    elif confidence_score < 0.4:
        return CoverageStatus.LIMITED
    elif confidence_score < 0.75:
        return CoverageStatus.MODERATE
    return CoverageStatus.STRONG


def summarize_risk_reasons(
    evidence_items: list[Any],
    time_of_day: datetime | None = None,
    confidence: float = 0.0,
    help_distance_meters: float | None = None,
) -> list[str]:
    """Identify the deterministic reasons explaining the risk profile of a segment.

    Explanations include:
    - poor_lighting: high severity lighting evidence
    - recent_incident: severe incident within 24 hours
    - isolated_road: high severity isolation evidence
    - limited_data: low confidence/count
    - help_far_away: help distance is large (> 1000m)
    - night_time: time is night
    - government_data: municipal/police sources present
    - user_reports_unverified: unverified user reports present
    """
    reasons: list[str] = []

    # 1. Check time of day
    if is_night_time(time_of_day):
        reasons.append("night_time")

    # 2. Check help distance
    if help_distance_meters is not None and help_distance_meters > 1000.0:
        reasons.append("help_far_away")

    # 3. Check data confidence/limits
    if confidence < 0.3 or len(evidence_items) < 2:
        reasons.append("limited_data")

    # 4. Check specific evidence characteristics
    has_gov = False
    has_unverified_user = False
    now = datetime.now(UTC)

    for item in evidence_items:
        severity = float(get_val(item, "severity", 0.0))
        conf = float(get_val(item, "confidence", 1.0))
        src = get_val(item, "source")
        e_type = get_val(item, "evidence_type")
        event_time = get_val(item, "event_time")

        # Government/Police source
        if src in (
            EvidenceSource.GOVERNMENT,
            EvidenceSource.POLICE,
            EvidenceSource.MUNICIPAL,
        ):
            has_gov = True

        # Unverified user report
        if src == EvidenceSource.USER_REPORT and conf < 0.5:
            has_unverified_user = True

        # Lighting issues
        if e_type == EvidenceType.LIGHTING and severity > 0.5:
            if "poor_lighting" not in reasons:
                reasons.append("poor_lighting")

        # Isolated road
        if e_type in (EvidenceType.ISOLATION, EvidenceType.ROAD_TYPE) and severity > 0.5:
            if "isolated_road" not in reasons:
                reasons.append("isolated_road")

        # Recent incidents (severe, within 24 hours)
        if event_time:
            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=UTC)
            age_hours = (now - event_time).total_seconds() / 3600.0
            if age_hours <= 24.0 and severity > 0.4:
                if "recent_incident" not in reasons:
                    reasons.append("recent_incident")

    if has_gov and "government_data" not in reasons:
        reasons.append("government_data")

    if has_unverified_user and "user_reports_unverified" not in reasons:
        reasons.append("user_reports_unverified")

    return reasons


def extract_h3_cells_for_route(route_geometry: dict) -> list[str]:
    """Extract unique H3 cell indices that intersect with the route geometry.

    Expects route_geometry to be a GeoJSON LineString dictionary.
    """
    from app.config import settings
    from app.utils.h3_utils import lat_lng_to_h3

    resolution = settings.H3_RESOLUTION
    coords = route_geometry.get("coordinates", [])
    if not coords:
        return []

    h3_cells = []
    seen = set()
    for coord in coords:
        if len(coord) >= 2:
            lng, lat = coord[0], coord[1]
            try:
                h3_idx = lat_lng_to_h3(lat, lng, resolution)
                if h3_idx and h3_idx not in seen:
                    seen.add(h3_idx)
                    h3_cells.append(h3_idx)
            except Exception:
                continue
    return h3_cells


def calculate_route_risk(
    segment_or_cell_scores: list[float], severe_incident_count: int = 0
) -> float:
    """Calculate aggregate route risk score.

    Risk is averaged across segments/cells, but cells with high risk get extra penalty
    to reflect routing away from concentrated danger areas.
    Severe recent incidents also add direct penalties.
    """
    if not segment_or_cell_scores:
        return 0.0

    avg_risk = sum(segment_or_cell_scores) / len(segment_or_cell_scores)

    # Red-segment penalty: add premium if any segment has extremely high risk (> 0.6)
    high_risk_premium = 0.0
    for score in segment_or_cell_scores:
        if score > 0.6:
            high_risk_premium += 0.1

    # Severe recent incident penalty
    incident_penalty = severe_incident_count * 0.15

    total_risk = avg_risk + min(0.3, high_risk_premium) + incident_penalty
    return min(1.0, max(0.0, total_risk))


def calculate_route_confidence(evidence_items: list[Any]) -> float:
    """Calculate aggregate data confidence across all evidence intersecting the route."""
    if not evidence_items:
        return 0.0
    return calculate_confidence(evidence_items)


def generate_route_explanation(reasons: list[str], confidence: float) -> str:
    """Generate professional explanation highlighting route safety observations."""
    if confidence < 0.25:
        return (
            "Low confidence due to insufficient safety evidence. "
            "Returning unavailable status; do not treat as a safety guarantee."
        )

    parts = []
    if "night_time" in reasons:
        parts.append("night-time risk penalty applied")
    if "recent_incident" in reasons:
        parts.append("severe recent incidents detected along route")
    if "poor_lighting" in reasons:
        parts.append("reports of poor lighting in segments")
    if "isolated_road" in reasons:
        parts.append("isolated transit lanes identified")

    if not parts:
        return (
            "Baseline risk evaluation. Route is characterized by standard coverage, "
            "showing lower-risk parameters."
        )

    return (
        f"Route evaluation notes: {', '.join(parts)}. "
        "Evaluated as lower-risk or moderate-risk depending on dynamic conditions."
    )


def evaluate_route(
    route_geometry: dict,
    departure_time: datetime | None = None,
    evidence_items: list[Any] = None,
) -> dict:
    """Evaluate full route coordinates against spatial evidence.

    Returns route breakdown containing safety score, confidence, risk levels, and reasons.
    If no evidence exists, safety_score is null and confidence is low.
    """
    if evidence_items is None:
        evidence_items = []

    # 1. Extract route H3 cells
    route_cells = extract_h3_cells_for_route(route_geometry)

    # 2. Filter evidence belonging to our route cells
    cell_set = set(route_cells)
    route_evidence = []
    severe_incidents = 0
    now = datetime.now(UTC)

    for item in evidence_items:
        h3_idx = get_val(item, "h3_index")
        if h3_idx in cell_set:
            route_evidence.append(item)

            # Count severe recent incidents (crime within 24 hours, severity > 0.6)
            severity = float(get_val(item, "severity", 0.0))
            event_time = get_val(item, "event_time")
            if event_time:
                if event_time.tzinfo is None:
                    event_time = event_time.replace(tzinfo=UTC)
                age_hours = (now - event_time).total_seconds() / 3600.0
                if age_hours <= 24.0 and severity > 0.6:
                    severe_incidents += 1

    # 3. If no evidence intersects, return low confidence / unavailable
    if not route_evidence:
        night_risk = 0.20 if is_night_time(departure_time) else 0.0
        return {
            "safety_score": None,
            "confidence_score": 0.0,
            "confidence_level": ConfidenceLevel.LOW,
            "risk_level": RiskLevel.UNKNOWN,
            "coverage_status": CoverageStatus.UNAVAILABLE,
            "risk_reasons": ["limited_data"]
            + (["night_time"] if night_risk > 0 else []),
            "explanation": (
                "No localized safety evidence available for this route. "
                "Returning unavailable status; do not assume safety."
            ),
            "evidence_count": 0,
        }

    # 4. Compute cell-by-cell risk
    cell_scores = []
    for cell in route_cells:
        cell_ev = [e for e in route_evidence if get_val(e, "h3_index") == cell]
        c_risk = calculate_segment_risk(cell_ev, time_of_day=departure_time)
        cell_scores.append(normalize_risk(c_risk))

    # 5. Compute route metrics
    route_raw_risk = calculate_route_risk(cell_scores, severe_incidents)
    route_confidence = calculate_route_confidence(route_evidence)

    # Night-time risk premium (Night increases risk)
    if is_night_time(departure_time):
        route_raw_risk = min(1.0, route_raw_risk + 0.20)

    norm_risk = normalize_risk(route_raw_risk)
    safety_score = calculate_safety_score(norm_risk)

    conf_level = map_confidence_level(route_confidence)
    risk_level = map_risk_level(norm_risk, route_confidence)
    coverage = map_coverage_status(route_evidence, route_confidence)
    reasons = summarize_risk_reasons(
        route_evidence, time_of_day=departure_time, confidence=route_confidence
    )

    return {
        "safety_score": round(safety_score, 4) if safety_score is not None else None,
        "confidence_score": round(route_confidence, 4),
        "confidence_level": conf_level,
        "risk_level": risk_level,
        "coverage_status": coverage,
        "risk_reasons": reasons,
        "explanation": generate_route_explanation(reasons, route_confidence),
        "evidence_count": len(route_evidence),
    }
