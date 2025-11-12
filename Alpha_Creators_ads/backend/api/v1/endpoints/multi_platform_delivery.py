"""
Multi-Platform Ad Delivery API Endpoints
Provides REST API for managing ad delivery across platforms
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from core.auth import get_current_user
from core.database import get_db_session
from models import User
from services.multi_platform_delivery import (
    multi_platform_delivery,
    AdDeliveryRequest,
    DeliveryResult
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/delivery", tags=["Multi-Platform Delivery"])


class CampaignDeliveryRequest(BaseModel):
    """Campaign delivery request model"""
    campaign_id: str
    platforms: List[str]
    budget_allocation: Dict[str, float]
    start_immediately: bool = True


class BudgetOptimizationRequest(BaseModel):
    """Budget optimization request model"""
    campaign_id: str
    total_budget: float


class DeliveryStatusResponse(BaseModel):
    """Delivery status response model"""
    campaign_id: str
    platform: str
    platform_ad_id: str
    status: str
    impressions_projected: int
    reach_projected: int
    cost_estimate: float
    delivery_start: datetime


class PerformanceDataResponse(BaseModel):
    """Performance data response model"""
    platform: str
    impressions: int
    clicks: int
    conversions: int
    cost: float
    ctr: float
    conversion_rate: float
    roi: float


@router.post("/campaigns/deliver", response_model=Dict[str, Any])
async def deliver_campaign(
    request: CampaignDeliveryRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Deliver a campaign across multiple advertising platforms
    """
    try:
        # Validate campaign exists and user has access
        async with get_db_session() as db:
            campaign_result = await db.execute(
                "SELECT * FROM campaigns WHERE id = :id AND user_id = :user_id",
                {"id": request.campaign_id, "user_id": current_user.id}
            )
            campaign = campaign_result.first()
            
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found or access denied"
                )
        
        # Validate platforms
        supported_platforms = ["google", "facebook", "linkedin"]
        invalid_platforms = [p for p in request.platforms if p not in supported_platforms]
        if invalid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platforms: {invalid_platforms}"
            )
        
        # Validate budget allocation
        total_allocated = sum(request.budget_allocation.values())
        if total_allocated <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total budget allocation must be greater than 0"
            )
        
        # Deliver campaign
        if request.start_immediately:
            delivery_results = await multi_platform_delivery.deliver_campaign(
                request.campaign_id,
                request.platforms,
                request.budget_allocation
            )
        else:
            # Schedule for later delivery
            background_tasks.add_task(
                multi_platform_delivery.deliver_campaign,
                request.campaign_id,
                request.platforms,
                request.budget_allocation
            )
            delivery_results = {"scheduled": True, "message": "Campaign delivery scheduled"}
        
        logger.info(f"Campaign {request.campaign_id} delivered by user {current_user.id}")
        
        return {
            "success": True,
            "campaign_id": request.campaign_id,
            "delivery_results": delivery_results,
            "platforms": request.platforms,
            "total_budget": total_allocated
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign delivery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Campaign delivery failed"
        )


@router.get("/campaigns/{campaign_id}/status", response_model=List[DeliveryStatusResponse])
async def get_campaign_delivery_status(
    campaign_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get delivery status for a campaign across all platforms
    """
    try:
        # Validate campaign access
        async with get_db_session() as db:
            campaign_result = await db.execute(
                "SELECT * FROM campaigns WHERE id = :id AND user_id = :user_id",
                {"id": campaign_id, "user_id": current_user.id}
            )
            campaign = campaign_result.first()
            
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found or access denied"
                )
            
            # Get delivery records
            deliveries_result = await db.execute("""
                SELECT * FROM platform_deliveries 
                WHERE campaign_id = :campaign_id
                ORDER BY created_at DESC
            """, {"campaign_id": campaign_id})
            
            deliveries = deliveries_result.all()
            
            delivery_status = []
            for delivery in deliveries:
                delivery_status.append(DeliveryStatusResponse(
                    campaign_id=delivery.campaign_id,
                    platform=delivery.platform,
                    platform_ad_id=delivery.platform_ad_id,
                    status=delivery.status,
                    impressions_projected=delivery.impressions_projected,
                    reach_projected=delivery.reach_projected,
                    cost_estimate=delivery.cost_estimate,
                    delivery_start=delivery.delivery_start
                ))
            
            return delivery_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get delivery status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve delivery status"
        )


@router.get("/campaigns/{campaign_id}/performance", response_model=Dict[str, PerformanceDataResponse])
async def get_campaign_performance(
    campaign_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get performance data for a campaign across all platforms
    """
    try:
        # Validate campaign access
        async with get_db_session() as db:
            campaign_result = await db.execute(
                "SELECT * FROM campaigns WHERE id = :id AND user_id = :user_id",
                {"id": campaign_id, "user_id": current_user.id}
            )
            campaign = campaign_result.first()
            
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found or access denied"
                )
        
        # Get performance data
        performance_data = await multi_platform_delivery.get_campaign_performance(campaign_id)
        
        # Format response
        formatted_performance = {}
        for platform, data in performance_data.items():
            if "error" in data:
                continue
                
            # Calculate ROI (assuming $50 per conversion)
            conversions = data.get("conversions", 0)
            cost = data.get("cost", 0)
            revenue = conversions * 50
            roi = (revenue - cost) / cost * 100 if cost > 0 else 0
            
            formatted_performance[platform] = PerformanceDataResponse(
                platform=platform,
                impressions=data.get("impressions", 0),
                clicks=data.get("clicks", 0),
                conversions=conversions,
                cost=cost,
                ctr=data.get("ctr", 0.0),
                conversion_rate=data.get("conversion_rate", 0.0),
                roi=roi
            )
        
        return formatted_performance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance data"
        )


