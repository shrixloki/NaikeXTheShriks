import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.config import settings
from app.domain.enums import (
    ReportStatus,
    ReportType,
    SosAlertStatus,
    SosAlertType,
    SosRecipientDeliveryStatus,
)
from app.domain.models import (
    IncidentReport,
    SosAlert,
    UserDevice,
)
from app.main import app
from app.security.dependencies import get_current_user
from app.services import safety_engine


@pytest.fixture
def authenticate_user(test_user):
    """Authenticate tests by overriding get_current_user injection."""
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield test_user
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_incident_report_creation_derives_h3_index(
    client: AsyncClient, mock_db: AsyncMock, authenticate_user
) -> None:
    """Test 1: incident report creation derives stable h3 index correctly."""
    # Stub DB save response
    mock_report = IncidentReport(
        id=uuid.uuid4(),
        user_id=authenticate_user.id,
        report_type=ReportType.POOR_LIGHTING,
        description="Dark street",
        location=None,
        h3_index="8928308280fffff",
        status=ReportStatus.SUBMITTED,
        confidence=0.25,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    
    with patch(
        "app.repositories.incidents_repo.create_incident_report"
    ) as mock_create:
        mock_create.return_value = mock_report

        response = await client.post(
            "/reports",
            json={
                "lat": 37.7749,
                "lng": -122.4194,
                "report_type": "poor_lighting",
                "description": "Dark street",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["h3_index"] != ""
        assert len(data["h3_index"]) >= 14


@pytest.mark.asyncio
async def test_incident_report_starts_as_submitted_and_low_confidence(
    client: AsyncClient, mock_db: AsyncMock, authenticate_user
) -> None:
    """Test 2: incident report starts as submitted and carries low confidence parameters."""
    mock_report = IncidentReport(
        id=uuid.uuid4(),
        user_id=authenticate_user.id,
        report_type=ReportType.ACCIDENT,
        description="Crash",
        location=None,
        h3_index="8928308280fffff",
        status=ReportStatus.SUBMITTED,
        confidence=0.25,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with patch(
        "app.repositories.incidents_repo.create_incident_report"
    ) as mock_create:
        mock_create.return_value = mock_report

        response = await client.post(
            "/reports",
            json={
                "lat": 37.7749,
                "lng": -122.4194,
                "report_type": "accident",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "submitted"
        assert data["confidence"] == 0.25


@pytest.mark.asyncio
async def test_routes_compare_degraded_if_graphhopper_disabled(
    client: AsyncClient, authenticate_user
) -> None:
    """Test 3: routes/compare returns degraded error if GraphHopper disabled."""
    with patch.object(settings, "GRAPHHOPPER_BASE_URL", None):
        response = await client.post(
            "/routes/compare",
            json={
                "origin": {"lat": 37.7749, "lng": -122.4194},
                "destination": {"lat": 37.7849, "lng": -122.4094},
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert "degraded" in data["detail"].lower()


@pytest.mark.asyncio
async def test_routes_compare_does_not_fabricate_safety_score_when_evidence_unavailable(
    client: AsyncClient, mock_db: AsyncMock, authenticate_user
) -> None:
    """Test 4: routes/compare does not fabricate safety score when evidence unavailable."""
    with (
        patch(
            "app.integrations.graphhopper_client.GraphHopperClient.is_enabled"
        ) as mock_enabled,
        patch(
            "app.integrations.graphhopper_client.GraphHopperClient.get_candidate_routes"
        ) as mock_gh,
        patch(
            "app.repositories.safety_repo.get_safety_evidence_by_h3_indices"
        ) as mock_ev,
        patch(
            "app.repositories.routes_repo.create_route_evaluation"
        ) as mock_create_eval,
    ):
        mock_enabled.return_value = True
        # Stub GraphHopper response
        mock_gh.return_value = [
            {
                "route_type": "fastest",
                "distance_meters": 1000.0,
                "duration_seconds": 600.0,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-122.4194, 37.7749], [-122.4094, 37.7849]],
                },
                "instructions": ["Walk north"],
            }
        ]
        # Empty safety database
        mock_ev.return_value = []
        mock_create_eval.return_value = None

        response = await client.post(
            "/routes/compare",
            json={
                "origin": {"lat": 37.7749, "lng": -122.4194},
                "destination": {"lat": 37.7849, "lng": -122.4094},
            },
        )

        assert response.status_code == 200
        data = response.json()
        
        # Verify no fake safety claims
        assert data["coverage_status"] == "unavailable"
        assert data["fastest_route"]["safety_score"] is None
        assert data["fastest_route"]["confidence_level"] == "low"


def test_safety_engine_severe_recent_incident_increases_route_penalty() -> None:
    """Test 5: safety engine severe recent incident increases route penalty."""
    # Base risk list
    cell_scores = [0.1, 0.2, 0.1]
    
    # 0 incidents vs 2 severe recent incidents
    base_risk = safety_engine.calculate_route_risk(cell_scores, severe_incident_count=0)
    high_risk = safety_engine.calculate_route_risk(cell_scores, severe_incident_count=2)

    assert high_risk > base_risk
    # Each severe incident adds 0.15 premium
    assert high_risk == min(1.0, base_risk + 0.3)


def test_safety_engine_low_evidence_returns_low_confidence() -> None:
    """Test 6: safety engine low evidence returns low confidence."""
    confidence = safety_engine.calculate_route_confidence([])
    assert confidence == 0.0


@pytest.mark.asyncio
async def test_sos_creation_stores_alert(
    client: AsyncClient, mock_db: AsyncMock, authenticate_user
) -> None:
    """Test 7: SOS creation triggers and stores active emergency alert."""
    with (
        patch("app.repositories.sos_repo.create_sos_alert") as mock_create_sos,
        patch("app.repositories.sos_repo.create_sos_recipient") as mock_create_recip,
    ):
        mock_create_sos.return_value = None
        mock_create_recip.return_value = None

        response = await client.post(
            "/sos",
            json={"lat": 37.7749, "lng": -122.4194, "alert_type": "sos"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"
        assert data["recipient_count"] == 0
        assert data["approximate_lat"] == 37.775  # rounded coordinates


@pytest.mark.asyncio
async def test_sos_creation_stores_recipients_when_nearby_devices_exist(
    client: AsyncClient, mock_db: AsyncMock, authenticate_user
) -> None:
    """Test 8: SOS creation triggers and records recipients when nearby active devices exist."""
    # Mock active nearby device in DB
    mock_device = UserDevice(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        fcm_token="token_recipient_fcm",
        platform="android",
        last_seen_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )

    # Stub executing select device stmt
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_device]
    mock_db.execute.return_value = mock_result

    with (
        patch("app.repositories.sos_repo.create_sos_alert") as mock_create_sos,
        patch("app.repositories.sos_repo.create_sos_recipient") as mock_create_recip,
    ):
        mock_create_sos.return_value = None
        mock_create_recip.return_value = None

        response = await client.post(
            "/sos",
            json={"lat": 37.7749, "lng": -122.4194, "alert_type": "accident"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["recipient_count"] == 1


@pytest.mark.asyncio
async def test_sos_does_not_claim_push_sent_when_fcm_disabled(
    client: AsyncClient, mock_db: AsyncMock, authenticate_user
) -> None:
    """Test 9: SOS creation sets delivery status to skipped and does not falsely claim push delivery when FCM disabled."""
    mock_device = UserDevice(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        fcm_token="token_recipient_fcm",
        platform="android",
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_device]
    mock_db.execute.return_value = mock_result

    with (
        patch("app.repositories.sos_repo.create_sos_alert") as mock_create_sos,
        patch("app.repositories.sos_repo.create_sos_recipient") as mock_create_recip,
        patch.object(settings, "FCM_SERVER_KEY", None),  # disable FCM
    ):
        mock_create_sos.return_value = None
        
        # Verify created recipient status is set to SKIPPED
        captured_recipients = []
        async def fake_create_recip(db, recip):
            captured_recipients.append(recip)
            return recip
        mock_create_recip.side_effect = fake_create_recip

        response = await client.post(
            "/sos",
            json={"lat": 37.7749, "lng": -122.4194, "alert_type": "medical"},
        )

        assert response.status_code == 201
        assert len(captured_recipients) == 1
        assert captured_recipients[0].delivery_status == SosRecipientDeliveryStatus.SKIPPED


@pytest.mark.asyncio
async def test_sos_cancel_works(
    client: AsyncClient, mock_db: MagicMock, authenticate_user
) -> None:
    """Test 10: SOS cancel updates trigger parameters and sets status cancelled."""
    mock_alert = SosAlert(
        id=uuid.uuid4(),
        user_id=authenticate_user.id,
        alert_type=SosAlertType.SOS,
        status=SosAlertStatus.ACTIVE,
        approximate_location=None,
        h3_index="8928308280fffff",
        triggered_at=datetime.now(UTC),
        expires_at=datetime.now(UTC),
    )

    with (
        patch("app.repositories.sos_repo.get_sos_alert_by_id") as mock_get,
        patch("app.repositories.sos_repo.update_sos_alert") as mock_update,
    ):
        mock_get.return_value = mock_alert
        mock_update.return_value = mock_alert

        response = await client.post(f"/sos/{mock_alert.id}/cancel")

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert mock_alert.status == SosAlertStatus.CANCELLED
        assert mock_alert.cancelled_at is not None


@pytest.mark.asyncio
async def test_sos_mark_safe_works(
    client: AsyncClient, mock_db: MagicMock, authenticate_user
) -> None:
    """Test 11: SOS mark safe resolves alert and updates status."""
    mock_alert = SosAlert(
        id=uuid.uuid4(),
        user_id=authenticate_user.id,
        alert_type=SosAlertType.SOS,
        status=SosAlertStatus.ACTIVE,
        approximate_location=None,
        h3_index="8928308280fffff",
        triggered_at=datetime.now(UTC),
        expires_at=datetime.now(UTC),
    )

    with (
        patch("app.repositories.sos_repo.get_sos_alert_by_id") as mock_get,
        patch("app.repositories.sos_repo.update_sos_alert") as mock_update,
    ):
        mock_get.return_value = mock_alert
        mock_update.return_value = mock_alert

        response = await client.post(f"/sos/{mock_alert.id}/mark-safe")

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert mock_alert.status == SosAlertStatus.MARKED_SAFE
        assert mock_alert.marked_safe_at is not None


@pytest.mark.asyncio
async def test_privacy_export_returns_user_records(
    client: AsyncClient, mock_db: AsyncMock, authenticate_user
) -> None:
    """Test 12: GDPR privacy export returns collated user records and details."""
    with (
        patch("app.repositories.users_repo.get_emergency_contacts") as mock_ec,
        patch("app.repositories.incidents_repo.get_user_incident_reports") as mock_rep,
    ):
        mock_ec.return_value = []
        mock_rep.return_value = []

        response = await client.get("/privacy/export")

        assert response.status_code == 200
        data = response.json()
        assert "profile" in data
        assert data["profile"]["email"] == authenticate_user.email
        assert "emergency_contacts" in data
        assert "incident_reports" in data


@pytest.mark.asyncio
async def test_account_delete_soft_deletes_user_and_disables_devices(
    client: AsyncClient, mock_db: AsyncMock, authenticate_user
) -> None:
    """Test 13: GDPR account deletion soft-deletes user profile and revokes device tokens."""
    # Stub active device lookup
    mock_device = UserDevice(id=uuid.uuid4(), user_id=authenticate_user.id, fcm_token="tkn")
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_device]
    mock_db.execute.return_value = mock_result

    response = await client.delete("/privacy/account")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Assert soft-delete indicators
    assert authenticate_user.deleted_at is not None
    assert authenticate_user.display_name == "[REDACTED]"
    assert authenticate_user.email is None
    
    # Assert device deleted
    mock_db.delete.assert_called_once_with(mock_device)


@pytest.mark.asyncio
async def test_places_help_returns_unavailable_coverage_if_no_provider_and_no_data(
    client: AsyncClient, mock_db: AsyncMock
) -> None:
    """Test 14: places/help returns unavailable coverage if no integration configured and empty DB."""
    with (
        patch("app.repositories.safety_repo.get_nearby_help_pois") as mock_pois,
        patch.object(settings, "GOOGLE_PLACES_API_KEY", None),  # Disable API key
    ):
        mock_pois.return_value = []

        response = await client.get("/places/help?lat=37.7749&lng=-122.4194&type=police")

        assert response.status_code == 200
        data = response.json()
        assert data["coverage_status"] == "unavailable"
        assert len(data["pois"]) == 0
