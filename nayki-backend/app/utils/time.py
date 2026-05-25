from datetime import UTC, datetime, time


def is_night_time(dt: datetime | None = None) -> bool:
    """Determine if a given datetime (or the current time if None) is during the night.

    Night is defined as 20:00 (8:00 PM) to 06:00 (6:00 AM).
    """
    if dt is None:
        dt = datetime.now(UTC)

    # Convert to time object
    current_time = dt.time()

    start_night = time(20, 0, 0)
    end_night = time(6, 0, 0)

    if start_night <= current_time or current_time <= end_night:
        return True
    return False


def get_freshness_factor(
    event_time: datetime | None, max_age_hours: float = 72.0
) -> float:
    """Calculate a freshness score between 0.0 (old/stale) and 1.0 (extremely fresh).

    If no event_time is provided, return 0.5 (medium freshness).
    """
    if not event_time:
        return 0.5

    # Ensure timezone aware comparison
    now = datetime.now(UTC)
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=UTC)

    age_seconds = (now - event_time).total_seconds()
    age_hours = max(0.0, age_seconds / 3600.0)

    if age_hours >= max_age_hours:
        return 0.0

    # Linear decay
    return 1.0 - (age_hours / max_age_hours)
