"""
Database connection management for MongoDB
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

# Global database instance
db = Database()

async def init_database():
    """Initialize database connection"""
    try:
        # Create MongoDB client
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            minPoolSize=settings.MONGODB_MIN_CONNECTIONS,
            maxPoolSize=settings.MONGODB_MAX_CONNECTIONS,
            serverSelectionTimeoutMS=5000
        )
        
        # Get database
        db.database = db.client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        
        # Initialize collections if they don't exist
        await init_collections()
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_database():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("✅ MongoDB connection closed")

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if not db.database:
        await init_database()
    return db.database

async def init_collections():
    """Initialize collections with proper indexes"""
    
    collections = [
        'users',
        'campaigns', 
        'ads',
        'analytics',
        'audience_segments',
        'ai_generations'
    ]
    
    # Create collections
    existing_collections = await db.database.list_collection_names()
    for collection_name in collections:
        if collection_name not in existing_collections:
            await db.database.create_collection(collection_name)
            logger.info(f"Created collection: {collection_name}")
    
    # Create indexes
    await create_indexes()

async def create_indexes():
    """Create database indexes for optimal performance"""
    
    # Users collection indexes
    await db.database.users.create_index("email", unique=True)
    await db.database.users.create_index("username", unique=True) 
    await db.database.users.create_index("createdAt")
    await db.database.users.create_index("subscription.plan")
    
    # Campaigns collection indexes
    await db.database.campaigns.create_index([("userId", 1), ("status", 1)])
    await db.database.campaigns.create_index([("createdAt", -1)])
    await db.database.campaigns.create_index("status")
    await db.database.campaigns.create_index("platforms")
    
    # Ads collection indexes
    await db.database.ads.create_index([("campaignId", 1), ("status", 1)])
    await db.database.ads.create_index([("userId", 1), ("aiGenerated", 1)])
    await db.database.ads.create_index([("createdAt", -1)])
    await db.database.ads.create_index("platform")
    await db.database.ads.create_index("type")
    
    # Analytics collection indexes (time-series optimization)
    await db.database.analytics.create_index([("campaignId", 1), ("timestamp", -1)])
    await db.database.analytics.create_index([("timestamp", -1)])
    await db.database.analytics.create_index([("userId", 1), ("timestamp", -1)])
    await db.database.analytics.create_index([("adId", 1), ("timestamp", -1)])
    
    # Audience segments indexes
    await db.database.audience_segments.create_index([("userId", 1), ("createdAt", -1)])
    await db.database.audience_segments.create_index("name")
    
    # AI generations indexes
    await db.database.ai_generations.create_index([("userId", 1), ("createdAt", -1)])
    await db.database.ai_generations.create_index("type")
    await db.database.ai_generations.create_index("model")
    
    logger.info("✅ Database indexes created successfully")

# Dependency for FastAPI
async def get_db() -> AsyncIOMotorDatabase:
    """Dependency to get database in FastAPI endpoints"""
    return await get_database()