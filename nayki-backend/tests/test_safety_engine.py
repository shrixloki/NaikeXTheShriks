from datetime import UTC, datetime, timedelta

from app.services import safety_engine


def test_night_increases_risk() -> None:
    """Test that night time adds a strict risk penalty compared to day time."""
    day_time = datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC)
    night_time = datetime(2026, 5, 22, 23, 0, 0, tzinfo=UTC)

    # Empty evidence list
    evidence = []

    day_risk = safety_engine.calculate_segment_risk(evidence, time_of_day=day_time)
    night_risk = safety_engine.calculate_segment_risk(evidence, time_of_day=night_time)

    # Night risk must carry the 0.20 premium
    assert night_risk > day_risk
    assert night_risk == 0.20
    assert day_risk == 0.0


def test_missing_evidence_returns_low_confidence() -> None:
    """Test that empty evidence lists evaluate strictly to zero confidence."""
    evidence = []
    confidence = safety_engine.calculate_confidence(evidence)
    assert confidence == 0.0


def test_severe_recent_incident_increases_risk() -> None:
    """Test that a recent severe incident carries significantly higher risk than a decayed historical one."""
    now = datetime.now(UTC)

    recent_incident = {
        "severity": 0.9,
        "confidence": 0.8,
        "event_time": now - timedelta(hours=2),
        "source": "police",
    }

    old_incident = {
        "severity": 0.9,
        "confidence": 0.8,
        "event_time": now - timedelta(days=5),  # Beyond 72 hours max_age
        "source": "police",
    }

    recent_risk = safety_engine.calculate_segment_risk([recent_incident], time_of_day=now)
    old_risk = safety_engine.calculate_segment_risk([old_incident], time_of_day=now)

    # Recent risk must be higher
    assert recent_risk > old_risk

    # Decayed historical evidence beyond limit should contribute 0 risk
    assert old_risk == 0.0
