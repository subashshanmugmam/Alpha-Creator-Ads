"""
Analytics and performance monitoring endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import json

from core.database import get_db_session, get_influx_client
from models import User, Campaign, AdCreative, AdDelivery, SystemMetrics
from services.authentication import get_current_user

router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class CampaignPerformance(BaseModel):
    campaign_id: str
    campaign_name: str
    impressions: int
    clicks: int
    conversions: int
    spend: float
    ctr: float
    conversion_rate: float
    cost_per_click: float
    cost_per_conversion: float
    return_on_ad_spend: float

class AdCreativePerformance(BaseModel):
    creative_id: str
    campaign_id: str
    headline: str
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    conversion_rate: float

class AudienceInsights(BaseModel):
    age_groups: Dict[str, int]
    genders: Dict[str, int]
    locations: Dict[str, int]
    interests: Dict[str, int]
    engagement_by_emotion: Dict[str, float]

class PerformanceMetrics(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_spend: float
    average_ctr: float
    average_conversion_rate: float
    average_cost_per_click: float

class TimeSeriesData(BaseModel):
    timestamp: datetime
    impressions: int
    clicks: int
    conversions: int
    spend: float

class SystemPerformance(BaseModel):
    api_response_time: float
    nlp_processing_time: float
    ad_generation_time: float
    posts_processed_per_hour: int
    system_uptime: float
    error_rate: float


@router.get("/overview", response_model=PerformanceMetrics)
async def get_performance_overview(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get overall performance metrics for user's campaigns"""
    
    # Set default date range if not provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get campaign performance
    query = """
    SELECT 
        COUNT(*) as total_campaigns,
        SUM(CASE WHEN is_active = true THEN 1 ELSE 0 END) as active_campaigns,
        SUM(impressions) as total_impressions,
        SUM(clicks) as total_clicks,
        SUM(conversions) as total_conversions,
        SUM(spend) as total_spend,
        AVG(ctr) as average_ctr,
        AVG(conversion_rate) as average_conversion_rate
    FROM campaigns 
    WHERE owner_id = :owner_id
    AND created_at >= :start_date 
    AND created_at <= :end_date
    """
    
    result = await db.execute(query, {
        "owner_id": current_user.id,
        "start_date": start_date,
        "end_date": end_date
    })
    
    metrics = result.first()
    
    # Calculate cost per click
    avg_cpc = 0.0
    if metrics.total_clicks > 0:
        avg_cpc = metrics.total_spend / metrics.total_clicks
    
    return PerformanceMetrics(
        total_campaigns=metrics.total_campaigns or 0,
        active_campaigns=metrics.active_campaigns or 0,
        total_impressions=metrics.total_impressions or 0,
        total_clicks=metrics.total_clicks or 0,
        total_conversions=metrics.total_conversions or 0,
        total_spend=metrics.total_spend or 0.0,
        average_ctr=metrics.average_ctr or 0.0,
        average_conversion_rate=metrics.average_conversion_rate or 0.0,
        average_cost_per_click=avg_cpc
    )


@router.get("/campaigns", response_model=List[CampaignPerformance])
async def get_campaign_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get performance analytics for all campaigns"""
    
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    query = """
    SELECT 
        id, name, impressions, clicks, conversions, spend, ctr, conversion_rate
    FROM campaigns 
    WHERE owner_id = :owner_id
    AND created_at >= :start_date 
    AND created_at <= :end_date
    ORDER BY spend DESC
    LIMIT :limit
    """
    
    result = await db.execute(query, {
        "owner_id": current_user.id,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    })
    
    campaigns = result.all()
    
    performance_data = []
    for campaign in campaigns:
        # Calculate additional metrics
        cost_per_click = campaign.spend / campaign.clicks if campaign.clicks > 0 else 0.0
        cost_per_conversion = campaign.spend / campaign.conversions if campaign.conversions > 0 else 0.0
        roas = (campaign.conversions * 50) / campaign.spend if campaign.spend > 0 else 0.0  # Assuming $50 per conversion
        
        performance_data.append(CampaignPerformance(
            campaign_id=campaign.id,
            campaign_name=campaign.name,
            impressions=campaign.impressions,
            clicks=campaign.clicks,
            conversions=campaign.conversions,
            spend=campaign.spend,
            ctr=campaign.ctr,
            conversion_rate=campaign.conversion_rate,
            cost_per_click=cost_per_click,
            cost_per_conversion=cost_per_conversion,
            return_on_ad_spend=roas
        ))
    
    return performance_data


@router.get("/campaigns/{campaign_id}/creatives", response_model=List[AdCreativePerformance])
async def get_creative_analytics(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get performance analytics for ad creatives in a campaign"""
    
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
    
    # Get creative performance
    query = """
    SELECT id, campaign_id, headline, impressions, clicks, conversions, ctr, conversion_rate
    FROM ad_creatives 
    WHERE campaign_id = :campaign_id
    ORDER BY ctr DESC
    """
    
    result = await db.execute(query, {"campaign_id": campaign_id})
    creatives = result.all()
    
    return [
        AdCreativePerformance(
            creative_id=creative.id,
            campaign_id=creative.campaign_id,
            headline=creative.headline,
            impressions=creative.impressions,
            clicks=creative.clicks,
            conversions=creative.conversions,
            ctr=creative.ctr,
            conversion_rate=creative.conversion_rate
        )
        for creative in creatives
    ]


