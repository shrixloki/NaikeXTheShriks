from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.config import settings


@pytest.mark.asyncio
async def test_dev_auth_session_creation(
    client: AsyncClient, mock_db: AsyncMock, test_user
) -> None:
    """Test successful dev session creation in local environment with DEV_AUTH_ENABLED=True."""
    with (
        patch.object(settings, "APP_ENV", "local"),
        patch.object(settings, "DEV_AUTH_ENABLED", True),
    ):
        # Stub the DB query to return the test user
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = test_user
        mock_db.execute.return_value = mock_result

        # Request session using dev token
        response = await client.post(
            "/auth/session", json={"dev_token": "dev_john"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "session_metadata" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["session_metadata"]["dev_mode_active"] is True
        assert data["session_metadata"]["env"] == "local"


@pytest.mark.asyncio
async def test_production_rejects_dev_auth(
    client: AsyncClient, mock_db: AsyncMock
) -> None:
    """Test that dev authentication is strictly rejected in production (or when DEV_AUTH_ENABLED is False)."""
    with (
        patch.object(settings, "APP_ENV", "production"),
        patch.object(settings, "DEV_AUTH_ENABLED", False),
    ):
        # Dev token request in production env
        response = await client.post(
            "/auth/session", json={"dev_token": "dev_john"}
        )

        # Rejects with Unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
