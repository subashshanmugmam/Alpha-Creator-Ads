"""
Database configuration and connection management.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from neo4j import AsyncGraphDatabase
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
import logging
from typing import AsyncGenerator

from core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()
metadata = MetaData()

# Redis connection
redis_client = None

# MongoDB connection
mongo_client = None
mongo_db = None

# Neo4j connection
neo4j_driver = None

# InfluxDB connection
influx_client = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return redis_client


async def get_mongo():
    """Get MongoDB connection"""
    global mongo_client, mongo_db
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongo_db = mongo_client[settings.MONGO_DB_NAME]
    return mongo_db


async def get_neo4j():
    """Get Neo4j connection"""
    global neo4j_driver
    if neo4j_driver is None:
        neo4j_driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URL,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
    return neo4j_driver


async def get_influx():
    """Get InfluxDB connection"""
    global influx_client
    if influx_client is None:
        influx_client = InfluxDBClientAsync(
            url=settings.INFLUX_URL,
            token=settings.INFLUX_TOKEN,
            org=settings.INFLUX_ORG
        )
    return influx_client


async def init_db():
    """Initialize all database connections"""
    try:
        # Initialize PostgreSQL
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL connection initialized")
        
        # Test Redis connection
        redis_conn = await get_redis()
        await redis_conn.ping()
        logger.info("Redis connection initialized")
        
        # Test MongoDB connection
        mongo_db = await get_mongo()
        await mongo_db.command("ping")
        logger.info("MongoDB connection initialized")
        
        # Test Neo4j connection
        neo4j_conn = await get_neo4j()
        await neo4j_conn.verify_connectivity()
        logger.info("Neo4j connection initialized")
        
        # Test InfluxDB connection
        influx_conn = await get_influx()
        health = await influx_conn.health()
        if health.status == "pass":
            logger.info("InfluxDB connection initialized")
        else:
            logger.warning("InfluxDB health check failed")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_db():
    """Close all database connections"""
    global redis_client, mongo_client, neo4j_driver, influx_client
    
    try:
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
            
        if mongo_client:
            mongo_client.close()
            logger.info("MongoDB connection closed")
            
        if neo4j_driver:
            await neo4j_driver.close()
            logger.info("Neo4j connection closed")
            
        if influx_client:
            await influx_client.close()
            logger.info("InfluxDB connection closed")
            
        await engine.dispose()
        logger.info("PostgreSQL connection closed")
        
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# Dependency functions for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session"""
    async for session in get_db():
        yield session


async def get_redis_client() -> redis.Redis:
    """FastAPI dependency for Redis client"""
    return await get_redis()


async def get_mongo_client():
    """FastAPI dependency for MongoDB client"""
    return await get_mongo()


async def get_neo4j_client():
    """FastAPI dependency for Neo4j client"""
    return await get_neo4j()


async def get_influx_client():
    """FastAPI dependency for InfluxDB client"""
    return await get_influx()