@router.get("/audience", response_model=AudienceInsights)
async def get_audience_insights(
    campaign_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get audience insights and demographics"""
    
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Base query for customer profiles
    base_query = """
    FROM customer_profiles cp
    JOIN ad_deliveries ad ON cp.id = ad.profile_id
    """
    
    conditions = ["ad.delivered_at >= :start_date", "ad.delivered_at <= :end_date"]
    params = {"start_date": start_date, "end_date": end_date}
    
    if campaign_id:
        # Verify campaign ownership first
        campaign_result = await db.execute(
            "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
            {"id": campaign_id, "owner_id": current_user.id}
        )
        if not campaign_result.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        base_query += " JOIN ad_creatives ac ON ad.ad_creative_id = ac.id"
        conditions.append("ac.campaign_id = :campaign_id")
        params["campaign_id"] = campaign_id
    else:
        # For all campaigns of the user
        base_query += " JOIN ad_creatives ac ON ad.ad_creative_id = ac.id JOIN campaigns c ON ac.campaign_id = c.id"
        conditions.append("c.owner_id = :owner_id")
        params["owner_id"] = current_user.id
    
    where_clause = " WHERE " + " AND ".join(conditions)
    
    # Get age group distribution
    age_query = f"""
    SELECT cp.age_range, COUNT(*) as count
    {base_query}
    {where_clause}
    AND cp.age_range IS NOT NULL
    GROUP BY cp.age_range
    """
    
    age_result = await db.execute(age_query, params)
    age_groups = {row.age_range: row.count for row in age_result.all()}
    
    # Get gender distribution
    gender_query = f"""
    SELECT cp.gender, COUNT(*) as count
    {base_query}
    {where_clause}
    AND cp.gender IS NOT NULL
    GROUP BY cp.gender
    """
    
    gender_result = await db.execute(gender_query, params)
    genders = {row.gender: row.count for row in gender_result.all()}
    
    # Get location distribution
    location_query = f"""
    SELECT cp.location, COUNT(*) as count
    {base_query}
    {where_clause}
    AND cp.location IS NOT NULL
    GROUP BY cp.location
    ORDER BY count DESC
    LIMIT 10
    """
    
    location_result = await db.execute(location_query, params)
    locations = {row.location: row.count for row in location_result.all()}
    
    # Get top interests (simplified)
    interests = {"technology": 150, "fashion": 120, "travel": 100, "food": 80, "sports": 75}
    
    # Get engagement by emotion
    emotion_query = f"""
    SELECT cp.emotional_state, AVG(CASE WHEN ad.clicked = true THEN 1 ELSE 0 END) as engagement_rate
    {base_query}
    {where_clause}
    AND cp.emotional_state IS NOT NULL
    GROUP BY cp.emotional_state
    """
    
    emotion_result = await db.execute(emotion_query, params)
    engagement_by_emotion = {row.emotional_state: float(row.engagement_rate) for row in emotion_result.all()}
    
    return AudienceInsights(
        age_groups=age_groups,
        genders=genders,
        locations=locations,
        interests=interests,
        engagement_by_emotion=engagement_by_emotion
    )


@router.get("/timeseries", response_model=List[TimeSeriesData])
async def get_timeseries_data(
    campaign_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    granularity: str = Query("day", regex="^(hour|day|week|month)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get time-series performance data"""
    
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Map granularity to SQL date truncation
    trunc_map = {
        "hour": "DATE_TRUNC('hour', ad.delivered_at)",
        "day": "DATE_TRUNC('day', ad.delivered_at)",
        "week": "DATE_TRUNC('week', ad.delivered_at)",
        "month": "DATE_TRUNC('month', ad.delivered_at)"
    }
    
    date_trunc = trunc_map.get(granularity, "DATE_TRUNC('day', ad.delivered_at)")
    
    base_query = f"""
    SELECT 
        {date_trunc} as time_bucket,
        COUNT(*) as impressions,
        SUM(CASE WHEN ad.clicked = true THEN 1 ELSE 0 END) as clicks,
        SUM(CASE WHEN ad.converted = true THEN 1 ELSE 0 END) as conversions,
        0.0 as spend  -- Placeholder for spend calculation
    FROM ad_deliveries ad
    """
    
    conditions = ["ad.delivered_at >= :start_date", "ad.delivered_at <= :end_date"]
    params = {"start_date": start_date, "end_date": end_date}
    
    if campaign_id:
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
        
        base_query += " JOIN ad_creatives ac ON ad.ad_creative_id = ac.id"
        conditions.append("ac.campaign_id = :campaign_id")
        params["campaign_id"] = campaign_id
    else:
        # For all campaigns of the user
        base_query += " JOIN ad_creatives ac ON ad.ad_creative_id = ac.id JOIN campaigns c ON ac.campaign_id = c.id"
        conditions.append("c.owner_id = :owner_id")
        params["owner_id"] = current_user.id
    
    where_clause = " WHERE " + " AND ".join(conditions)
    query = f"{base_query} {where_clause} GROUP BY time_bucket ORDER BY time_bucket"
    
    result = await db.execute(query, params)
    data = result.all()
    
    return [
        TimeSeriesData(
            timestamp=row.time_bucket,
            impressions=row.impressions,
            clicks=row.clicks,
            conversions=row.conversions,
            spend=row.spend
        )
        for row in data
    ]


@router.get("/system", response_model=SystemPerformance)
async def get_system_performance(
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get system performance metrics"""
    
    # Only allow advertisers or admins to view system metrics
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get system metrics from database
    query = """
    SELECT metric_name, AVG(metric_value) as avg_value
    FROM system_metrics 
    WHERE timestamp >= :start_time
    AND metric_name IN ('api_response_time', 'nlp_processing_time', 'ad_generation_time', 
                        'posts_processed_per_hour', 'system_uptime', 'error_rate')
    GROUP BY metric_name
    """
    
    result = await db.execute(query, {"start_time": start_time})
    metrics = {row.metric_name: row.avg_value for row in result.all()}
    
    return SystemPerformance(
        api_response_time=metrics.get('api_response_time', 0.0),
        nlp_processing_time=metrics.get('nlp_processing_time', 0.0),
        ad_generation_time=metrics.get('ad_generation_time', 0.0),
        posts_processed_per_hour=int(metrics.get('posts_processed_per_hour', 0)),
        system_uptime=metrics.get('system_uptime', 0.0),
        error_rate=metrics.get('error_rate', 0.0)
    )


@router.get("/export")
async def export_analytics(
    campaign_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Export analytics data in various formats"""
    
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get campaign data for export
    query = """
    SELECT c.id, c.name, c.impressions, c.clicks, c.conversions, c.spend, c.ctr, c.conversion_rate,
           c.created_at, c.updated_at
    FROM campaigns c
    WHERE c.owner_id = :owner_id
    AND c.created_at >= :start_date 
    AND c.created_at <= :end_date
    """
    
    params = {
        "owner_id": current_user.id,
        "start_date": start_date,
        "end_date": end_date
    }
    
    if campaign_id:
        query += " AND c.id = :campaign_id"
        params["campaign_id"] = campaign_id
    
    result = await db.execute(query, params)
    campaigns = result.all()
    
    # Convert to export format
    export_data = []
    for campaign in campaigns:
        export_data.append({
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "impressions": campaign.impressions,
            "clicks": campaign.clicks,
            "conversions": campaign.conversions,
            "spend": float(campaign.spend),
            "ctr": float(campaign.ctr),
            "conversion_rate": float(campaign.conversion_rate),
            "created_at": campaign.created_at.isoformat(),
            "updated_at": campaign.updated_at.isoformat()
        })
    
    if format == "json":
        return {"data": export_data, "exported_at": datetime.utcnow().isoformat()}
    elif format == "csv":
        # In a real implementation, you'd generate and return a CSV file
        return {"message": "CSV export functionality would be implemented here", "data": export_data}
    elif format == "xlsx":
        # In a real implementation, you'd generate and return an Excel file
        return {"message": "XLSX export functionality would be implemented here", "data": export_data}
