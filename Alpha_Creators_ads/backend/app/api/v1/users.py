"""
User Management API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List, Optional
import logging
from bson import ObjectId

from app.database import get_db
from app.cache import CacheManager, CacheKeys
from app.models.user import UserResponse, UserUpdate, UserPreferences, Subscription, ApiUsage
from app.utils.security import get_current_user_id, verify_password, get_password_hash
from app.schemas.auth import ChangePasswordRequest, ChangePasswordResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    👤 **Get User Profile**
    
    Retrieve detailed user profile information.
    """
    
    # Try cache first
    cached_user = await cache.get(CacheKeys.user_profile(current_user_id))
    if cached_user:
        return UserResponse(**cached_user)
    
    # Get from database
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

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ✏️ **Update User Profile**
    
    Update user profile information.
    
    **Updatable Fields:**
    - Full name
    - Username (if available)
    - Avatar
    - Preferences
    """
    
    # Prepare update data
    update_data = {"updatedAt": datetime.utcnow()}
    
    if user_update.fullName is not None:
        update_data["fullName"] = user_update.fullName
    
    if user_update.username is not None:
        # Check username availability
        existing_user = await db.users.find_one({
            "username": user_update.username,
            "_id": {"$ne": ObjectId(current_user_id)}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_data["username"] = user_update.username
    
    if user_update.avatar is not None:
        update_data["avatar"] = user_update.avatar
    
    if user_update.preferences is not None:
        update_data["preferences"] = user_update.preferences.dict()
    
    # Update user
    await db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$set": update_data}
    )
    
    # Get updated user
    user_doc = await db.users.find_one({"_id": ObjectId(current_user_id)})
    
    # Update cache
    user_doc["id"] = current_user_id
    await cache.set(CacheKeys.user_profile(current_user_id), user_doc, ttl=3600)
    
    logger.info(f"User profile updated: {current_user_id}")
    
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

@router.put("/preferences", response_model=dict)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ⚙️ **Update User Preferences**
    
    Update user preferences and settings.
    
    **Preference Categories:**
    - Theme (light/dark)
    - Language
    - Notifications
    - Default currency
    """
    
    # Update preferences
    await db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {
            "$set": {
                "preferences": preferences.dict(),
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Clear cache to force refresh
    await cache.delete(CacheKeys.user_profile(current_user_id))
    
    logger.info(f"User preferences updated: {current_user_id}")
    
    return {"message": "Preferences updated successfully"}

@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    🔐 **Change Password**
    
    Change user password with current password verification.
    """
    
    # Get current user
    user_doc = await db.users.find_one({"_id": ObjectId(current_user_id)})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.currentPassword, user_doc["passwordHash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    from app.utils.security import validate_password_strength
    password_check = validate_password_strength(password_data.newPassword)
    if not password_check["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "New password does not meet security requirements",
                "errors": password_check["errors"],
                "suggestions": password_check["suggestions"]
            }
        )
    
    # Update password
    new_password_hash = get_password_hash(password_data.newPassword)
    await db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {
            "$set": {
                "passwordHash": new_password_hash,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Clear user cache
    await cache.delete(CacheKeys.user_profile(current_user_id))
    
    logger.info(f"Password changed for user: {current_user_id}")
    
    return ChangePasswordResponse(message="Password changed successfully")

@router.get("/subscription", response_model=Subscription)
async def get_user_subscription(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    💳 **Get User Subscription**
    
    Retrieve current subscription details.
    """
    
    user_doc = await db.users.find_one(
        {"_id": ObjectId(current_user_id)},
        {"subscription": 1}
    )
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return Subscription(**user_doc["subscription"])

@router.get("/api-usage", response_model=ApiUsage)
async def get_api_usage(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📊 **Get API Usage**
    
    Retrieve current API usage statistics.
    """
    
    user_doc = await db.users.find_one(
        {"_id": ObjectId(current_user_id)},
        {"apiUsage": 1}
    )
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return ApiUsage(**user_doc["apiUsage"])

@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    📷 **Upload User Avatar**
    
    Upload and update user avatar image.
    
    **Supported formats:** JPG, PNG, GIF
    **Max size:** 5MB
    """
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPG, PNG, and GIF are allowed."
        )
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    file_size = len(await file.read())
    await file.seek(0)  # Reset file pointer
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
    
    # TODO: Upload to cloud storage (AWS S3, Cloudinary, etc.)
    # For now, we'll store a placeholder URL
    avatar_url = f"https://avatars.example.com/{current_user_id}/{file.filename}"
    
    # Update user avatar
    await db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {
            "$set": {
                "avatar": avatar_url,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Clear cache
    await cache.delete(CacheKeys.user_profile(current_user_id))
    
    logger.info(f"Avatar uploaded for user: {current_user_id}")
    
    return {
        "message": "Avatar uploaded successfully",
        "avatar_url": avatar_url
    }

@router.delete("/deactivate")
async def deactivate_account(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ⚠️ **Deactivate Account**
    
    Deactivate user account (soft delete).
    """
    
    # Deactivate user
    await db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {
            "$set": {
                "isActive": False,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Clear all user caches
    await cache.delete(CacheKeys.user_profile(current_user_id))
    
    logger.info(f"Account deactivated: {current_user_id}")
    
    return {"message": "Account deactivated successfully"}

@router.get("/activity", response_model=List[dict])
async def get_user_activity(
    current_user_id: str = Depends(get_current_user_id),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📈 **Get User Activity**
    
    Retrieve user activity logs and history.
    """
    
    # Get user activities (campaigns, ads, etc.)
    activities = []
    
    # Get recent campaigns
    campaigns_cursor = db.campaigns.find(
        {"userId": ObjectId(current_user_id)},
        {"name": 1, "status": 1, "createdAt": 1, "updatedAt": 1}
    ).sort("createdAt", -1).limit(limit).skip(offset)
    
    async for campaign in campaigns_cursor:
        activities.append({
            "type": "campaign",
            "action": "created" if campaign["createdAt"] == campaign["updatedAt"] else "updated",
            "title": f"Campaign: {campaign['name']}",
            "status": campaign["status"],
            "timestamp": campaign["updatedAt"]
        })
    
    # Get recent ads
    ads_cursor = db.ads.find(
        {"userId": ObjectId(current_user_id)},
        {"title": 1, "status": 1, "createdAt": 1, "updatedAt": 1}
    ).sort("createdAt", -1).limit(limit).skip(offset)
    
    async for ad in ads_cursor:
        activities.append({
            "type": "ad",
            "action": "created" if ad["createdAt"] == ad["updatedAt"] else "updated",
            "title": f"Ad: {ad['title']}",
            "status": ad["status"],
            "timestamp": ad["updatedAt"]
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return activities[:limit]