"""
Test configuration and fixtures for the Alpha Creators Ads backend.
"""

import pytest
import asyncio
from httpx import AsyncClient
from main import app
from core.database import get_db, Base, engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


# Test database URL (use a separate test database)
TEST_DATABASE_URL = "postgresql+asyncpg://alphaads:password@localhost:5432/alphaads_test"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database):
    """Create a test database session."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Create a test client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_social_post():
    """Sample social media post data for testing."""
    return {
        "platform": "twitter",
        "post_id": "1234567890",
        "content": "I love this new product! It's amazing and makes me so happy!",
        "author_id": "user123",
        "author_username": "testuser",
        "posted_at": "2023-01-01T12:00:00Z",
        "engagement_count": 100,
        "likes_count": 50,
        "shares_count": 25,
        "comments_count": 25,
        "hashtags": ["#love", "#amazing"],
        "mentions": ["@brand"],
        "raw_data": {}
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }
