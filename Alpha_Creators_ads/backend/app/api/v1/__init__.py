"""
API v1 router initialization
"""

from fastapi import APIRouter
from app.api.v1 import auth, users, campaigns, ads, ai, analytics

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["User Management"]
)

api_router.include_router(
    campaigns.router,
    prefix="/campaigns",
    tags=["Campaign Management"]
)

api_router.include_router(
    ads.router,
    prefix="/ads",
    tags=["Ad Management"]
)

api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI Generation"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics & Reporting"]
)