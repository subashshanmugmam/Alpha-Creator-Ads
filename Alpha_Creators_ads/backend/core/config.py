"""
Core configuration settings for the Alpha Creators Ads backend.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Alpha Creators Ads"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database URLs
    DATABASE_URL: str = "postgresql://user:password@localhost/alphaads"
    REDIS_URL: str = "redis://localhost:6379/0"
    MONGODB_URL: str = "mongodb://localhost:27017/alphaads"
    NEO4J_URL: str = "bolt://localhost:7687"
    INFLUX_URL: str = "http://localhost:8086"
    
    # Database credentials
    POSTGRES_USER: str = "alphaads"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "alphaads"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # MongoDB
    MONGO_DB_NAME: str = "alphaads"
    
    # Neo4j
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # InfluxDB
    INFLUX_TOKEN: str = "your-influx-token"
    INFLUX_ORG: str = "alphaads"
    INFLUX_BUCKET: str = "metrics"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "alphaads-consumers"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Social Media APIs
    TWITTER_BEARER_TOKEN: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    
    # AI/ML APIs
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    HUGGINGFACE_API_TOKEN: Optional[str] = None
    
    # Advertising Platform APIs
    GOOGLE_ADS_DEVELOPER_TOKEN: Optional[str] = None
    GOOGLE_ADS_CLIENT_ID: Optional[str] = None
    GOOGLE_ADS_CLIENT_SECRET: Optional[str] = None
    
    FACEBOOK_ADS_ACCESS_TOKEN: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_AD_ACCOUNT_ID: Optional[str] = None
    FACEBOOK_PAGE_ID: Optional[str] = None
    
    LINKEDIN_ADS_ACCESS_TOKEN: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    
    # Landing page for ads
    LANDING_PAGE_URL: str = "https://alphaads.com"
    
    # NLP Models
    SENTIMENT_MODEL_PATH: str = "models/sentiment"
    EMOTION_MODEL_PATH: str = "models/emotion"
    BERT_MODEL_NAME: str = "bert-base-uncased"
    
    # Processing Limits
    MAX_POSTS_PER_HOUR: int = 100000
    MAX_CONCURRENT_PROCESSING: int = 100
    SENTIMENT_PROCESSING_TIMEOUT: int = 30
    AD_GENERATION_TIMEOUT: int = 300
    
    # Performance Targets
    TARGET_UPTIME: float = 99.9
    MAX_RESPONSE_TIME: float = 5.0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Paths
    MODELS_DIR: str = "models"
    LOGS_DIR: str = "logs"
    DATA_DIR: str = "data"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
