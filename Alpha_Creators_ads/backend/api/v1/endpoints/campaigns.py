"""
Campaign management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from core.database import get_db_session
from models import User, Campaign, AdCreative
from services.authentication import get_current_user

router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_audience: Dict[str, Any]
    budget: float
    daily_budget: Optional[float] = None
    start_date: datetime
    end_date: Optional[datetime] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[Dict[str, Any]] = None
    budget: Optional[float] = None
    daily_budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None

class CampaignResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    description: Optional[str]
    target_audience: Dict[str, Any]
    budget: float
    daily_budget: Optional[float]
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    is_active: bool
    impressions: int
    clicks: int
    conversions: int
    spend: float
    ctr: float
    conversion_rate: float
    created_at: datetime
    updated_at: datetime

class AdCreativeCreate(BaseModel):
    headline: str
    description: Optional[str] = None
    cta_text: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    target_emotions: List[str] = []
    target_audience: Dict[str, Any] = {}

class AdCreativeResponse(BaseModel):
    id: str
    campaign_id: str
    headline: str
    description: Optional[str]
    cta_text: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    target_emotions: List[str]
    target_audience: Dict[str, Any]
    ai_model_used: Optional[str]
    confidence_score: Optional[float]
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    conversion_rate: float
    created_at: datetime


@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all campaigns for the current user"""
    query = "SELECT * FROM campaigns WHERE owner_id = :owner_id"
    params = {"owner_id": current_user.id}
    
    if status:
        query += " AND status = :status"
        params["status"] = status
    
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
    params.update({"limit": limit, "skip": skip})
    
    result = await db.execute(query, params)
    campaigns = result.all()
    
    return [
        CampaignResponse(
            id=campaign.id,
            owner_id=campaign.owner_id,
            name=campaign.name,
            description=campaign.description,
            target_audience=campaign.target_audience or {},
            budget=campaign.budget,
            daily_budget=campaign.daily_budget,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            status=campaign.status,
            is_active=campaign.is_active,
            impressions=campaign.impressions,
            clicks=campaign.clicks,
            conversions=campaign.conversions,
            spend=campaign.spend,
            ctr=campaign.ctr,
            conversion_rate=campaign.conversion_rate,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at
        )
        for campaign in campaigns
    ]


@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new campaign"""
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can create campaigns"
        )
    
    campaign = Campaign(
        id=str(uuid.uuid4()),
        owner_id=current_user.id,
        name=campaign_data.name,
        description=campaign_data.description,
        target_audience=campaign_data.target_audience,
        budget=campaign_data.budget,
        daily_budget=campaign_data.daily_budget,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        status="draft"
    )
    
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    
    return CampaignResponse(
        id=campaign.id,
        owner_id=campaign.owner_id,
        name=campaign.name,
        description=campaign.description,
        target_audience=campaign.target_audience or {},
        budget=campaign.budget,
        daily_budget=campaign.daily_budget,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        status=campaign.status,
        is_active=campaign.is_active,
        impressions=campaign.impressions,
        clicks=campaign.clicks,
        conversions=campaign.conversions,
        spend=campaign.spend,
        ctr=campaign.ctr,
        conversion_rate=campaign.conversion_rate,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific campaign"""
    result = await db.execute(
        "SELECT * FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": campaign_id, "owner_id": current_user.id}
    )
    campaign = result.first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignResponse(
        id=campaign.id,
        owner_id=campaign.owner_id,
        name=campaign.name,
        description=campaign.description,
        target_audience=campaign.target_audience or {},
        budget=campaign.budget,
        daily_budget=campaign.daily_budget,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        status=campaign.status,
        is_active=campaign.is_active,
        impressions=campaign.impressions,
        clicks=campaign.clicks,
        conversions=campaign.conversions,
        spend=campaign.spend,
        ctr=campaign.ctr,
        conversion_rate=campaign.conversion_rate,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at
    )


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a campaign"""
    result = await db.execute(
        "SELECT * FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": campaign_id, "owner_id": current_user.id}
    )
    campaign = result.first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update fields
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    campaign.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(campaign)
    
    return CampaignResponse(
        id=campaign.id,
        owner_id=campaign.owner_id,
        name=campaign.name,
        description=campaign.description,
        target_audience=campaign.target_audience or {},
        budget=campaign.budget,
        daily_budget=campaign.daily_budget,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        status=campaign.status,
        is_active=campaign.is_active,
        impressions=campaign.impressions,
        clicks=campaign.clicks,
        conversions=campaign.conversions,
        spend=campaign.spend,
        ctr=campaign.ctr,
        conversion_rate=campaign.conversion_rate,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at
    )


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a campaign"""
    result = await db.execute(
        "SELECT * FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": campaign_id, "owner_id": current_user.id}
    )
    campaign = result.first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    await db.execute(
        "DELETE FROM campaigns WHERE id = :id",
        {"id": campaign_id}
    )
    await db.commit()
    
    return {"message": "Campaign deleted successfully"}


@router.get("/{campaign_id}/creatives", response_model=List[AdCreativeResponse])
async def get_campaign_creatives(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all ad creatives for a campaign"""
    # Verify campaign ownership
    campaign_result = await db.execute(
        "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": campaign_id, "owner_id": current_user.id}
    )
    if not campaign_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    result = await db.execute(
        "SELECT * FROM ad_creatives WHERE campaign_id = :campaign_id ORDER BY created_at DESC",
        {"campaign_id": campaign_id}
    )
    creatives = result.all()
    
    return [
        AdCreativeResponse(
            id=creative.id,
            campaign_id=creative.campaign_id,
            headline=creative.headline,
            description=creative.description,
            cta_text=creative.cta_text,
            image_url=creative.image_url,
            video_url=creative.video_url,
            target_emotions=creative.target_emotions or [],
            target_audience=creative.target_audience or {},
            ai_model_used=creative.ai_model_used,
            confidence_score=creative.confidence_score,
            impressions=creative.impressions,
            clicks=creative.clicks,
            conversions=creative.conversions,
            ctr=creative.ctr,
            conversion_rate=creative.conversion_rate,
            created_at=creative.created_at
        )
        for creative in creatives
    ]


@router.post("/{campaign_id}/creatives", response_model=AdCreativeResponse)
async def create_ad_creative(
    campaign_id: str,
    creative_data: AdCreativeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new ad creative for a campaign"""
    # Verify campaign ownership
    campaign_result = await db.execute(
        "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": campaign_id, "owner_id": current_user.id}
    )
    if not campaign_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    creative = AdCreative(
        id=str(uuid.uuid4()),
        campaign_id=campaign_id,
        headline=creative_data.headline,
        description=creative_data.description,
        cta_text=creative_data.cta_text,
        image_url=creative_data.image_url,
        video_url=creative_data.video_url,
        target_emotions=creative_data.target_emotions,
        target_audience=creative_data.target_audience
    )
    
    db.add(creative)
    await db.commit()
    await db.refresh(creative)
    
    return AdCreativeResponse(
        id=creative.id,
        campaign_id=creative.campaign_id,
        headline=creative.headline,
        description=creative.description,
        cta_text=creative.cta_text,
        image_url=creative.image_url,
        video_url=creative.video_url,
        target_emotions=creative.target_emotions or [],
        target_audience=creative.target_audience or {},
        ai_model_used=creative.ai_model_used,
        confidence_score=creative.confidence_score,
        impressions=creative.impressions,
        clicks=creative.clicks,
        conversions=creative.conversions,
        ctr=creative.ctr,
        conversion_rate=creative.conversion_rate,
        created_at=creative.created_at
    )
