import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import UTC
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.domain.models import User
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db() -> AsyncMock:
    """Mock database session."""
    db = AsyncMock()
    # Stub common execute responses
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result
    return db


@pytest_asyncio.fixture
async def client(mock_db: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing API endpoints."""
    # Override database dependency with mock
    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_user() -> User:
    """Generate a consistent mock User object."""
    import uuid
    from datetime import datetime

    user = User(
        id=uuid.UUID("11111111-2222-3333-4444-555555555555"),
        firebase_uid="firebase_test_uid_123",
        email="test@example.com",
        display_name="Test User",
        phone="+15555555555",
        trust_score=0.5,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return user
