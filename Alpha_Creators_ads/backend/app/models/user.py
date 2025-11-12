"""
User-related Pydantic models
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"

class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro" 
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class NotificationSettings(BaseModel):
    email: bool = True
    push: bool = True
    sms: bool = False

class Subscription(BaseModel):
    plan: SubscriptionPlan = SubscriptionPlan.FREE
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    startDate: datetime
    endDate: Optional[datetime] = None
    features: List[str] = []

class UserPreferences(BaseModel):
    theme: Theme = Theme.LIGHT
    language: str = "en"
    notifications: NotificationSettings = NotificationSettings()
    defaultCurrency: str = "USD"

class ApiUsage(BaseModel):
    adsGenerated: int = 0
    apiCallsThisMonth: int = 0
    quotaLimit: int = 100

class UserBase(BaseModel):
    email: EmailStr
    username: str
    fullName: str
    avatar: Optional[str] = None
    role: UserRole = UserRole.USER
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower()

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')  
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    fullName: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Optional[UserPreferences] = None

class UserInDB(UserBase):
    id: str
    passwordHash: str
    subscription: Subscription
    preferences: UserPreferences = UserPreferences()
    apiUsage: ApiUsage = ApiUsage()
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime] = None
    isVerified: bool = False
    isActive: bool = True
    
    class Config:
        populate_by_name = True

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    fullName: str
    avatar: Optional[str]
    role: UserRole
    subscription: Subscription
    preferences: UserPreferences
    apiUsage: ApiUsage
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime]
    isVerified: bool
    isActive: bool
    
    class Config:
        populate_by_name = True

class UserProfile(BaseModel):
    id: str
    username: str
    fullName: str
    avatar: Optional[str]
    role: UserRole
    subscription: Subscription
    
class UserStats(BaseModel):
    totalCampaigns: int
    activeCampaigns: int
    totalAds: int
    totalSpend: float
    avgCTR: float
    avgROAS: float