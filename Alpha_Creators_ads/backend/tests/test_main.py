"""
Comprehensive test suite for the Alpha Creators Ads backend system.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json
import uuid

# Import the main application and dependencies
from main import app
from core.database import get_db_session, Base
from core.config import settings
from services.authentication import create_access_token
from models import User, Campaign, AdCreative, SocialMediaPost


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db_session dependency."""
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email="test@example.com",
        username="testuser",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        is_advertiser=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_campaign(db_session, test_user):
    """Create a test campaign."""
    campaign_id = str(uuid.uuid4())
    campaign = Campaign(
        id=campaign_id,
        name="Test Campaign",
        description="A test campaign for unit testing",
        owner_id=test_user.id,
        target_audience={"age": "25-35", "interests": ["technology"]},
        budget=1000.0,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(campaign)
    await db_session.commit()
    await db_session.refresh(campaign)
    return campaign


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test requests."""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Alpha Creators Ads API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "active"
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data


class TestUserEndpoints:
    """Test user management endpoints."""
    
    def test_user_registration(self, client):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "is_advertiser": True
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["is_advertiser"] == user_data["is_advertiser"]
        assert "id" in data
    
    def test_user_login(self, client, test_user):
        """Test user login."""
        login_data = {
            "username": test_user.email,
            "password": "secret"
        }
        
        response = client.post("/api/v1/users/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user information."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email


class TestCampaignEndpoints:
    """Test campaign management endpoints."""
    
    def test_create_campaign(self, client, auth_headers):
        """Test campaign creation."""
        campaign_data = {
            "name": "New Test Campaign",
            "description": "A new campaign for testing",
            "target_audience": {"age": "25-35", "interests": ["technology"]},
            "budget": 1500.0,
            "start_date": "2024-01-15T00:00:00",
            "end_date": "2024-02-15T00:00:00"
        }
        
        response = client.post("/api/v1/campaigns/", json=campaign_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == campaign_data["name"]
        assert data["budget"] == campaign_data["budget"]
        assert "id" in data
    
    def test_get_campaigns(self, client, auth_headers, test_campaign):
        """Test getting user campaigns."""
        response = client.get("/api/v1/campaigns/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(campaign["id"] == test_campaign.id for campaign in data)
    
    def test_get_campaign_by_id(self, client, auth_headers, test_campaign):
        """Test getting a specific campaign."""
        response = client.get(f"/api/v1/campaigns/{test_campaign.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_campaign.id
        assert data["name"] == test_campaign.name


class TestAnalyticsEndpoints:
    """Test analytics endpoints."""
    
    def test_performance_overview(self, client, auth_headers):
        """Test getting performance overview."""
        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_campaigns" in data
        assert "total_impressions" in data
        assert "average_ctr" in data
    
    def test_campaign_analytics(self, client, auth_headers):
        """Test getting campaign analytics."""
        response = client.get("/api/v1/analytics/campaigns", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_audience_insights(self, client, auth_headers):
        """Test getting audience insights."""
        response = client.get("/api/v1/analytics/audience", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "age_groups" in data
        assert "genders" in data
        assert "locations" in data


class TestNLPEndpoints:
    """Test NLP and sentiment analysis endpoints."""
    
    def test_analyze_text(self, client, auth_headers):
        """Test text sentiment analysis."""
        analysis_data = {
            "text": "This is an amazing product that I absolutely love!",
            "analyze_emotions": True,
            "extract_entities": True
        }
        
        response = client.post("/api/v1/nlp/analyze", json=analysis_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert "emotions" in data
        assert "entities" in data
        assert data["sentiment"]["sentiment"] in ["positive", "negative", "neutral"]
    
    def test_batch_analyze(self, client, auth_headers):
        """Test batch text analysis."""
        batch_data = {
            "texts": [
                "I love this product!",
                "This is terrible.",
                "It's okay, nothing special."
            ],
            "analyze_emotions": True,
            "extract_entities": False
        }
        
        response = client.post("/api/v1/nlp/batch-analyze", json=batch_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["total_processed"] == 3
        assert len(data["results"]) == 3
    
    def test_trending_topics(self, client, auth_headers):
        """Test getting trending topics."""
        response = client.get("/api/v1/nlp/trending?hours=24", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        assert "sentiment_distribution" in data
        assert "emotion_distribution" in data


class TestAIAdEndpoints:
    """Test AI advertisement generation endpoints."""
    
    def test_generate_ad(self, client, auth_headers):
        """Test AI ad generation."""
        ad_request = {
            "product_name": "Smart Fitness Tracker",
            "product_description": "Advanced fitness tracking with heart rate monitoring and GPS",
            "target_audience": {"age": "25-40", "interests": ["fitness", "technology"]},
            "campaign_objective": "conversion",
            "brand_voice": "energetic",
            "platform": "facebook",
            "ad_format": "single_image",
            "budget_range": "medium",
            "keywords": ["fitness", "smart", "tracking"],
            "emotions_to_target": ["motivation", "achievement"]
        }
        
        response = client.post("/api/v1/ai-ads/generate", json=ad_request, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "headline" in data
        assert "description" in data
        assert "call_to_action" in data
        assert "estimated_performance" in data
        assert "variations" in data
    
    def test_ab_test_generation(self, client, auth_headers):
        """Test A/B test ad generation."""
        ab_test_request = {
            "product_name": "Eco-Friendly Water Bottle",
            "product_description": "Sustainable, BPA-free water bottle made from recycled materials",
            "target_audience": {"age": "20-45", "interests": ["environment", "health"]},
            "campaign_objective": "awareness",
            "brand_voice": "caring",
            "platform": "instagram",
            "variation_count": 3,
            "keywords": ["eco", "sustainable", "health"],
            "emotions_to_target": ["care", "responsibility"]
        }
        
        response = client.post("/api/v1/ai-ads/ab-test", json=ab_test_request, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("headline" in ad for ad in data)
        assert all("estimated_performance" in ad for ad in data)
    
    def test_get_ad_templates(self, client, auth_headers):
        """Test getting ad templates."""
        response = client.get("/api/v1/ai-ads/templates?platform=facebook&industry=ecommerce", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert data["platform"] == "facebook"


class TestIntegrationScenarios:
    """Test complex integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_campaign_workflow(self, client, auth_headers, db_session):
        """Test a complete campaign creation and management workflow."""
        
        # 1. Create a campaign
        campaign_data = {
            "name": "Integration Test Campaign",
            "description": "Testing complete workflow",
            "target_audience": {"age": "25-35", "interests": ["technology"]},
            "budget": 2000.0,
            "start_date": "2024-01-15T00:00:00",
            "end_date": "2024-02-15T00:00:00"
        }
        
        campaign_response = client.post("/api/v1/campaigns/", json=campaign_data, headers=auth_headers)
        assert campaign_response.status_code == 201
        campaign = campaign_response.json()
        campaign_id = campaign["id"]
        
        # 2. Generate AI ads for the campaign
        ad_request = {
            "campaign_id": campaign_id,
            "product_name": "Smart Home Device",
            "product_description": "Revolutionary IoT device for home automation",
            "target_audience": campaign_data["target_audience"],
            "campaign_objective": "conversion",
            "platform": "facebook",
            "keywords": ["smart", "home", "automation"],
            "emotions_to_target": ["convenience", "innovation"]
        }
        
        ad_response = client.post("/api/v1/ai-ads/generate", json=ad_request, headers=auth_headers)
        assert ad_response.status_code == 200
        generated_ad = ad_response.json()
        
        # 3. Analyze campaign performance
        analytics_response = client.get(f"/api/v1/analytics/campaigns", headers=auth_headers)
        assert analytics_response.status_code == 200
        
        # 4. Get audience insights
        audience_response = client.get(f"/api/v1/analytics/audience?campaign_id={campaign_id}", headers=auth_headers)
        assert audience_response.status_code == 200
        
        # Verify the complete workflow worked
        assert campaign["name"] == campaign_data["name"]
        assert generated_ad["headline"] is not None
        assert len(generated_ad["variations"]) > 0


# Performance and Load Testing
class TestPerformance:
    """Test system performance under load."""
    
    def test_concurrent_ad_generation(self, client, auth_headers):
        """Test concurrent ad generation requests."""
        import concurrent.futures
        import time
        
        def generate_ad():
            ad_request = {
                "product_name": f"Test Product {time.time()}",
                "product_description": "Test description for load testing",
                "target_audience": {"age": "25-35"},
                "campaign_objective": "engagement",
                "platform": "facebook",
                "keywords": ["test"],
                "emotions_to_target": ["joy"]
            }
            return client.post("/api/v1/ai-ads/generate", json=ad_request, headers=auth_headers)
        
        # Test 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_ad) for _ in range(5)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(response.status_code == 200 for response in responses)
    
    def test_batch_processing_performance(self, client, auth_headers):
        """Test batch processing performance."""
        batch_request = {
            "texts": [f"Test text {i} for batch processing" for i in range(20)],
            "analyze_emotions": True,
            "extract_entities": True
        }
        
        start_time = time.time()
        response = client.post("/api/v1/nlp/batch-analyze", json=batch_request, headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 20
        assert end_time - start_time < 10  # Should complete within 10 seconds


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
