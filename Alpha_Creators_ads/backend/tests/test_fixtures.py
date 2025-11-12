"""
Test fixtures and utilities for the test suite.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
import tempfile
import os
from unittest.mock import Mock, AsyncMock

# Mock external services for testing
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"headline": "Test Headline", "description": "Test Description", "call_to_action": "Test CTA"}'
    
    async def mock_create(*args, **kwargs):
        return mock_response
    
    mock_client.chat.completions.create = mock_create
    return mock_client

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = '{"headline": "Test Headline", "description": "Test Description", "call_to_action": "Test CTA"}'
    
    async def mock_create(*args, **kwargs):
        return mock_response
    
    mock_client.messages.create = mock_create
    return mock_client

@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer for testing."""
    mock_producer = AsyncMock()
    mock_producer.send = AsyncMock(return_value=None)
    mock_producer.flush = AsyncMock()
    return mock_producer

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    return mock_redis

@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def sample_social_media_data():
    """Sample social media data for testing."""
    return [
        {
            "id": "tweet_123",
            "platform": "twitter",
            "content": "I absolutely love this new product! It's amazing! 😍",
            "author": "user123",
            "timestamp": "2024-01-15T10:00:00Z",
            "metrics": {"likes": 150, "shares": 25, "comments": 30}
        },
        {
            "id": "fb_456",
            "platform": "facebook",
            "content": "This product is terrible. Worst purchase ever.",
            "author": "user456",
            "timestamp": "2024-01-15T11:00:00Z",
            "metrics": {"likes": 5, "shares": 2, "comments": 10}
        },
        {
            "id": "ig_789",
            "platform": "instagram",
            "content": "Pretty good product overall. Does what it says.",
            "author": "user789",
            "timestamp": "2024-01-15T12:00:00Z",
            "metrics": {"likes": 75, "shares": 15, "comments": 8}
        }
    ]

@pytest.fixture
def sample_nlp_results():
    """Sample NLP analysis results for testing."""
    return {
        "sentiment": {
            "sentiment": "positive",
            "confidence": 0.89,
            "polarity": 0.75,
            "subjectivity": 0.65
        },
        "emotions": {
            "joy": 0.8,
            "excitement": 0.7,
            "satisfaction": 0.6,
            "surprise": 0.3
        },
        "entities": [
            {"text": "Apple", "label": "ORG", "start": 0, "end": 5},
            {"text": "iPhone", "label": "PRODUCT", "start": 6, "end": 12}
        ]
    }

@pytest.fixture
def sample_ad_performance_data():
    """Sample ad performance data for testing."""
    return {
        "impressions": 10000,
        "clicks": 250,
        "conversions": 15,
        "spend": 500.0,
        "ctr": 0.025,
        "conversion_rate": 0.06,
        "cost_per_click": 2.0,
        "cost_per_conversion": 33.33
    }
