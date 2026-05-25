from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_safety_cell_unavailable_when_no_evidence(
    client: AsyncClient,
) -> None:
    """Test that safety/cell endpoint returns strict 'unavailable' status when no evidence exists."""
    with (
        patch(
            "app.repositories.safety_repo.get_safety_evidence_by_h3_indices"
        ) as mock_evidence,
        patch(
            "app.repositories.safety_repo.get_nearby_help_pois"
        ) as mock_pois,
    ):
        # Setup mocks returning empty databases
        mock_evidence.return_value = []
        mock_pois.return_value = []

        response = await client.get("/safety/cell?lat=37.7749&lng=-122.4194")

        assert response.status_code == 200
        data = response.json()

        # Strict safety checks assertion (Safety Rules)
        assert data["coverage_status"] == "unavailable"
        assert data["confidence_level"] == "low"
        assert data["safety_score"] is None
        assert data["risk_level"] == "unknown"
        assert data["evidence_count"] == 0
        assert "limited_data" in data["risk_reasons"]
