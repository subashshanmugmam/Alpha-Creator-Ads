"""
Ad-related Pydantic models
"""

from pydantic import BaseModel, validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AdType(str, Enum):
    TEXT = "text"
    DISPLAY = "display"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"

class AdStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class EmotionalTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    EXCITING = "exciting"
    URGENT = "urgent"
    PLAYFUL = "playful"
    TRUSTWORTHY = "trustworthy"
    LUXURIOUS = "luxurious"

class AdContent(BaseModel):
    headline: str
    description: str
    cta: str
    body: Optional[str] = None
    images: List[str] = []  # URLs
    videos: List[str] = []  # URLs
    
    @validator('headline')
    def validate_headline(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Headline must be at least 5 characters long')
        if len(v) > 100:
            raise ValueError('Headline cannot exceed 100 characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        if len(v) > 500:
            raise ValueError('Description cannot exceed 500 characters')
        return v.strip()
    
    @validator('cta')
    def validate_cta(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('CTA must be at least 2 characters long')
        if len(v) > 30:
            raise ValueError('CTA cannot exceed 30 characters')
        return v.strip()

class GenerationParams(BaseModel):
    model: str = "gpt-4"
    prompt: str
    emotionalTone: EmotionalTone = EmotionalTone.PROFESSIONAL
    targetAudience: str
    productCategory: str
    keywords: List[str] = []
    brandVoice: Optional[str] = None

class AdPerformance(BaseModel):
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    engagement: int = 0
    spend: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    conversionRate: float = 0.0

class ABTesting(BaseModel):
    isTestAd: bool = False
    testGroup: Optional[str] = None
    winnerDeclared: bool = False
    confidenceLevel: Optional[float] = None

class AdBase(BaseModel):
    campaignId: str
    type: AdType
    content: AdContent
    platform: str
    
    @validator('campaignId')
    def validate_campaign_id(cls, v):
        if not v.strip():
            raise ValueError('Campaign ID is required')
        return v

class AdCreate(AdBase):
    aiGenerated: bool = False
    generationParams: Optional[GenerationParams] = None

class AdUpdate(BaseModel):
    content: Optional[AdContent] = None
    status: Optional[AdStatus] = None
    platform: Optional[str] = None

class AdInDB(AdBase):
    id: str
    userId: str
    aiGenerated: bool = False
    generationParams: Optional[GenerationParams] = None
    status: AdStatus = AdStatus.DRAFT
    performance: AdPerformance = AdPerformance()
    abTesting: ABTesting = ABTesting()
    createdAt: datetime
    updatedAt: datetime
    publishedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

class AdResponse(AdBase):
    id: str
    userId: str
    aiGenerated: bool
    generationParams: Optional[GenerationParams]
    status: AdStatus
    performance: AdPerformance
    abTesting: ABTesting
    createdAt: datetime
    updatedAt: datetime
    publishedAt: Optional[datetime]
    
    class Config:
        populate_by_name = True

class AdSummary(BaseModel):
    id: str
    campaignId: str
    type: AdType
    headline: str
    status: AdStatus
    platform: str
    performance: AdPerformance
    createdAt: datetime

class AdGenerationRequest(BaseModel):
    campaignId: str
    type: AdType = AdType.TEXT
    platform: str
    generationParams: GenerationParams
    generateVariants: bool = False
    variantCount: int = 1
    
    @validator('variantCount')
    def validate_variant_count(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Variant count must be between 1 and 5')
        return v

class AdGenerationResponse(BaseModel):
    ads: List[AdContent]
    model: str
    tokensUsed: int
    generationTime: float
    cost: Optional[float] = None