"""
API v1 router for Alpha Creators Ads.
"""

from fastapi import APIRouter
from api.v1.endpoints import health, analytics, campaigns, nlp, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(nlp.router, prefix="/nlp", tags=["nlp"])
