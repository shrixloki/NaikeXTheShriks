import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.domain.models import EmergencyContact
from app.main import app
from app.security.dependencies import get_current_user


@pytest.mark.asyncio
async def test_emergency_contact_crud(
    client: AsyncClient, mock_db: AsyncMock, test_user
) -> None:
    """Test full CRUD lifecycle for Emergency Contacts of an authenticated user."""
    # Authenticate current client request
    app.dependency_overrides[get_current_user] = lambda: test_user

    contact_id = uuid.uuid4()
    mock_contact = EmergencyContact(
        id=contact_id,
        user_id=test_user.id,
        name="Jane Doe",
        phone="+15559998888",
        relationship="Sister",
        is_verified=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # 1. CREATE
    with patch(
        "app.repositories.users_repo.create_emergency_contact"
    ) as mock_create:
        mock_create.return_value = mock_contact

        response = await client.post(
            "/me/emergency-contacts",
            json={
                "name": "Jane Doe",
                "phone": "+15559998888",
                "relationship": "Sister",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["phone"] == "+15559998888"

    # 2. READ
    with patch(
        "app.repositories.users_repo.get_emergency_contacts"
    ) as mock_list:
        mock_list.return_value = [mock_contact]

        response = await client.get("/me/emergency-contacts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Jane Doe"

    # 3. UPDATE
    with (
        patch(
            "app.repositories.users_repo.get_emergency_contact_by_id"
        ) as mock_get,
        patch(
            "app.repositories.users_repo.update_emergency_contact"
        ) as mock_update,
    ):
        mock_get.return_value = mock_contact
        # Mutate contact mock
        mock_contact.relationship = "Sibling"
        mock_update.return_value = mock_contact

        response = await client.put(
            f"/me/emergency-contacts/{contact_id}",
            json={"relationship": "Sibling"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["relationship"] == "Sibling"

    # 4. DELETE
    with (
        patch(
            "app.repositories.users_repo.get_emergency_contact_by_id"
        ) as mock_get,
        patch(
            "app.repositories.users_repo.delete_emergency_contact"
        ) as mock_delete,
    ):
        mock_get.return_value = mock_contact
        mock_delete.return_value = None

        response = await client.delete(f"/me/emergency-contacts/{contact_id}")

        assert response.status_code == 204

    # Teardown dependency overrides
    app.dependency_overrides.clear()
