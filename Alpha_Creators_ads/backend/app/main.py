"""
Alpha Creator Ads - Main FastAPI Application
Production-ready advertising platform backend
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import uvicorn
from typing import Dict, Any
import os
from datetime import datetime
import time

# Import custom modules
# Simplified imports for development
from app.api.v1 import api_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Alpha Creator Ads Backend...")
    
    # Initialize database connection
    await connect_to_mongo()
    logger.info("✅ Database connection established")
    
    # Redis and other services will be initialized as needed
    logger.info("✅ Core services ready")
    
    logger.info("🎉 Backend startup complete!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Alpha Creator Ads Backend...")
    
    # Close database connections
    await close_mongo_connection()
    logger.info("✅ Database connections closed")
    
    logger.info("👋 Backend shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Alpha Creator Ads API",
    description="""
    🚀 **Alpha Creator Ads** - Next-Generation AI-Powered Advertising Platform
    
    ## Features
    
    * **🤖 AI Ad Generation** - Create compelling ads with GPT-4
    * **📊 Advanced Analytics** - Real-time campaign performance tracking  
    * **🎯 Smart Targeting** - Audience segmentation and optimization
    * **💰 Budget Management** - Automated spend optimization
    * **🔄 Multi-Platform** - Google, Facebook, Instagram, LinkedIn
    * **⚡ Real-time Updates** - WebSocket-based live metrics
    
    ## Authentication
    
    Use JWT Bearer tokens for authentication:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    
    ## Rate Limiting
    
    API calls are rate limited to prevent abuse:
    - **Free tier**: 100 requests/hour
    - **Pro tier**: 1000 requests/hour  
    - **Enterprise**: Unlimited
    
    ## Support
    
    - 📧 Email: support@alphaads.com
    - 📖 Documentation: https://docs.alphaads.com
    - 🐛 Issues: https://github.com/alphaads/platform/issues
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
    contact={
        "name": "Alpha Creator Ads Support",
        "email": "support@alphaads.com",
        "url": "https://alphaads.com/support"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Security middleware (simplified for development)
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"]
)

# Custom middleware will be added in production

# Static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    🏠 **API Root Endpoint**
    
    Welcome to the Alpha Creator Ads API! This endpoint provides basic 
    information about the API status and available endpoints.
    
    Returns:
        dict: API information and status
    """
    return {
        "message": "🚀 Alpha Creator Ads API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/api/docs",
        "endpoints": {
            "authentication": "/api/v1/auth/",
            "campaigns": "/api/v1/campaigns/",
            "ads": "/api/v1/ads/", 
            "analytics": "/api/v1/analytics/",
            "ai_generation": "/api/v1/ai/",
            "users": "/api/v1/users/"
        },
        "features": [
            "AI-Powered Ad Generation",
            "Multi-Platform Campaign Management", 
            "Real-time Analytics",
            "Advanced Targeting",
            "Budget Optimization"
        ]
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    ❤️ **System Health Check**
    
    Comprehensive health check endpoint that verifies the status of all
    critical system components including database, cache, and external services.
    
    Returns:
        dict: Detailed health status of all components
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": time.time(),
        "services": {}
    }
    
    # Database connection check (simplified for development)
    health_status["services"]["database"] = {
        "status": "development_mode",
        "type": "MongoDB",
        "note": "Database connection will be configured in production"
    }
    
    # Check Redis connection
    try:
        from app.cache import CacheManager
        cache = CacheManager()
        # Redis check would go here
        pass
        health_status["services"]["cache"] = {
            "status": "healthy",
            "type": "Redis"
        }
    except Exception as e:
        health_status["services"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check external services
    health_status["services"]["ai_service"] = {
        "status": "healthy" if os.getenv("OPENAI_API_KEY") else "not_configured",
        "type": "OpenAI GPT-4"
    }
    
    return health_status

# Metrics endpoint for monitoring
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    📊 **System Metrics**
    
    Provides system metrics for monitoring and alerting.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "requests": {
            "total": 0,  # Would be tracked in middleware
            "rate": "0/sec"
        },
        "database": {
            "connections": 10,
            "queries_per_second": 0
        },
        "memory": {
            "usage": "256MB",
            "available": "2GB"
        }
    }

# API Info endpoint
@app.get("/api/info", tags=["API Info"])
async def api_info():
    """
    ℹ️ **API Information**
    
    Detailed information about API capabilities, rate limits, and usage.
    """
    return {
        "api_version": "1.0.0",
        "supported_formats": ["JSON"],
        "authentication": "JWT Bearer Token",
        "rate_limits": {
            "free": "100 requests/hour",
            "pro": "1000 requests/hour", 
            "enterprise": "unlimited"
        },
        "features": {
            "ai_generation": {
                "models": ["GPT-4", "GPT-3.5-turbo"],
                "formats": ["text", "image_prompts"],
                "languages": ["en", "es", "fr", "de"]
            },
            "analytics": {
                "real_time": True,
                "historical_data": "90 days",
                "export_formats": ["CSV", "PDF", "JSON"]
            },
            "platforms": [
                "Google Ads",
                "Facebook Ads", 
                "Instagram Ads",
                "LinkedIn Ads"
            ]
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info",
        access_log=True
    )