"""
Redis cache management for Alpha Creator Ads
"""

import aioredis
from typing import Optional, Any, Union
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class Cache:
    redis: Optional[aioredis.Redis] = None

# Global cache instance
cache = Cache()

async def init_redis():
    """Initialize Redis connection"""
    try:
        cache.redis = await aioredis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Test connection
        await cache.redis.ping()
        logger.info("✅ Connected to Redis cache")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
        raise

async def close_redis():
    """Close Redis connection"""
    if cache.redis:
        await cache.redis.close()
        logger.info("✅ Redis connection closed")

async def get_redis() -> aioredis.Redis:
    """Get Redis instance"""
    if not cache.redis:
        await init_redis()
    return cache.redis

class CacheManager:
    """Cache management utilities"""
    
    @staticmethod
    async def set(key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in cache with optional TTL"""
        try:
            redis = await get_redis()
            
            # Serialize complex objects to JSON
            if not isinstance(value, (str, int, float, bool)):
                value = json.dumps(value, default=str)
            
            if ttl:
                return await redis.setex(key, ttl, value)
            else:
                return await redis.set(key, value)
                
        except Exception as e:
            logger.error(f"Cache SET error for key {key}: {e}")
            return False
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            redis = await get_redis()
            value = await redis.get(key)
            
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Cache GET error for key {key}: {e}")
            return None
    
    @staticmethod
    async def delete(key: str) -> bool:
        """Delete a key from cache"""
        try:
            redis = await get_redis()
            return bool(await redis.delete(key))
        except Exception as e:
            logger.error(f"Cache DELETE error for key {key}: {e}")
            return False
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if a key exists in cache"""
        try:
            redis = await get_redis()
            return bool(await redis.exists(key))
        except Exception as e:
            logger.error(f"Cache EXISTS error for key {key}: {e}")
            return False
    
    @staticmethod
    async def increment(key: str, amount: int = 1) -> int:
        """Increment a numeric value in cache"""
        try:
            redis = await get_redis()
            return await redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache INCREMENT error for key {key}: {e}")
            return 0
    
    @staticmethod
    async def set_hash(name: str, mapping: dict, ttl: int = None) -> bool:
        """Set a hash in cache"""
        try:
            redis = await get_redis()
            
            # Serialize complex values in the mapping
            serialized_mapping = {}
            for k, v in mapping.items():
                if not isinstance(v, (str, int, float, bool)):
                    serialized_mapping[k] = json.dumps(v, default=str)
                else:
                    serialized_mapping[k] = v
            
            result = await redis.hset(name, mapping=serialized_mapping)
            
            if ttl:
                await redis.expire(name, ttl)
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache HSET error for hash {name}: {e}")
            return False
    
    @staticmethod
    async def get_hash(name: str) -> dict:
        """Get a hash from cache"""
        try:
            redis = await get_redis()
            hash_data = await redis.hgetall(name)
            
            # Try to deserialize JSON values
            result = {}
            for k, v in hash_data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            
            return result
            
        except Exception as e:
            logger.error(f"Cache HGETALL error for hash {name}: {e}")
            return {}
    
    @staticmethod
    async def add_to_set(key: str, *values: str) -> int:
        """Add values to a set in cache"""
        try:
            redis = await get_redis()
            return await redis.sadd(key, *values)
        except Exception as e:
            logger.error(f"Cache SADD error for set {key}: {e}")
            return 0
    
    @staticmethod
    async def get_set_members(key: str) -> set:
        """Get all members of a set from cache"""
        try:
            redis = await get_redis()
            return await redis.smembers(key)
        except Exception as e:
            logger.error(f"Cache SMEMBERS error for set {key}: {e}")
            return set()
    
    @staticmethod
    async def push_to_list(key: str, *values: str) -> int:
        """Push values to a list in cache"""
        try:
            redis = await get_redis()
            return await redis.lpush(key, *values)
        except Exception as e:
            logger.error(f"Cache LPUSH error for list {key}: {e}")
            return 0
    
    @staticmethod
    async def get_list_range(key: str, start: int = 0, end: int = -1) -> list:
        """Get range of values from a list in cache"""
        try:
            redis = await get_redis()
            return await redis.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Cache LRANGE error for list {key}: {e}")
            return []

# Cache key generators
class CacheKeys:
    """Standardized cache key generators"""
    
    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"user:profile:{user_id}"
    
    @staticmethod
    def user_campaigns(user_id: str) -> str:
        return f"user:campaigns:{user_id}"
    
    @staticmethod
    def campaign_analytics(campaign_id: str) -> str:
        return f"campaign:analytics:{campaign_id}"
    
    @staticmethod
    def ad_performance(ad_id: str) -> str:
        return f"ad:performance:{ad_id}"
    
    @staticmethod
    def ai_generation_quota(user_id: str) -> str:
        return f"ai:quota:{user_id}"
    
    @staticmethod
    def rate_limit(user_id: str, endpoint: str) -> str:
        return f"rate_limit:{endpoint}:{user_id}"
    
    @staticmethod
    def session(session_id: str) -> str:
        return f"session:{session_id}"
    
    @staticmethod
    def dashboard_metrics(user_id: str) -> str:
        return f"dashboard:metrics:{user_id}"

# Dependency for FastAPI
async def get_cache() -> CacheManager:
    """Dependency to get cache manager in FastAPI endpoints"""
    return CacheManager()