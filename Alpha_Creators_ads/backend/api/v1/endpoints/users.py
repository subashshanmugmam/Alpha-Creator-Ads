"""
User management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import uuid

from core.database import get_db_session
from models import User, CustomerProfile
from services.authentication import get_current_user, create_access_token, verify_password, get_password_hash

router = APIRouter()
security = HTTPBearer()


# Pydantic models for request/response
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    is_advertiser: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    is_active: bool
    is_advertiser: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class ProfileCreate(BaseModel):
    social_media_id: str
    platform: str
    age_range: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    language: str = "en"

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    social_media_id: str
    platform: str
    age_range: Optional[str]
    gender: Optional[str]
    location: Optional[str]
    language: str
    emotional_state: Optional[str]
    sentiment_score: float
    purchase_intent: float
    created_at: datetime


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.execute(
        "SELECT id FROM users WHERE email = :email OR username = :username",
        {"email": user_data.email, "username": user_data.username}
    )
    if existing_user.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_advertiser=user_data.is_advertiser
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_advertiser=user.is_advertiser,
        created_at=user.created_at
    )


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db_session)
):
    """Login user and return access token"""
    # Get user by email
    result = await db.execute(
        "SELECT * FROM users WHERE email = :email",
        {"email": login_data.email}
    )
    user = result.first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_advertiser=current_user.is_advertiser,
        created_at=current_user.created_at
    )


@router.get("/profiles", response_model=List[ProfileResponse])
async def get_user_profiles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all profiles for current user"""
    result = await db.execute(
        "SELECT * FROM customer_profiles WHERE user_id = :user_id",
        {"user_id": current_user.id}
    )
    profiles = result.all()
    
    return [
        ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            social_media_id=profile.social_media_id,
            platform=profile.platform,
            age_range=profile.age_range,
            gender=profile.gender,
            location=profile.location,
            language=profile.language,
            emotional_state=profile.emotional_state,
            sentiment_score=profile.sentiment_score or 0.0,
            purchase_intent=profile.purchase_intent or 0.0,
            created_at=profile.created_at
        )
        for profile in profiles
    ]


@router.post("/profiles", response_model=ProfileResponse)
async def create_user_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new customer profile"""
    profile = CustomerProfile(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        social_media_id=profile_data.social_media_id,
        platform=profile_data.platform,
        age_range=profile_data.age_range,
        gender=profile_data.gender,
        location=profile_data.location,
        language=profile_data.language,
        sentiment_score=0.0,
        purchase_intent=0.0
    )
    
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        social_media_id=profile.social_media_id,
        platform=profile.platform,
        age_range=profile.age_range,
        gender=profile.gender,
        location=profile.location,
        language=profile.language,
        emotional_state=profile.emotional_state,
        sentiment_score=profile.sentiment_score,
        purchase_intent=profile.purchase_intent,
        created_at=profile.created_at
    )
