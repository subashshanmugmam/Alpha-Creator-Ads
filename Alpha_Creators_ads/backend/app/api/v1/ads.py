"""
Ad Management API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from bson import ObjectId

from app.database import get_db
from app.cache import CacheManager, CacheKeys
from app.models.ad import AdCreate, AdUpdate, AdResponse, AdListResponse, AdContent
from app.utils.security import get_current_user_id
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
async def create_ad(
    ad_data: AdCreate,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    🎨 **Create New Ad**
    
    Create a new advertisement with content and targeting.
    
    **Features:**
    - Multiple ad formats (image, video, carousel, collection)
    - AI-powered content generation
    - Auto-optimization settings
    - A/B testing capabilities
    - Platform-specific formatting
    
    **Ad Types:**
    - Single Image/Video
    - Carousel (multiple images)
    - Collection (product catalog)
    - Story (vertical format)
    - Reel (short video)
    """
    
    # Verify campaign exists and belongs to user
    campaign_doc = await db.campaigns.find_one({
        "_id": ObjectId(ad_data.campaignId),
        "userId": ObjectId(current_user_id)
    })
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check ad limits based on subscription
    user_doc = await db.users.find_one(
        {"_id": ObjectId(current_user_id)},
        {"subscription": 1, "apiUsage": 1}
    )
    
    ad_count = await db.ads.count_documents({
        "userId": ObjectId(current_user_id),
        "campaignId": ObjectId(ad_data.campaignId)
    })
    
    subscription_plan = user_doc["subscription"]["plan"]
    ad_limits = {
        "free": 10,
        "basic": 50,
        "professional": 200,
        "enterprise": 1000
    }
    
    if ad_count >= ad_limits.get(subscription_plan, 10):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Ad limit reached for {subscription_plan} plan"
        )
    
    # Create ad document
    now = datetime.utcnow()
    ad_doc = {
        "userId": ObjectId(current_user_id),
        "campaignId": ObjectId(ad_data.campaignId),
        "title": ad_data.title,
        "description": ad_data.description,
        "type": ad_data.type,
        "format": ad_data.format,
        "status": "draft",
        "content": ad_data.content.dict(),
        "targeting": ad_data.targeting.dict() if ad_data.targeting else campaign_doc.get("targeting", {}),
        "placement": ad_data.placement,
        "optimization": {
            "objective": ad_data.optimization.objective if ad_data.optimization else "clicks",
            "bidAmount": ad_data.optimization.bidAmount if ad_data.optimization else None,
            "schedule": ad_data.optimization.schedule.dict() if ad_data.optimization and ad_data.optimization.schedule else None,
            "autoOptimize": True
        },
        "analytics": {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "spent": 0.0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpa": 0.0,
            "engagement": {
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "saves": 0
            }
        },
        "aiGenerated": ad_data.aiGenerated or False,
        "variations": [],  # For A/B testing
        "createdAt": now,
        "updatedAt": now,
        "approvedAt": None,
        "publishedAt": None
    }
    
    # Insert ad
    result = await db.ads.insert_one(ad_doc)
    ad_id = str(result.inserted_id)
    
    # Cache ad
    ad_doc["id"] = ad_id
    await cache.set(CacheKeys.ad(ad_id), ad_doc, ttl=3600)
    
    # Schedule AI optimization if enabled (background task)
    if ad_data.aiGenerated:
        # background_tasks.add_task(generate_ad_variations, ad_id)
        pass
    
    # Update API usage
    await db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {
            "$inc": {
                "apiUsage.adsGenerated": 1,
                "apiUsage.apiCallsThisMonth": 1
            },
            "$set": {"updatedAt": now}
        }
    )
    
    logger.info(f"Ad created: {ad_id} for campaign {ad_data.campaignId}")
    
    return AdResponse(
        id=ad_id,
        userId=current_user_id,
        campaignId=ad_data.campaignId,
        title=ad_data.title,
        description=ad_data.description,
        type=ad_data.type,
        format=ad_data.format,
        status="draft",
        content=ad_data.content,
        targeting=ad_data.targeting,
        placement=ad_data.placement,
        optimization=ad_doc["optimization"],
        analytics=ad_doc["analytics"],
        aiGenerated=ad_data.aiGenerated or False,
        variations=[],
        createdAt=now,
        updatedAt=now,
        approvedAt=None,
        publishedAt=None
    )

