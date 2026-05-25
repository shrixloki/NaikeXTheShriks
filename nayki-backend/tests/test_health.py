from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient, mock_db: AsyncMock) -> None:
    """Test that the /health endpoint correctly returns DB and Redis health status."""
    # Mock Redis connection and ping to succeed
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.ping.return_value = True
        mock_from_url.return_value = mock_redis_client

        # Mock DB select 1 to succeed
        mock_db.execute.return_value = AsyncMock()

        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "redis" in data
        assert data["database"] == "healthy"
        assert data["redis"] == "healthy"
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_endpoint_degraded(client: AsyncClient, mock_db: AsyncMock) -> None:
    """Test that /health returns degraded when dependencies are down."""
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.ping.side_effect = Exception("Redis connection refused")
        mock_from_url.return_value = mock_redis_client

        # Mock DB select 1 to fail
        mock_db.execute.side_effect = Exception("DB connection timeout")

        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "unhealthy"
        assert data["redis"] == "unhealthy"

