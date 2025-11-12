"""
Campaign-related Pydantic models
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CampaignObjective(str, Enum):
    AWARENESS = "awareness"
    ENGAGEMENT = "engagement" 
    CONVERSIONS = "conversions"
    TRAFFIC = "traffic"

class Platform(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"

class AgeRange(BaseModel):
    min: int = 18
    max: int = 65
    
    @validator('min')
    def validate_min_age(cls, v):
        if v < 13:
            raise ValueError('Minimum age must be at least 13')
        return v
    
    @validator('max')
    def validate_max_age(cls, v):
        if v > 100:
            raise ValueError('Maximum age cannot exceed 100')
        return v

class Demographics(BaseModel):
    ageRange: AgeRange = AgeRange()
    gender: List[str] = ["all"]
    locations: List[str] = []
    languages: List[str] = ["en"]

class Targeting(BaseModel):
    demographics: Demographics = Demographics()
    interests: List[str] = []
    behaviors: List[str] = []
    customAudiences: List[str] = []

class Budget(BaseModel):
    total: float
    spent: float = 0.0
    currency: str = "USD"
    dailyLimit: Optional[float] = None
    
    @validator('total')
    def validate_total_budget(cls, v):
        if v <= 0:
            raise ValueError('Total budget must be greater than 0')
        return v
    
    @validator('dailyLimit')
    def validate_daily_limit(cls, v, values):
        if v is not None and v <= 0:
            raise ValueError('Daily limit must be greater than 0')
        if v is not None and 'total' in values and v > values['total']:
            raise ValueError('Daily limit cannot exceed total budget')
        return v

class Schedule(BaseModel):
    startDate: datetime
    endDate: Optional[datetime] = None
    timezone: str = "UTC"
    dayParting: Optional[Dict[str, List[str]]] = None
    
    @validator('endDate')
    def validate_end_date(cls, v, values):
        if v and 'startDate' in values and v <= values['startDate']:
            raise ValueError('End date must be after start date')
        return v

class Performance(BaseModel):
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    ctr: float = 0.0
    cpc: float = 0.0
    roas: float = 0.0
    lastUpdated: Optional[datetime] = None

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    objective: CampaignObjective
    budget: Budget
    targeting: Targeting = Targeting()
    schedule: Schedule
    platforms: List[Platform] = []
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Campaign name must be at least 3 characters long')
        return v.strip()

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    budget: Optional[Budget] = None
    targeting: Optional[Targeting] = None
    schedule: Optional[Schedule] = None
    platforms: Optional[List[Platform]] = None

class CampaignInDB(CampaignBase):
    id: str
    userId: str
    status: CampaignStatus = CampaignStatus.DRAFT
    ads: List[str] = []  # List of ad IDs
    performance: Performance = Performance()
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True

class CampaignResponse(CampaignBase):
    id: str
    userId: str
    status: CampaignStatus
    ads: List[str]
    performance: Performance
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True

class CampaignSummary(BaseModel):
    id: str
    name: str
    status: CampaignStatus
    objective: CampaignObjective
    budget: Budget
    platforms: List[Platform]
    performance: Performance
    createdAt: datetime
    adsCount: int = 0

class CampaignStats(BaseModel):
    totalCampaigns: int
    activeCampaigns: int
    pausedCampaigns: int
    completedCampaigns: int
    totalSpent: float
    totalImpressions: int
    totalClicks: int
    totalConversions: int
    avgCTR: float
    avgROAS: float