@router.post("/campaigns/{campaign_id}/optimize-budget", response_model=Dict[str, float])
async def optimize_campaign_budget(
    campaign_id: str,
    request: BudgetOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Optimize budget allocation across platforms based on performance
    """
    try:
        # Validate campaign access
        async with get_db_session() as db:
            campaign_result = await db.execute(
                "SELECT * FROM campaigns WHERE id = :id AND user_id = :user_id",
                {"id": campaign_id, "user_id": current_user.id}
            )
            campaign = campaign_result.first()
            
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found or access denied"
                )
        
        if request.total_budget <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total budget must be greater than 0"
            )
        
        # Optimize budget allocation
        optimized_allocation = await multi_platform_delivery.optimize_budget_allocation(
            campaign_id, request.total_budget
        )
        
        logger.info(f"Budget optimized for campaign {campaign_id}")
        
        return optimized_allocation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Budget optimization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Budget optimization failed"
        )


@router.get("/platforms", response_model=List[Dict[str, Any]])
async def get_supported_platforms(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of supported advertising platforms
    """
    platforms = [
        {
            "id": "google",
            "name": "Google Ads",
            "description": "Search and display advertising on Google",
            "supported_formats": ["text", "display", "video"],
            "min_budget": 10.0,
            "recommended_budget": 100.0
        },
        {
            "id": "facebook",
            "name": "Facebook Ads",
            "description": "Social media advertising on Facebook and Instagram",
            "supported_formats": ["image", "video", "carousel"],
            "min_budget": 5.0,
            "recommended_budget": 50.0
        },
        {
            "id": "linkedin",
            "name": "LinkedIn Ads",
            "description": "Professional network advertising",
            "supported_formats": ["text", "image", "video"],
            "min_budget": 25.0,
            "recommended_budget": 200.0
        }
    ]
    
    return platforms


@router.post("/campaigns/{campaign_id}/pause", response_model=Dict[str, str])
async def pause_campaign_delivery(
    campaign_id: str,
    platforms: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Pause campaign delivery on specified platforms (or all platforms)
    """
    try:
        # Validate campaign access
        async with get_db_session() as db:
            campaign_result = await db.execute(
                "SELECT * FROM campaigns WHERE id = :id AND user_id = :user_id",
                {"id": campaign_id, "user_id": current_user.id}
            )
            campaign = campaign_result.first()
            
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found or access denied"
                )
            
            # Get platform deliveries to pause
            if platforms:
                deliveries_result = await db.execute("""
                    SELECT * FROM platform_deliveries 
                    WHERE campaign_id = :campaign_id AND platform = ANY(:platforms)
                """, {"campaign_id": campaign_id, "platforms": platforms})
            else:
                deliveries_result = await db.execute("""
                    SELECT * FROM platform_deliveries 
                    WHERE campaign_id = :campaign_id
                """, {"campaign_id": campaign_id})
            
            deliveries = deliveries_result.all()
            
            # In a real implementation, this would make API calls to pause campaigns
            paused_platforms = []
            for delivery in deliveries:
                # Update status in database
                await db.execute("""
                    UPDATE platform_deliveries 
                    SET status = 'PAUSED', updated_at = :updated_at
                    WHERE id = :id
                """, {
                    "id": delivery.id,
                    "updated_at": datetime.utcnow()
                })
                paused_platforms.append(delivery.platform)
            
            await db.commit()
            
            logger.info(f"Campaign {campaign_id} paused on platforms: {paused_platforms}")
            
            return {
                "message": f"Campaign paused on platforms: {', '.join(paused_platforms)}",
                "campaign_id": campaign_id,
                "paused_platforms": str(paused_platforms)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause campaign"
        )


@router.post("/campaigns/{campaign_id}/resume", response_model=Dict[str, str])
async def resume_campaign_delivery(
    campaign_id: str,
    platforms: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Resume campaign delivery on specified platforms (or all platforms)
    """
    try:
        # Validate campaign access
        async with get_db_session() as db:
            campaign_result = await db.execute(
                "SELECT * FROM campaigns WHERE id = :id AND user_id = :user_id",
                {"id": campaign_id, "user_id": current_user.id}
            )
            campaign = campaign_result.first()
            
            if not campaign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found or access denied"
                )
            
            # Get platform deliveries to resume
            if platforms:
                deliveries_result = await db.execute("""
                    SELECT * FROM platform_deliveries 
                    WHERE campaign_id = :campaign_id AND platform = ANY(:platforms)
                """, {"campaign_id": campaign_id, "platforms": platforms})
            else:
                deliveries_result = await db.execute("""
                    SELECT * FROM platform_deliveries 
                    WHERE campaign_id = :campaign_id
                """, {"campaign_id": campaign_id})
            
            deliveries = deliveries_result.all()
            
            # In a real implementation, this would make API calls to resume campaigns
            resumed_platforms = []
            for delivery in deliveries:
                # Update status in database
                await db.execute("""
                    UPDATE platform_deliveries 
                    SET status = 'ACTIVE', updated_at = :updated_at
                    WHERE id = :id
                """, {
                    "id": delivery.id,
                    "updated_at": datetime.utcnow()
                })
                resumed_platforms.append(delivery.platform)
            
            await db.commit()
            
            logger.info(f"Campaign {campaign_id} resumed on platforms: {resumed_platforms}")
            
            return {
                "message": f"Campaign resumed on platforms: {', '.join(resumed_platforms)}",
                "campaign_id": campaign_id,
                "resumed_platforms": str(resumed_platforms)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume campaign"
        )
