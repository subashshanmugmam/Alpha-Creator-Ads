"""
Main API router that includes all endpoint modules.
"""

from fastapi import APIRouter

from api.v1.endpoints import health, users, campaigns, analytics, nlp, ai_ads, reinforcement_learning, multi_platform_delivery

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(nlp.router, prefix="/nlp", tags=["nlp"])
api_router.include_router(ai_ads.router, prefix="/ai-ads", tags=["ai-ads"])
api_router.include_router(reinforcement_learning.router, prefix="/rl", tags=["reinforcement-learning"])
api_router.include_router(multi_platform_delivery.router, tags=["multi-platform-delivery"])
