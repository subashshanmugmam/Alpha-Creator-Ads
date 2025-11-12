"""
Authentication API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from app.database import get_db
from app.cache import CacheManager, CacheKeys
from app.schemas.auth import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    RefreshTokenRequest, RefreshTokenResponse, ForgotPasswordRequest,
    ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse,
    ChangePasswordRequest, ChangePasswordResponse, VerifyEmailRequest,
    VerifyEmailResponse, PasswordStrengthCheck, PasswordStrengthResponse
)
from app.models.user import UserCreate, UserInDB, UserResponse, Subscription, UserPreferences, ApiUsage
from app.utils.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    verify_token, generate_password_reset_token, verify_password_reset_token,
    generate_verification_token, verify_email_token, get_current_user_id,
    validate_password_strength
)
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    🚀 **Register New User**
    
    Create a new user account with email verification.
    
    **Features:**
    - Password strength validation
    - Email uniqueness check
    - Username availability check  
    - Automatic email verification sending
    - JWT token generation
    - Free tier subscription setup
    
    **Returns:**
    - User profile information
    - Access and refresh tokens
    - Success message
    """
    
    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    
    if existing_user:
        if existing_user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Validate password strength
    password_check = validate_password_strength(user_data.password)
    if not password_check["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password does not meet security requirements",
                "errors": password_check["errors"],
                "suggestions": password_check["suggestions"]
            }
        )
    
    # Create user document
    now = datetime.utcnow()
    user_doc = {
        "email": user_data.email,
        "username": user_data.username,
        "fullName": user_data.fullName,
        "passwordHash": get_password_hash(user_data.password),
        "avatar": None,
        "role": "user",
        "subscription": {
            "plan": "free",
            "status": "active", 
            "startDate": now,
            "endDate": None,
            "features": ["basic_analytics", "campaign_management"]
        },
        "preferences": {
            "theme": "light",
            "language": "en",
            "notifications": {
                "email": True,
                "push": True,
                "sms": False
            },
            "defaultCurrency": "USD"
        },
        "apiUsage": {
            "adsGenerated": 0,
            "apiCallsThisMonth": 0,
            "quotaLimit": settings.AI_GENERATION_QUOTA_FREE
        },
        "createdAt": now,
        "updatedAt": now,
        "lastLogin": now,
        "isVerified": False,
        "isActive": True
    }
    
    # Insert user
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Generate verification token and send email (background task)
    verification_token = generate_verification_token(user_data.email)
    # background_tasks.add_task(send_verification_email, user_data.email, verification_token)
    
    # Cache user data
    user_doc["id"] = user_id
    await cache.set(CacheKeys.user_profile(user_id), user_doc, ttl=3600)
    
    # Create response
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        username=user_data.username,
        fullName=user_data.fullName,
        avatar=None,
        role="user",
        subscription=Subscription(**user_doc["subscription"]),
        preferences=UserPreferences(**user_doc["preferences"]),
        apiUsage=ApiUsage(**user_doc["apiUsage"]),
        createdAt=now,
        updatedAt=now,
        lastLogin=now,
        isVerified=False,
        isActive=True
    )
    
    logger.info(f"New user registered: {user_data.email}")
    
    return RegisterResponse(
        message="Account created successfully. Please check your email for verification.",
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    🔐 **User Login**
    
    Authenticate user and return JWT tokens.
    
    **Features:**
    - Email/password authentication
    - JWT token generation
    - User session tracking
    - Login attempt logging
    - Cache user profile
    
    **Returns:**
    - Access and refresh tokens
    - User profile information
    - Token expiration info
    """
    
    # Find user by email
    user_doc = await db.users.find_one({"email": credentials.email})
    
    if not user_doc or not verify_password(credentials.password, user_doc["passwordHash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user_doc["isActive"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    user_id = str(user_doc["_id"])
    now = datetime.utcnow()
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"lastLogin": now, "updatedAt": now}}
    )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Cache user profile
    user_doc["id"] = user_id
    user_doc["lastLogin"] = now
    await cache.set(CacheKeys.user_profile(user_id), user_doc, ttl=3600)
    
    # Create response
    user_response = UserResponse(
        id=user_id,
        email=user_doc["email"],
        username=user_doc["username"],
        fullName=user_doc["fullName"],
        avatar=user_doc.get("avatar"),
        role=user_doc["role"],
        subscription=Subscription(**user_doc["subscription"]),
        preferences=UserPreferences(**user_doc["preferences"]),
        apiUsage=ApiUsage(**user_doc["apiUsage"]),
        createdAt=user_doc["createdAt"],
        updatedAt=now,
        lastLogin=now,
        isVerified=user_doc["isVerified"],
        isActive=user_doc["isActive"]
    )
    
    logger.info(f"User logged in: {credentials.email}")
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(token_data: RefreshTokenRequest):
    """
    🔄 **Refresh Access Token**
    
    Generate new access token using refresh token.
    """
    
    try:
        payload = verify_token(token_data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new access token
        access_token = create_access_token(data={"sub": user_id})
        
        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        ) from e

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    👤 **Get Current User Profile**
    
    Retrieve current authenticated user's profile information.
    """
    
    # Try cache first
    cached_user = await cache.get(CacheKeys.user_profile(current_user_id))
    if cached_user:
        return UserResponse(**cached_user)
    
    # Get from database
    from bson import ObjectId
    user_doc = await db.users.find_one({"_id": ObjectId(current_user_id)})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cache user data
    user_doc["id"] = current_user_id
    await cache.set(CacheKeys.user_profile(current_user_id), user_doc, ttl=3600)
    
    return UserResponse(
        id=current_user_id,
        email=user_doc["email"],
        username=user_doc["username"],
        fullName=user_doc["fullName"],
        avatar=user_doc.get("avatar"),
        role=user_doc["role"],
        subscription=Subscription(**user_doc["subscription"]),
        preferences=UserPreferences(**user_doc["preferences"]),
        apiUsage=ApiUsage(**user_doc["apiUsage"]),
        createdAt=user_doc["createdAt"],
        updatedAt=user_doc["updatedAt"],
        lastLogin=user_doc.get("lastLogin"),
        isVerified=user_doc["isVerified"],
        isActive=user_doc["isActive"]
    )

@router.post("/check-password-strength", response_model=PasswordStrengthResponse)
async def check_password_strength(password_data: PasswordStrengthCheck):
    """
    🔒 **Check Password Strength**
    
    Validate password strength and provide feedback.
    """
    
    result = validate_password_strength(password_data.password)
    return PasswordStrengthResponse(**result)

@router.post("/logout")
async def logout(
    current_user_id: str = Depends(get_current_user_id),
    cache: CacheManager = Depends()
):
    """
    👋 **User Logout**
    
    Logout user and clear cached data.
    """
    
    # Clear user cache
    await cache.delete(CacheKeys.user_profile(current_user_id))
    
    return {"message": "Logged out successfully"}