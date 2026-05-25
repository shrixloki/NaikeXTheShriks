from app.utils import h3_utils


def test_h3_util_derives_stable_h3_index() -> None:
    """Test that coordinate conversions to H3 cells are consistent, deterministic, and stable."""
    lat, lng = 37.7749, -122.4194  # San Francisco coordinates
    resolution = 9

    # Generate H3 cell repeatedly
    h3_first = h3_utils.lat_lng_to_h3(lat, lng, resolution)
    h3_second = h3_utils.lat_lng_to_h3(lat, lng, resolution)

    # Assert stable output
    assert h3_first == h3_second
    assert isinstance(h3_first, str)
    assert len(h3_first) >= 14  # Standard H3 hex address length

    # Assert hexagonal boundary vertices
    boundary = h3_utils.h3_to_boundary(h3_first)
    assert len(boundary) >= 6

    # Assert hexagonal neighborhood counts (self + 6 adjacent cells = 7)
    neighbors = h3_utils.h3_neighbors(h3_first)
    assert h3_first in neighbors
    assert len(neighbors) == 7
