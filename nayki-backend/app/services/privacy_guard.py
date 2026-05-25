from typing import Any

from app.services.safety_engine import get_val


def aggregate_evidence_by_h3(evidence_items: list[Any]) -> list[dict[str, Any]]:
    """Group individual safety evidence records by their H3 index.

    This acts as a privacy guard by aggregating precise incidents into
    standardized hexagonal regions, removing pinpoint incident details.
    """
    aggregations: dict[str, dict[str, Any]] = {}

    for item in evidence_items:
        h3_index = get_val(item, "h3_index")
        if not h3_index:
            continue

        severity = float(get_val(item, "severity", 0.0))
        confidence = float(get_val(item, "confidence", 1.0))
        e_type = get_val(item, "evidence_type")

        if h3_index not in aggregations:
            aggregations[h3_index] = {
                "h3_index": h3_index,
                "evidence_count": 0,
                "total_severity": 0.0,
                "total_confidence": 0.0,
                "evidence_types": set(),
            }

        agg = aggregations[h3_index]
        agg["evidence_count"] += 1
        agg["total_severity"] += severity
        agg["total_confidence"] += confidence
        if e_type:
            agg["evidence_types"].add(str(e_type))

    # Format the return structure cleanly
    result = []
    for h3_index, agg in aggregations.items():
        count = agg["evidence_count"]
        result.append(
            {
                "h3_index": h3_index,
                "evidence_count": count,
                "average_severity": round(agg["total_severity"] / count, 3),
                "average_confidence": round(agg["total_confidence"] / count, 3),
                "evidence_types": list(agg["evidence_types"]),
            }
        )

    return result


def obfuscate_coordinates(latitude: float, longitude: float, precision: int = 3) -> tuple[float, float]:
    """Obfuscate coordinates by rounding to a coarser grid.

    A precision of 3 decimal places hides exact street numbers (~110m).
    """
    return round(latitude, precision), round(longitude, precision)
