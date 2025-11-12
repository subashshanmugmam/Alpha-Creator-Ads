"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any

from services.monitoring import health_checker, metrics_collector

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Alpha Creators Ads API"
    }


@router.get("/detailed")
async def detailed_health():
    """Detailed health check with all system components"""
    health = await health_checker.get_system_health()
    
    return {
        "status": health.status,
        "timestamp": health.timestamp.isoformat(),
        "services": health.services,
        "metrics": health.metrics
    }


@router.get("/metrics")
async def get_metrics():
    """Get current system metrics"""
    metrics = await health_checker.get_system_metrics()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics
    }


@router.get("/metrics/history")
async def get_metrics_history(hours: int = 24):
    """Get metrics history for the last N hours"""
    history = metrics_collector.get_metrics_history(hours)
    return {
        "period_hours": hours,
        "data_points": len(history),
        "history": history
    }
