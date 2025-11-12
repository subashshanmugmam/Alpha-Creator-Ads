"""
Campaign Management API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from bson import ObjectId

from app.database import get_db
from app.cache import CacheManager, CacheKeys
from app.models.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse
from app.utils.security import get_current_user_id
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    🚀 **Create New Campaign**
    
    Create a new advertising campaign with targeting and budget settings.
    
    **Features:**
    - Campaign setup with objectives
    - Audience targeting configuration
    - Budget and scheduling
    - Performance tracking setup
    - AI-powered optimization suggestions
    
    **Campaign Types:**
    - Brand Awareness
    - Lead Generation
    - Sales Conversion
    - Website Traffic
    - App Installs
    """
    
    # Validate user subscription limits
    user_doc = await db.users.find_one(
        {"_id": ObjectId(current_user_id)},
        {"subscription": 1, "apiUsage": 1}
    )
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check campaign limits based on subscription
    campaign_count = await db.campaigns.count_documents({"userId": ObjectId(current_user_id)})
    subscription_plan = user_doc["subscription"]["plan"]
    
    campaign_limits = {
        "free": 3,
        "basic": 10,
        "professional": 50,
        "enterprise": 1000
    }
    
    if campaign_count >= campaign_limits.get(subscription_plan, 3):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Campaign limit reached for {subscription_plan} plan"
        )
    
    # Create campaign document
    now = datetime.utcnow()
    campaign_doc = {
        "userId": ObjectId(current_user_id),
        "name": campaign_data.name,
        "description": campaign_data.description,
        "objective": campaign_data.objective,
        "status": "draft",
        "budget": campaign_data.budget.dict(),
        "schedule": campaign_data.schedule.dict() if campaign_data.schedule else None,
        "targeting": campaign_data.targeting.dict(),
        "creativeRequirements": campaign_data.creativeRequirements.dict() if campaign_data.creativeRequirements else None,
        "platforms": campaign_data.platforms,
        "tags": campaign_data.tags or [],
        "analytics": {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "spent": 0.0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpa": 0.0,
            "roas": 0.0
        },
        "optimization": {
            "autoOptimize": True,
            "bidStrategy": "auto",
            "targetCpa": None,
            "targetRoas": None
        },
        "createdAt": now,
        "updatedAt": now,
        "lastOptimized": None
    }
    
    # Insert campaign
    result = await db.campaigns.insert_one(campaign_doc)
    campaign_id = str(result.inserted_id)
    
    # Cache campaign
    campaign_doc["id"] = campaign_id
    await cache.set(CacheKeys.campaign(campaign_id), campaign_doc, ttl=3600)
    
    # Schedule AI optimization analysis (background task)
    # background_tasks.add_task(analyze_campaign_potential, campaign_id)
    
    logger.info(f"Campaign created: {campaign_id} by user {current_user_id}")
    
    return CampaignResponse(
        id=campaign_id,
        userId=current_user_id,
        name=campaign_data.name,
        description=campaign_data.description,
        objective=campaign_data.objective,
        status="draft",
        budget=campaign_data.budget,
        schedule=campaign_data.schedule,
        targeting=campaign_data.targeting,
        creativeRequirements=campaign_data.creativeRequirements,
        platforms=campaign_data.platforms,
        tags=campaign_data.tags or [],
        analytics=campaign_doc["analytics"],
        optimization=campaign_doc["optimization"],
        createdAt=now,
        updatedAt=now,
        lastOptimized=None
    )

