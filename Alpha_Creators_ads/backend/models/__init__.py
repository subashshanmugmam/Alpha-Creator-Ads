"""
Database models for the Alpha Creators Ads system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model for customers and advertisers"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_advertiser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="owner")
    profiles = relationship("CustomerProfile", back_populates="user")


class CustomerProfile(Base):
    """Dynamic customer profile with emotional and behavioral data"""
    __tablename__ = "customer_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    social_media_id = Column(String, index=True)
    platform = Column(String, nullable=False)  # twitter, facebook, instagram, linkedin
    
    # Demographic info
    age_range = Column(String)
    gender = Column(String)
    location = Column(String)
    language = Column(String, default="en")
    
    # Interests and preferences
    interests = Column(JSON)  # List of interests
    topics = Column(JSON)  # Topics they engage with
    brands = Column(JSON)  # Brands they follow/mention
    
    # Emotional profile
    emotional_state = Column(String)  # Current dominant emotion
    emotional_history = Column(JSON)  # Historical emotional patterns
    sentiment_score = Column(Float, default=0.0)
    
    # Behavioral profile
    engagement_patterns = Column(JSON)  # When they're most active
    content_preferences = Column(JSON)  # Types of content they engage with
    purchase_intent = Column(Float, default=0.0)  # 0-1 scale
    customer_lifetime_value = Column(Float, default=0.0)
    
    # Privacy settings
    data_consent = Column(Boolean, default=False)
    tracking_consent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profiles")
    social_posts = relationship("SocialMediaPost", back_populates="profile")


class SocialMediaPost(Base):
    """Social media posts collected for analysis"""
    __tablename__ = "social_media_posts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String, ForeignKey("customer_profiles.id"), nullable=False)
    post_id = Column(String, nullable=False, index=True)  # Platform-specific post ID
    platform = Column(String, nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    media_urls = Column(JSON)  # URLs to images, videos, etc.
    hashtags = Column(JSON)  # List of hashtags
    mentions = Column(JSON)  # List of user mentions
    
    # Metadata
    posted_at = Column(DateTime, nullable=False)
    author_username = Column(String)
    engagement_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Analysis results
    sentiment_score = Column(Float)
    emotions = Column(JSON)  # Dict of emotion: confidence
    topics = Column(JSON)  # Extracted topics
    entities = Column(JSON)  # Named entities
    intent = Column(String)  # Purchase intent, complaint, etc.
    confidence_score = Column(Float)
    
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = relationship("CustomerProfile", back_populates="social_posts")


class Campaign(Base):
    """Advertising campaigns"""
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Campaign settings
    target_audience = Column(JSON)  # Audience criteria
    budget = Column(Float, nullable=False)
    daily_budget = Column(Float)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    # Status
    status = Column(String, default="draft")  # draft, active, paused, completed
    is_active = Column(Boolean, default=False)
    rl_optimization = Column(Boolean, default=False)  # Whether RL optimization is enabled
    
    # Performance
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)  # Click-through rate
    conversion_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="campaigns")
    ad_creatives = relationship("AdCreative", back_populates="campaign")
    platform_deliveries = relationship("PlatformDelivery", back_populates="campaign")


class AdCreative(Base):
    """Generated ad creatives"""
    __tablename__ = "ad_creatives"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    
    # Content
    headline = Column(String, nullable=False)
    description = Column(Text)
    cta_text = Column(String)  # Call-to-action
    image_url = Column(String)
    video_url = Column(String)
    
    # Targeting
    target_emotions = Column(JSON)  # Emotions this ad targets
    target_audience = Column(JSON)  # Specific audience criteria
    personalization_data = Column(JSON)  # Data used for personalization
    
    # Generation metadata
    ai_model_used = Column(String)
    generation_prompt = Column(Text)
    confidence_score = Column(Float)
    
    # Performance
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # A/B Testing
    variant_id = Column(String)  # For A/B test grouping
    is_control = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="ad_creatives")


class AdDelivery(Base):
    """Ad delivery tracking"""
    __tablename__ = "ad_deliveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ad_creative_id = Column(String, ForeignKey("ad_creatives.id"), nullable=False)
    profile_id = Column(String, ForeignKey("customer_profiles.id"), nullable=False)
    
    # Platform details
    platform = Column(String, nullable=False)  # google_ads, facebook_ads, etc.
    placement = Column(String)  # news_feed, stories, search, etc.
    platform_ad_id = Column(String)  # Platform-specific ad ID
    
    # Delivery details
    delivered_at = Column(DateTime, nullable=False)
    emotional_context = Column(JSON)  # User's emotional state when delivered
    user_context = Column(JSON)  # Additional context (time, location, etc.)
    
    # Engagement
    viewed = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    converted = Column(Boolean, default=False)
    engagement_time = Column(Float)  # Time spent viewing
    
    # Feedback
    user_feedback = Column(String)  # positive, negative, neutral
    feedback_reason = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ReinforcementLearningModel(Base):
    """RL model states and performance tracking"""
    __tablename__ = "reinforcement_learning_models"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    
    # Model configuration
    algorithm = Column(String, nullable=False)  # DQN, A3C, etc.
    hyperparameters = Column(JSON)
    state_representation = Column(JSON)  # State configuration
    
    # Performance metrics
    performance_metrics = Column(JSON)
    avg_reward = Column(Float, default=0.0)
    convergence_score = Column(Float, default=0.0)
    episodes_trained = Column(Integer, default=0)
    
    # Deployment
    status = Column(String, default="training")  # training, active, inactive
    is_global = Column(Boolean, default=False)
    deployed_at = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReinforcementLearningFeedback(Base):
    """RL feedback and training data"""
    __tablename__ = "reinforcement_learning_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Performance data
    performance_metrics = Column(JSON, nullable=False)
    reward = Column(Float, nullable=False)
    time_period = Column(String, default="1h")
    
    # Training context
    state_vector = Column(JSON)
    action_taken = Column(Integer)
    confidence_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class PlatformDelivery(Base):
    """Multi-platform ad delivery records"""
    __tablename__ = "platform_deliveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    ad_creative_id = Column(String, ForeignKey("ad_creatives.id"), nullable=False)
    
    # Platform details
    platform = Column(String, nullable=False)  # google, facebook, linkedin, etc.
    platform_ad_id = Column(String, nullable=False)  # Platform-specific ad ID
    
    # Delivery status and metrics
    status = Column(String, default="ACTIVE")  # ACTIVE, PAUSED, COMPLETED, ERROR
    impressions_projected = Column(Integer, default=0)
    reach_projected = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)
    
    # Actual performance (updated from platform APIs)
    impressions_actual = Column(Integer, default=0)
    clicks_actual = Column(Integer, default=0)
    conversions_actual = Column(Integer, default=0)
    cost_actual = Column(Float, default=0.0)
    
    # Timing
    delivery_start = Column(DateTime, nullable=False)
    delivery_end = Column(DateTime)
    
    # Platform-specific data
    platform_config = Column(JSON)  # Platform-specific settings
    targeting_options = Column(JSON)  # Platform targeting details
    
    # Relationships
    campaign = relationship("Campaign", back_populates="platform_deliveries")
    ad_creative = relationship("AdCreative")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlatformPerformance(Base):
    """Platform performance tracking"""
    __tablename__ = "platform_performance"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    delivery_id = Column(String, ForeignKey("platform_deliveries.id"), nullable=False)
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    
    # Calculated metrics
    ctr = Column(Float, default=0.0)  # Click-through rate
    conversion_rate = Column(Float, default=0.0)
    cpm = Column(Float, default=0.0)  # Cost per mille
    cpc = Column(Float, default=0.0)  # Cost per click
    cpa = Column(Float, default=0.0)  # Cost per acquisition
    
    # Time period for these metrics
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Additional platform-specific metrics
    platform_metrics = Column(JSON)
    
    # Relationships
    delivery = relationship("PlatformDelivery")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemMetrics(Base):
    """System performance and health metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String)
    
    # Context
    component = Column(String)  # Which system component
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Additional metadata
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