@router.get("/", response_model=AdListResponse)
async def get_ads(
    current_user_id: str = Depends(get_current_user_id),
    campaign_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, regex="^(draft|pending|approved|active|paused|rejected|archived)$"),
    type_filter: Optional[str] = Query(None),
    format_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("createdAt", regex="^(createdAt|updatedAt|title|status|ctr|spent)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📝 **Get User Ads**
    
    Retrieve user's ads with filtering and sorting options.
    
    **Filters:**
    - Campaign ID
    - Status (draft, pending, approved, active, paused, rejected, archived)
    - Ad type (product, brand, promotional, etc.)
    - Format (image, video, carousel, collection)
    - Search by title or description
    
    **Sorting:**
    - Creation/update date
    - Title
    - Status
    - Performance (CTR, spent)
    """
    
    # Build query
    query = {"userId": ObjectId(current_user_id)}
    
    if campaign_id:
        query["campaignId"] = ObjectId(campaign_id)
    
    if status_filter:
        query["status"] = status_filter
    
    if type_filter:
        query["type"] = type_filter
    
    if format_filter:
        query["format"] = format_filter
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Build sort
    sort_direction = -1 if sort_order == "desc" else 1
    sort_field = "analytics.ctr" if sort_by == "ctr" else "analytics.spent" if sort_by == "spent" else sort_by
    
    # Get total count
    total = await db.ads.count_documents(query)
    
    # Get ads
    ads_cursor = db.ads.find(query).sort(sort_field, sort_direction).skip(offset).limit(limit)
    
    ads = []
    async for ad_doc in ads_cursor:
        ads.append(AdResponse(
            id=str(ad_doc["_id"]),
            userId=str(ad_doc["userId"]),
            campaignId=str(ad_doc["campaignId"]),
            title=ad_doc["title"],
            description=ad_doc["description"],
            type=ad_doc["type"],
            format=ad_doc["format"],
            status=ad_doc["status"],
            content=AdContent(**ad_doc["content"]),
            targeting=ad_doc.get("targeting"),
            placement=ad_doc["placement"],
            optimization=ad_doc["optimization"],
            analytics=ad_doc["analytics"],
            aiGenerated=ad_doc.get("aiGenerated", False),
            variations=ad_doc.get("variations", []),
            createdAt=ad_doc["createdAt"],
            updatedAt=ad_doc["updatedAt"],
            approvedAt=ad_doc.get("approvedAt"),
            publishedAt=ad_doc.get("publishedAt")
        ))
    
    return AdListResponse(
        ads=ads,
        total=total,
        limit=limit,
        offset=offset,
        hasMore=offset + len(ads) < total
    )

@router.get("/{ad_id}", response_model=AdResponse)
async def get_ad(
    ad_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    📄 **Get Ad Details**
    
    Retrieve detailed information about a specific ad.
    """
    
    # Try cache first
    cached_ad = await cache.get(CacheKeys.ad(ad_id))
    if cached_ad and cached_ad.get("userId") == current_user_id:
        return AdResponse(**cached_ad)
    
    # Get from database
    ad_doc = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not ad_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    # Cache ad
    ad_doc["id"] = ad_id
    ad_doc["userId"] = current_user_id
    ad_doc["campaignId"] = str(ad_doc["campaignId"])
    await cache.set(CacheKeys.ad(ad_id), ad_doc, ttl=3600)
    
    return AdResponse(
        id=ad_id,
        userId=current_user_id,
        campaignId=str(ad_doc["campaignId"]),
        title=ad_doc["title"],
        description=ad_doc["description"],
        type=ad_doc["type"],
        format=ad_doc["format"],
        status=ad_doc["status"],
        content=AdContent(**ad_doc["content"]),
        targeting=ad_doc.get("targeting"),
        placement=ad_doc["placement"],
        optimization=ad_doc["optimization"],
        analytics=ad_doc["analytics"],
        aiGenerated=ad_doc.get("aiGenerated", False),
        variations=ad_doc.get("variations", []),
        createdAt=ad_doc["createdAt"],
        updatedAt=ad_doc["updatedAt"],
        approvedAt=ad_doc.get("approvedAt"),
        publishedAt=ad_doc.get("publishedAt")
    )

@router.put("/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: str,
    ad_update: AdUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ✏️ **Update Ad**
    
    Update ad content, targeting, and optimization settings.
    
    **Updatable Fields:**
    - Title and description
    - Content (images, videos, text)
    - Targeting parameters
    - Placement options
    - Optimization settings
    """
    
    # Check if ad exists and belongs to user
    existing_ad = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not existing_ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    # Check if ad can be updated (not if it's active)
    if existing_ad["status"] == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update active ads. Pause the ad first."
        )
    
    # Prepare update data
    update_data = ad_update.dict(exclude_unset=True)
    if update_data:
        update_data["updatedAt"] = datetime.utcnow()
        
        # Reset approval if content changed
        if any(field in update_data for field in ["title", "description", "content"]):
            update_data["status"] = "draft"
            update_data["approvedAt"] = None
        
        # Update ad
        await db.ads.update_one(
            {"_id": ObjectId(ad_id)},
            {"$set": update_data}
        )
    
    # Get updated ad
    updated_ad = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    })
    
    # Update cache
    updated_ad["id"] = ad_id
    updated_ad["userId"] = current_user_id
    updated_ad["campaignId"] = str(updated_ad["campaignId"])
    await cache.set(CacheKeys.ad(ad_id), updated_ad, ttl=3600)
    
    logger.info(f"Ad updated: {ad_id} by user {current_user_id}")
    
    return AdResponse(
        id=ad_id,
        userId=current_user_id,
        campaignId=str(updated_ad["campaignId"]),
        title=updated_ad["title"],
        description=updated_ad["description"],
        type=updated_ad["type"],
        format=updated_ad["format"],
        status=updated_ad["status"],
        content=AdContent(**updated_ad["content"]),
        targeting=updated_ad.get("targeting"),
        placement=updated_ad["placement"],
        optimization=updated_ad["optimization"],
        analytics=updated_ad["analytics"],
        aiGenerated=updated_ad.get("aiGenerated", False),
        variations=updated_ad.get("variations", []),
        createdAt=updated_ad["createdAt"],
        updatedAt=updated_ad["updatedAt"],
        approvedAt=updated_ad.get("approvedAt"),
        publishedAt=updated_ad.get("publishedAt")
    )

@router.post("/{ad_id}/submit-for-review")
async def submit_ad_for_review(
    ad_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    📋 **Submit Ad for Review**
    
    Submit ad for platform review and approval.
    """
    
    # Check ad exists and belongs to user
    ad_doc = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not ad_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    if ad_doc["status"] != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft ads can be submitted for review"
        )
    
    # Validate ad content completeness
    content = ad_doc["content"]
    if not content.get("primaryText") and not content.get("headline"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ad must have either primary text or headline"
        )
    
    if not content.get("images") and not content.get("videos"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ad must have at least one image or video"
        )
    
    # Update ad status
    await db.ads.update_one(
        {"_id": ObjectId(ad_id)},
        {
            "$set": {
                "status": "pending",
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Clear cache
    await cache.delete(CacheKeys.ad(ad_id))
    
    logger.info(f"Ad submitted for review: {ad_id}")
    
    return {"message": "Ad submitted for review successfully", "status": "pending"}

@router.post("/{ad_id}/activate")
async def activate_ad(
    ad_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ▶️ **Activate Ad**
    
    Activate approved ad and begin delivery.
    """
    
    # Check ad exists and belongs to user
    ad_doc = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not ad_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    if ad_doc["status"] != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved ads can be activated"
        )
    
    # Check if campaign is active
    campaign_doc = await db.campaigns.find_one(
        {"_id": ad_doc["campaignId"]},
        {"status": 1}
    )
    
    if campaign_doc["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign must be active to activate ads"
        )
    
    # Update ad status
    now = datetime.utcnow()
    await db.ads.update_one(
        {"_id": ObjectId(ad_id)},
        {
            "$set": {
                "status": "active",
                "publishedAt": now,
                "updatedAt": now
            }
        }
    )
    
    # Clear cache
    await cache.delete(CacheKeys.ad(ad_id))
    
    logger.info(f"Ad activated: {ad_id}")
    
    return {"message": "Ad activated successfully", "status": "active"}

@router.post("/{ad_id}/pause")
async def pause_ad(
    ad_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ⏸️ **Pause Ad**
    
    Temporarily pause ad delivery.
    """
    
    # Check ad exists and belongs to user
    ad_doc = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not ad_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    if ad_doc["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active ads can be paused"
        )
    
    # Update ad status
    await db.ads.update_one(
        {"_id": ObjectId(ad_id)},
        {
            "$set": {
                "status": "paused",
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Clear cache
    await cache.delete(CacheKeys.ad(ad_id))
    
    logger.info(f"Ad paused: {ad_id}")
    
    return {"message": "Ad paused successfully", "status": "paused"}

@router.delete("/{ad_id}")
async def delete_ad(
    ad_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    🗑️ **Delete Ad**
    
    Permanently delete ad.
    """
    
    # Check ad exists and belongs to user
    ad_doc = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not ad_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    if ad_doc["status"] == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active ad. Pause it first."
        )
    
    # Delete ad
    await db.ads.delete_one({"_id": ObjectId(ad_id)})
    
    # Clear cache
    await cache.delete(CacheKeys.ad(ad_id))
    
    logger.info(f"Ad deleted: {ad_id}")
    
    return {"message": "Ad deleted successfully"}

@router.get("/{ad_id}/analytics", response_model=Dict[str, Any])
async def get_ad_analytics(
    ad_id: str,
    current_user_id: str = Depends(get_current_user_id),
    date_range: str = Query("7d", regex="^(1d|7d|30d|90d|all)$"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📊 **Get Ad Analytics**
    
    Retrieve detailed analytics and performance metrics for specific ad.
    
    **Metrics Include:**
    - Impressions, clicks, conversions
    - CTR, CPC, CPA
    - Engagement (likes, shares, comments, saves)
    - Audience breakdown
    - Performance trends
    """
    
    # Check ad exists and belongs to user
    ad_doc = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    }, {"analytics": 1, "createdAt": 1, "publishedAt": 1})
    
    if not ad_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    # Calculate date range
    from datetime import timedelta
    now = datetime.utcnow()
    if date_range == "1d":
        start_date = now - timedelta(days=1)
    elif date_range == "7d":
        start_date = now - timedelta(days=7)
    elif date_range == "30d":
        start_date = now - timedelta(days=30)
    elif date_range == "90d":
        start_date = now - timedelta(days=90)
    else:  # all
        start_date = ad_doc.get("publishedAt", ad_doc["createdAt"])
    
    # Get detailed analytics from analytics collection
    analytics_pipeline = [
        {
            "$match": {
                "adId": ObjectId(ad_id),
                "timestamp": {"$gte": start_date, "$lte": now}
            }
        },
        {
            "$group": {
                "_id": None,
                "totalImpressions": {"$sum": "$impressions"},
                "totalClicks": {"$sum": "$clicks"},
                "totalConversions": {"$sum": "$conversions"},
                "totalSpent": {"$sum": "$spent"},
                "totalEngagement": {"$sum": "$engagement.total"},
                "dailyMetrics": {
                    "$push": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "impressions": "$impressions",
                        "clicks": "$clicks",
                        "conversions": "$conversions",
                        "spent": "$spent",
                        "engagement": "$engagement"
                    }
                }
            }
        }
    ]
    
    # Execute analytics aggregation
    analytics_result = await db.analytics.aggregate(analytics_pipeline).to_list(1)
    
    if analytics_result:
        analytics_data = analytics_result[0]
        total_impressions = analytics_data["totalImpressions"]
        total_clicks = analytics_data["totalClicks"]
        total_conversions = analytics_data["totalConversions"]
        total_spent = analytics_data["totalSpent"]
        total_engagement = analytics_data["totalEngagement"]
        
        # Calculate derived metrics
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cpc = (total_spent / total_clicks) if total_clicks > 0 else 0
        cpa = (total_spent / total_conversions) if total_conversions > 0 else 0
        engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0
        
    else:
        # Fallback to ad analytics if no detailed data
        analytics_data = ad_doc["analytics"]
        total_impressions = analytics_data["impressions"]
        total_clicks = analytics_data["clicks"]
        total_conversions = analytics_data["conversions"]
        total_spent = analytics_data["spent"]
        ctr = analytics_data["ctr"]
        cpc = analytics_data["cpc"]
        cpa = analytics_data["cpa"]
        total_engagement = sum(analytics_data["engagement"].values())
        engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0
    
    return {
        "adId": ad_id,
        "dateRange": date_range,
        "startDate": start_date.isoformat(),
        "endDate": now.isoformat(),
        "metrics": {
            "impressions": total_impressions,
            "clicks": total_clicks,
            "conversions": total_conversions,
            "spent": round(total_spent, 2),
            "ctr": round(ctr, 2),
            "cpc": round(cpc, 2),
            "cpa": round(cpa, 2) if total_conversions > 0 else None,
            "engagement": {
                "total": total_engagement,
                "rate": round(engagement_rate, 2)
            }
        },
        "dailyMetrics": analytics_result[0]["dailyMetrics"] if analytics_result else []
    }

@router.post("/{ad_id}/duplicate", response_model=AdResponse)
async def duplicate_ad(
    ad_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📋 **Duplicate Ad**
    
    Create a copy of an existing ad.
    """
    
    # Get original ad
    original_ad = await db.ads.find_one({
        "_id": ObjectId(ad_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not original_ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    # Create duplicate
    now = datetime.utcnow()
    duplicate_ad = original_ad.copy()
    del duplicate_ad["_id"]
    duplicate_ad["title"] = f"{original_ad['title']} - Copy"
    duplicate_ad["status"] = "draft"
    duplicate_ad["analytics"] = {
        "impressions": 0,
        "clicks": 0,
        "conversions": 0,
        "spent": 0.0,
        "ctr": 0.0,
        "cpc": 0.0,
        "cpa": 0.0,
        "engagement": {
            "likes": 0,
            "shares": 0,
            "comments": 0,
            "saves": 0
        }
    }
    duplicate_ad["createdAt"] = now
    duplicate_ad["updatedAt"] = now
    duplicate_ad["approvedAt"] = None
    duplicate_ad["publishedAt"] = None
    
    # Insert duplicate
    result = await db.ads.insert_one(duplicate_ad)
    duplicate_id = str(result.inserted_id)
    
    logger.info(f"Ad duplicated: {ad_id} -> {duplicate_id}")
    
    return AdResponse(
        id=duplicate_id,
        userId=current_user_id,
        campaignId=str(duplicate_ad["campaignId"]),
        title=duplicate_ad["title"],
        description=duplicate_ad["description"],
        type=duplicate_ad["type"],
        format=duplicate_ad["format"],
        status=duplicate_ad["status"],
        content=AdContent(**duplicate_ad["content"]),
        targeting=duplicate_ad.get("targeting"),
        placement=duplicate_ad["placement"],
        optimization=duplicate_ad["optimization"],
        analytics=duplicate_ad["analytics"],
        aiGenerated=duplicate_ad.get("aiGenerated", False),
        variations=duplicate_ad.get("variations", []),
        createdAt=duplicate_ad["createdAt"],
        updatedAt=duplicate_ad["updatedAt"],
        approvedAt=duplicate_ad.get("approvedAt"),
        publishedAt=duplicate_ad.get("publishedAt")
    )