@router.get("/", response_model=CampaignListResponse)
async def get_campaigns(
    current_user_id: str = Depends(get_current_user_id),
    status_filter: Optional[str] = Query(None, regex="^(draft|active|paused|completed|archived)$"),
    objective_filter: Optional[str] = Query(None),
    platform_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("createdAt", regex="^(createdAt|updatedAt|name|status|spent)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📋 **Get User Campaigns**
    
    Retrieve user's campaigns with filtering and sorting options.
    
    **Filters:**
    - Status (draft, active, paused, completed, archived)
    - Objective (brand_awareness, lead_generation, etc.)
    - Platform (facebook, google, instagram, etc.)
    - Search by name or description
    
    **Sorting:**
    - Creation date
    - Update date
    - Name
    - Status
    - Amount spent
    """
    
    # Build query
    query = {"userId": ObjectId(current_user_id)}
    
    if status_filter:
        query["status"] = status_filter
    
    if objective_filter:
        query["objective"] = objective_filter
    
    if platform_filter:
        query["platforms"] = platform_filter
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Build sort
    sort_direction = -1 if sort_order == "desc" else 1
    sort_field = "analytics.spent" if sort_by == "spent" else sort_by
    
    # Get total count
    total = await db.campaigns.count_documents(query)
    
    # Get campaigns
    campaigns_cursor = db.campaigns.find(query).sort(sort_field, sort_direction).skip(offset).limit(limit)
    
    campaigns = []
    async for campaign_doc in campaigns_cursor:
        campaigns.append(CampaignResponse(
            id=str(campaign_doc["_id"]),
            userId=str(campaign_doc["userId"]),
            name=campaign_doc["name"],
            description=campaign_doc["description"],
            objective=campaign_doc["objective"],
            status=campaign_doc["status"],
            budget=campaign_doc["budget"],
            schedule=campaign_doc.get("schedule"),
            targeting=campaign_doc["targeting"],
            creativeRequirements=campaign_doc.get("creativeRequirements"),
            platforms=campaign_doc["platforms"],
            tags=campaign_doc.get("tags", []),
            analytics=campaign_doc["analytics"],
            optimization=campaign_doc.get("optimization", {}),
            createdAt=campaign_doc["createdAt"],
            updatedAt=campaign_doc["updatedAt"],
            lastOptimized=campaign_doc.get("lastOptimized")
        ))
    
    return CampaignListResponse(
        campaigns=campaigns,
        total=total,
        limit=limit,
        offset=offset,
        hasMore=offset + len(campaigns) < total
    )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    📄 **Get Campaign Details**
    
    Retrieve detailed information about a specific campaign.
    """
    
    # Try cache first
    cached_campaign = await cache.get(CacheKeys.campaign(campaign_id))
    if cached_campaign and cached_campaign.get("userId") == current_user_id:
        return CampaignResponse(**cached_campaign)
    
    # Get from database
    campaign_doc = await db.campaigns.find_one({
        "_id": ObjectId(campaign_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Cache campaign
    campaign_doc["id"] = campaign_id
    campaign_doc["userId"] = current_user_id
    await cache.set(CacheKeys.campaign(campaign_id), campaign_doc, ttl=3600)
    
    return CampaignResponse(
        id=campaign_id,
        userId=current_user_id,
        name=campaign_doc["name"],
        description=campaign_doc["description"],
        objective=campaign_doc["objective"],
        status=campaign_doc["status"],
        budget=campaign_doc["budget"],
        schedule=campaign_doc.get("schedule"),
        targeting=campaign_doc["targeting"],
        creativeRequirements=campaign_doc.get("creativeRequirements"),
        platforms=campaign_doc["platforms"],
        tags=campaign_doc.get("tags", []),
        analytics=campaign_doc["analytics"],
        optimization=campaign_doc.get("optimization", {}),
        createdAt=campaign_doc["createdAt"],
        updatedAt=campaign_doc["updatedAt"],
        lastOptimized=campaign_doc.get("lastOptimized")
    )

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ✏️ **Update Campaign**
    
    Update campaign settings and configuration.
    
    **Updatable Fields:**
    - Name and description
    - Budget and schedule
    - Targeting parameters
    - Creative requirements
    - Platforms and tags
    """
    
    # Check if campaign exists and belongs to user
    existing_campaign = await db.campaigns.find_one({
        "_id": ObjectId(campaign_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if campaign can be updated (not if it's running)
    if existing_campaign["status"] == "active":
        # Only allow certain fields to be updated for active campaigns
        restricted_fields = ["budget", "schedule", "targeting"]
        update_dict = campaign_update.dict(exclude_unset=True)
        for field in restricted_fields:
            if field in update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot update {field} for active campaigns. Pause the campaign first."
                )
    
    # Prepare update data
    update_data = campaign_update.dict(exclude_unset=True)
    if update_data:
        update_data["updatedAt"] = datetime.utcnow()
        
        # Update campaign
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$set": update_data}
        )
    
    # Get updated campaign
    updated_campaign = await db.campaigns.find_one({
        "_id": ObjectId(campaign_id),
        "userId": ObjectId(current_user_id)
    })
    
    # Update cache
    updated_campaign["id"] = campaign_id
    updated_campaign["userId"] = current_user_id
    await cache.set(CacheKeys.campaign(campaign_id), updated_campaign, ttl=3600)
    
    logger.info(f"Campaign updated: {campaign_id} by user {current_user_id}")
    
    return CampaignResponse(
        id=campaign_id,
        userId=current_user_id,
        name=updated_campaign["name"],
        description=updated_campaign["description"],
        objective=updated_campaign["objective"],
        status=updated_campaign["status"],
        budget=updated_campaign["budget"],
        schedule=updated_campaign.get("schedule"),
        targeting=updated_campaign["targeting"],
        creativeRequirements=updated_campaign.get("creativeRequirements"),
        platforms=updated_campaign["platforms"],
        tags=updated_campaign.get("tags", []),
        analytics=updated_campaign["analytics"],
        optimization=updated_campaign.get("optimization", {}),
        createdAt=updated_campaign["createdAt"],
        updatedAt=updated_campaign["updatedAt"],
        lastOptimized=updated_campaign.get("lastOptimized")
    )

@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ▶️ **Start Campaign**
    
    Activate campaign and begin ad delivery.
    """
    
    # Check campaign exists and belongs to user
    campaign_doc = await db.campaigns.find_one({
        "_id": ObjectId(campaign_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign_doc["status"] == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign is already active"
        )
    
    # Check if campaign has ads
    ad_count = await db.ads.count_documents({
        "campaignId": ObjectId(campaign_id),
        "status": {"$in": ["active", "approved"]}
    })
    
    if ad_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign must have at least one active ad before starting"
        )
    
    # Update campaign status
    now = datetime.utcnow()
    await db.campaigns.update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {
                "status": "active",
                "updatedAt": now,
                "schedule.startDate": now
            }
        }
    )
    
    # Clear cache
    await cache.delete(CacheKeys.campaign(campaign_id))
    
    logger.info(f"Campaign started: {campaign_id}")
    
    return {"message": "Campaign started successfully", "status": "active"}

@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    ⏸️ **Pause Campaign**
    
    Temporarily pause campaign ad delivery.
    """
    
    # Check campaign exists and belongs to user
    campaign_doc = await db.campaigns.find_one({
        "_id": ObjectId(campaign_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign_doc["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active campaigns can be paused"
        )
    
    # Update campaign status
    await db.campaigns.update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {
                "status": "paused",
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Clear cache
    await cache.delete(CacheKeys.campaign(campaign_id))
    
    logger.info(f"Campaign paused: {campaign_id}")
    
    return {"message": "Campaign paused successfully", "status": "paused"}

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    🗑️ **Delete Campaign**
    
    Permanently delete campaign and all associated ads.
    """
    
    # Check campaign exists and belongs to user
    campaign_doc = await db.campaigns.find_one({
        "_id": ObjectId(campaign_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign_doc["status"] == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active campaign. Pause it first."
        )
    
    # Delete all associated ads first
    await db.ads.delete_many({"campaignId": ObjectId(campaign_id)})
    
    # Delete campaign
    await db.campaigns.delete_one({"_id": ObjectId(campaign_id)})
    
    # Clear cache
    await cache.delete(CacheKeys.campaign(campaign_id))
    
    logger.info(f"Campaign deleted: {campaign_id}")
    
    return {"message": "Campaign deleted successfully"}

@router.get("/{campaign_id}/analytics", response_model=Dict[str, Any])
async def get_campaign_analytics(
    campaign_id: str,
    current_user_id: str = Depends(get_current_user_id),
    date_range: str = Query("7d", regex="^(1d|7d|30d|90d|all)$"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📊 **Get Campaign Analytics**
    
    Retrieve detailed analytics and performance metrics.
    
    **Metrics Include:**
    - Impressions, clicks, conversions
    - CTR, CPC, CPA, ROAS
    - Spend and budget utilization
    - Performance by platform/audience
    - Time-based trends
    """
    
    # Check campaign exists and belongs to user
    campaign_doc = await db.campaigns.find_one({
        "_id": ObjectId(campaign_id),
        "userId": ObjectId(current_user_id)
    }, {"analytics": 1, "budget": 1, "createdAt": 1})
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Calculate date range
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
        start_date = campaign_doc["createdAt"]
    
    # Get detailed analytics from analytics collection
    analytics_pipeline = [
        {
            "$match": {
                "campaignId": ObjectId(campaign_id),
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
                "dailyMetrics": {
                    "$push": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "impressions": "$impressions",
                        "clicks": "$clicks",
                        "conversions": "$conversions",
                        "spent": "$spent"
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
        
        # Calculate derived metrics
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cpc = (total_spent / total_clicks) if total_clicks > 0 else 0
        cpa = (total_spent / total_conversions) if total_conversions > 0 else 0
        
    else:
        # Fallback to campaign analytics if no detailed data
        analytics_data = campaign_doc["analytics"]
        total_impressions = analytics_data["impressions"]
        total_clicks = analytics_data["clicks"]
        total_conversions = analytics_data["conversions"]
        total_spent = analytics_data["spent"]
        ctr = analytics_data["ctr"]
        cpc = analytics_data["cpc"]
        cpa = analytics_data["cpa"]
    
    # Budget utilization
    budget_total = campaign_doc["budget"]["amount"]
    budget_utilization = (total_spent / budget_total * 100) if budget_total > 0 else 0
    
    return {
        "campaignId": campaign_id,
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
            "cpa": round(cpa, 2) if total_conversions > 0 else None
        },
        "budget": {
            "total": budget_total,
            "spent": round(total_spent, 2),
            "remaining": round(budget_total - total_spent, 2),
            "utilization": round(budget_utilization, 1)
        },
        "dailyMetrics": analytics_result[0]["dailyMetrics"] if analytics_result else []
    }