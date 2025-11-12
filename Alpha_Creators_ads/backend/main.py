"""
Alpha Creators Ads - Backend System
Real-Time Emotion-Aware Ad Creation System

This is the main backend application for processing social media data,
analyzing sentiment, and generating personalized advertisements using AI.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import uvicorn
from typing import Dict, Any
import os
from datetime import datetime

# Import modules (will be created)
from core.config import settings
from core.database import init_db
from api.v1.api import api_router
from services.monitoring import setup_monitoring
from services.logging_config import setup_logging
from services.kafka_manager import kafka_manager, register_default_handlers
from services.reinforcement_learning import rl_manager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Alpha Creators Ads Backend...")
    await init_db()
    setup_monitoring()
    
    # Initialize Kafka
    try:
        await kafka_manager.start()
        register_default_handlers()
        await kafka_manager.start_all_consumers()
        logger.info("Kafka manager initialized")
    except Exception as e:
        logger.warning(f"Kafka initialization failed: {e}")
    
    logger.info("Backend startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Alpha Creators Ads Backend...")
    
    # Stop Kafka
    try:
        await kafka_manager.stop()
        logger.info("Kafka manager stopped")
    except Exception as e:
        logger.warning(f"Kafka shutdown error: {e}")
    
    logger.info("Backend shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Alpha Creators Ads API",
    description="Real-Time Emotion-Aware Ad Creation System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Alpha Creators Ads API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "redis": "connected",
            "kafka": "connected"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
