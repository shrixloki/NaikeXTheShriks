
import h3

from app.utils.geo import validate_coordinates


def lat_lng_to_h3(lat: float, lng: float, resolution: int) -> str:
    """Convert latitude/longitude to a unique H3 hexagonal cell index.

    Supports both H3 v3 and v4 API surfaces.
    """
    validate_coordinates(lat, lng)
    if hasattr(h3, "geo_to_h3"):
        # H3 v3 API
        return h3.geo_to_h3(lat, lng, resolution)
    elif hasattr(h3, "latlng_to_cell"):
        # H3 v4 API
        return h3.latlng_to_cell(lat, lng, resolution)
    else:
        # Fallback or older versions
        raise AttributeError("No known H3 conversion function found (geo_to_h3 or latlng_to_cell).")


def h3_to_boundary(h3_index: str) -> list[tuple[float, float]]:
    """Get the geographic boundary coordinates (vertices) of an H3 cell.

    Returns:
        List[Tuple[float, float]]: List of (latitude, longitude) tuples.
    """
    if hasattr(h3, "h3_to_geo_boundary"):
        # H3 v3 API
        return h3.h3_to_geo_boundary(h3_index)
    elif hasattr(h3, "cell_to_boundary"):
        # H3 v4 API
        return h3.cell_to_boundary(h3_index)
    else:
        raise AttributeError("No known H3 boundary function found (h3_to_geo_boundary or cell_to_boundary).")


def h3_neighbors(h3_index: str) -> list[str]:
    """Get the neighboring H3 cell indices of a given cell index (including itself)."""
    if hasattr(h3, "k_ring"):
        # H3 v3 API
        return list(h3.k_ring(h3_index, 1))
    elif hasattr(h3, "grid_disk"):
        # H3 v4 API
        return list(h3.grid_disk(h3_index, 1))
    else:
        raise AttributeError("No known H3 neighbors function found (k_ring or grid_disk).")
