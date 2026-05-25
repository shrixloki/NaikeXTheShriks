import math

from app.domain.errors import ValidationError


def validate_coordinates(latitude: float, longitude: float) -> None:
    """Validate that coordinates are within realistic ranges.

    Raises:
        ValidationError: If latitude is not between -90 and 90, or
                         longitude is not between -180 and 180.
    """
    if not (-90.0 <= latitude <= 90.0):
        raise ValidationError(
            f"Invalid latitude {latitude}. Must be between -90 and 90."
        )
    if not (-180.0 <= longitude <= 180.0):
        raise ValidationError(
            f"Invalid longitude {longitude}. Must be between -180 and 180."
        )


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculate the great-circle distance between two points on the Earth's surface.

    Returns the distance in meters.
    """
    validate_coordinates(lat1, lon1)
    validate_coordinates(lat2, lon2)

    # Earth radius in meters
    R = 6371000.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c
