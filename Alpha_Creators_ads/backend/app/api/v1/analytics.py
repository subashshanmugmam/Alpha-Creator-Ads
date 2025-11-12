"""
Analytics and Reporting API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from bson import ObjectId

from app.database import get_db
from app.cache import CacheManager, CacheKeys
from app.utils.security import get_current_user_id

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user_id: str = Depends(get_current_user_id),
    date_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    📊 **Dashboard Analytics Overview**
    
    Get comprehensive analytics overview for user dashboard.
    
    **Metrics Include:**
    - Campaign performance summary
    - Ad performance summary
    - Spend analysis
    - ROI and ROAS metrics
    - Top performing campaigns/ads
    - Trend analysis
    """
    
    # Calculate date range
    now = datetime.utcnow()
    if date_range == "7d":
        start_date = now - timedelta(days=7)
    elif date_range == "30d":
        start_date = now - timedelta(days=30)
    elif date_range == "90d":
        start_date = now - timedelta(days=90)
    else:  # 1y
        start_date = now - timedelta(days=365)
    
    # Check cache first
    cache_key = f"dashboard_analytics:{current_user_id}:{date_range}:{now.strftime('%Y%m%d%H')}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Aggregate campaign analytics
    campaign_pipeline = [
        {
            "$match": {
                "userId": ObjectId(current_user_id),
                "createdAt": {"$gte": start_date, "$lte": now}
            }
        },
        {
            "$group": {
                "_id": None,
                "totalCampaigns": {"$sum": 1},
                "activeCampaigns": {
                    "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                },
                "totalSpent": {"$sum": "$analytics.spent"},
                "totalImpressions": {"$sum": "$analytics.impressions"},
                "totalClicks": {"$sum": "$analytics.clicks"},
                "totalConversions": {"$sum": "$analytics.conversions"},
                "campaignsByObjective": {
                    "$push": {
                        "objective": "$objective",
                        "spent": "$analytics.spent",
                        "conversions": "$analytics.conversions"
                    }
                }
            }
        }
    ]
    
    campaign_analytics = await db.campaigns.aggregate(campaign_pipeline).to_list(1)
    campaign_data = campaign_analytics[0] if campaign_analytics else {
        "totalCampaigns": 0,
        "activeCampaigns": 0,
        "totalSpent": 0,
        "totalImpressions": 0,
        "totalClicks": 0,
        "totalConversions": 0,
        "campaignsByObjective": []
    }
    
    # Aggregate ad analytics
    ad_pipeline = [
        {
            "$match": {
                "userId": ObjectId(current_user_id),
                "createdAt": {"$gte": start_date, "$lte": now}
            }
        },
        {
            "$group": {
                "_id": None,
                "totalAds": {"$sum": 1},
                "activeAds": {
                    "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                },
                "adsByFormat": {
                    "$push": {
                        "format": "$format",
                        "ctr": "$analytics.ctr",
                        "spent": "$analytics.spent"
                    }
                }
            }
        }
    ]
    
    ad_analytics = await db.ads.aggregate(ad_pipeline).to_list(1)
    ad_data = ad_analytics[0] if ad_analytics else {
        "totalAds": 0,
        "activeAds": 0,
        "adsByFormat": []
    }
    
    # Calculate derived metrics
    total_impressions = campaign_data["totalImpressions"]
    total_clicks = campaign_data["totalClicks"]
    total_conversions = campaign_data["totalConversions"]
    total_spent = campaign_data["totalSpent"]
    
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    overall_cpc = (total_spent / total_clicks) if total_clicks > 0 else 0
    overall_cpa = (total_spent / total_conversions) if total_conversions > 0 else 0
    
    # Get top performing campaigns
    top_campaigns_cursor = db.campaigns.find(
        {
            "userId": ObjectId(current_user_id),
            "createdAt": {"$gte": start_date, "$lte": now}
        },
        {"name": 1, "analytics": 1, "status": 1}
    ).sort("analytics.conversions", -1).limit(5)
    
    top_campaigns = []
    async for campaign in top_campaigns_cursor:
        top_campaigns.append({
            "id": str(campaign["_id"]),
            "name": campaign["name"],
            "status": campaign["status"],
            "conversions": campaign["analytics"]["conversions"],
            "spent": campaign["analytics"]["spent"],
            "roas": (campaign["analytics"]["conversions"] * 50 / campaign["analytics"]["spent"]) if campaign["analytics"]["spent"] > 0 else 0  # Assuming $50 avg order value
        })
    
    # Get top performing ads
    top_ads_cursor = db.ads.find(
        {
            "userId": ObjectId(current_user_id),
            "createdAt": {"$gte": start_date, "$lte": now}
        },
        {"title": 1, "analytics": 1, "status": 1, "format": 1}
    ).sort("analytics.ctr", -1).limit(5)
    
    top_ads = []
    async for ad in top_ads_cursor:
        top_ads.append({
            "id": str(ad["_id"]),
            "title": ad["title"],
            "format": ad["format"],
            "status": ad["status"],
            "ctr": ad["analytics"]["ctr"],
            "conversions": ad["analytics"]["conversions"],
            "spent": ad["analytics"]["spent"]
        })
    
    # Get daily performance trends
    daily_trends_pipeline = [
        {
            "$match": {
                "userId": ObjectId(current_user_id),
                "timestamp": {"$gte": start_date, "$lte": now}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$timestamp"
                    }
                },
                "impressions": {"$sum": "$impressions"},
                "clicks": {"$sum": "$clicks"},
                "conversions": {"$sum": "$conversions"},
                "spent": {"$sum": "$spent"}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    
    daily_trends = await db.analytics.aggregate(daily_trends_pipeline).to_list(None)
    
    # Prepare response
    dashboard_data = {
        "dateRange": {
            "startDate": start_date.isoformat(),
            "endDate": now.isoformat(),
            "period": date_range
        },
        "overview": {
            "totalCampaigns": campaign_data["totalCampaigns"],
            "activeCampaigns": campaign_data["activeCampaigns"],
            "totalAds": ad_data["totalAds"],
            "activeAds": ad_data["activeAds"],
            "totalSpent": round(total_spent, 2),
            "totalImpressions": total_impressions,
            "totalClicks": total_clicks,
            "totalConversions": total_conversions
        },
        "performance": {
            "overallCtr": round(overall_ctr, 2),
            "overallCpc": round(overall_cpc, 2),
            "overallCpa": round(overall_cpa, 2) if total_conversions > 0 else None,
            "estimatedRoas": round((total_conversions * 50 / total_spent), 2) if total_spent > 0 else 0
        },
        "topCampaigns": top_campaigns,
        "topAds": top_ads,
        "dailyTrends": daily_trends,
        "generatedAt": now.isoformat()
    }
    
    # Cache for 1 hour
    await cache.set(cache_key, dashboard_data, ttl=3600)
    
    return dashboard_data

@router.get("/performance-comparison")
async def get_performance_comparison(
    current_user_id: str = Depends(get_current_user_id),
    period_1: str = Query("30d", regex="^(7d|30d|90d)$"),
    period_2: str = Query("60d", regex="^(7d|30d|90d)$"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📈 **Performance Comparison**
    
    Compare performance metrics between two time periods.
    """
    
    now = datetime.utcnow()
    
    # Calculate date ranges
    def get_date_range(period: str):
        days = int(period[:-1])
        return now - timedelta(days=days)
    
    period_1_start = get_date_range(period_1)
    period_2_start = get_date_range(period_2)
    
    # Get metrics for both periods
    async def get_period_metrics(start_date: datetime):
        pipeline = [
            {
                "$match": {
                    "userId": ObjectId(current_user_id),
                    "timestamp": {"$gte": start_date, "$lte": now}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "impressions": {"$sum": "$impressions"},
                    "clicks": {"$sum": "$clicks"},
                    "conversions": {"$sum": "$conversions"},
                    "spent": {"$sum": "$spent"}
                }
            }
        ]
        
        result = await db.analytics.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "spent": 0
        }
    
    period_1_metrics = await get_period_metrics(period_1_start)
    period_2_metrics = await get_period_metrics(period_2_start)
    
    # Calculate percentage changes
    def calculate_change(current: float, previous: float) -> Dict[str, Any]:
        if previous == 0:
            return {"change": 0, "percentage": 0, "trend": "stable"}
        
        change = current - previous
        percentage = (change / previous) * 100
        trend = "up" if percentage > 0 else "down" if percentage < 0 else "stable"
        
        return {
            "change": round(change, 2),
            "percentage": round(percentage, 2),
            "trend": trend
        }
    
    return {
        "comparison": {
            "period1": {
                "label": f"Last {period_1}",
                "startDate": period_1_start.isoformat(),
                "metrics": period_1_metrics
            },
            "period2": {
                "label": f"Previous {period_2}",
                "startDate": period_2_start.isoformat(),
                "metrics": period_2_metrics
            }
        },
        "changes": {
            "impressions": calculate_change(period_1_metrics["impressions"], period_2_metrics["impressions"]),
            "clicks": calculate_change(period_1_metrics["clicks"], period_2_metrics["clicks"]),
            "conversions": calculate_change(period_1_metrics["conversions"], period_2_metrics["conversions"]),
            "spent": calculate_change(period_1_metrics["spent"], period_2_metrics["spent"])
        }
    }

@router.get("/audience-insights")
async def get_audience_insights(
    current_user_id: str = Depends(get_current_user_id),
    campaign_id: Optional[str] = Query(None),
    date_range: str = Query("30d", regex="^(7d|30d|90d)$"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    👥 **Audience Insights**
    
    Get detailed audience performance analytics.
    
    **Insights Include:**
    - Demographics breakdown
    - Geographic performance
    - Device/platform analysis
    - Interest and behavior data
    - Time-based engagement patterns
    """
    
    # Calculate date range
    now = datetime.utcnow()
    days = int(date_range[:-1])
    start_date = now - timedelta(days=days)
    
    # Build query
    query = {
        "userId": ObjectId(current_user_id),
        "timestamp": {"$gte": start_date, "$lte": now}
    }
    
    if campaign_id:
        query["campaignId"] = ObjectId(campaign_id)
    
    # Demographics breakdown
    demographics_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": {
                    "ageRange": "$audience.ageRange",
                    "gender": "$audience.gender"
                },
                "impressions": {"$sum": "$impressions"},
                "clicks": {"$sum": "$clicks"},
                "conversions": {"$sum": "$conversions"},
                "spent": {"$sum": "$spent"}
            }
        },
        {
            "$addFields": {
                "ctr": {
                    "$cond": [
                        {"$gt": ["$impressions", 0]},
                        {"$multiply": [{"$divide": ["$clicks", "$impressions"]}, 100]},
                        0
                    ]
                },
                "cpc": {
                    "$cond": [
                        {"$gt": ["$clicks", 0]},
                        {"$divide": ["$spent", "$clicks"]},
                        0
                    ]
                }
            }
        }
    ]
    
    demographics = await db.analytics.aggregate(demographics_pipeline).to_list(None)
    
    # Geographic performance
    geographic_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": {
                    "country": "$audience.location.country",
                    "region": "$audience.location.region"
                },
                "impressions": {"$sum": "$impressions"},
                "clicks": {"$sum": "$clicks"},
                "conversions": {"$sum": "$conversions"},
                "spent": {"$sum": "$spent"}
            }
        },
        {"$sort": {"conversions": -1}},
        {"$limit": 20}
    ]
    
    geographic = await db.analytics.aggregate(geographic_pipeline).to_list(None)
    
    # Device/Platform breakdown
    device_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": {
                    "device": "$audience.device",
                    "platform": "$platform"
                },
                "impressions": {"$sum": "$impressions"},
                "clicks": {"$sum": "$clicks"},
                "conversions": {"$sum": "$conversions"},
                "spent": {"$sum": "$spent"}
            }
        }
    ]
    
    devices = await db.analytics.aggregate(device_pipeline).to_list(None)
    
    # Time-based engagement
    hourly_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": {"$hour": "$timestamp"},
                "impressions": {"$sum": "$impressions"},
                "clicks": {"$sum": "$clicks"},
                "ctr": {
                    "$avg": {
                        "$cond": [
                            {"$gt": ["$impressions", 0]},
                            {"$multiply": [{"$divide": ["$clicks", "$impressions"]}, 100]},
                            0
                        ]
                    }
                }
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    hourly_engagement = await db.analytics.aggregate(hourly_pipeline).to_list(None)
    
    return {
        "dateRange": {
            "startDate": start_date.isoformat(),
            "endDate": now.isoformat(),
            "period": date_range
        },
        "demographics": demographics,
        "geographic": geographic,
        "devices": devices,
        "hourlyEngagement": hourly_engagement,
        "campaignId": campaign_id,
        "generatedAt": now.isoformat()
    }

@router.get("/conversion-funnel")
async def get_conversion_funnel(
    current_user_id: str = Depends(get_current_user_id),
    campaign_id: Optional[str] = Query(None),
    date_range: str = Query("30d", regex="^(7d|30d|90d)$"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    🎯 **Conversion Funnel Analysis**
    
    Analyze the conversion funnel and identify drop-off points.
    
    **Funnel Stages:**
    1. Impressions → Clicks
    2. Clicks → Landing Page Views
    3. Landing Page Views → Conversions
    4. Conversions → Revenue
    """
    
    # Calculate date range
    now = datetime.utcnow()
    days = int(date_range[:-1])
    start_date = now - timedelta(days=days)
    
    # Build query
    query = {
        "userId": ObjectId(current_user_id),
        "timestamp": {"$gte": start_date, "$lte": now}
    }
    
    if campaign_id:
        query["campaignId"] = ObjectId(campaign_id)
    
    # Funnel analysis pipeline
    funnel_pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": None,
                "totalImpressions": {"$sum": "$impressions"},
                "totalClicks": {"$sum": "$clicks"},
                "totalLandingPageViews": {"$sum": "$landingPageViews"},
                "totalConversions": {"$sum": "$conversions"},
                "totalRevenue": {"$sum": "$revenue"}
            }
        },
        {
            "$addFields": {
                "clickThroughRate": {
                    "$cond": [
                        {"$gt": ["$totalImpressions", 0]},
                        {"$multiply": [{"$divide": ["$totalClicks", "$totalImpressions"]}, 100]},
                        0
                    ]
                },
                "landingPageConversionRate": {
                    "$cond": [
                        {"$gt": ["$totalClicks", 0]},
                        {"$multiply": [{"$divide": ["$totalLandingPageViews", "$totalClicks"]}, 100]},
                        0
                    ]
                },
                "conversionRate": {
                    "$cond": [
                        {"$gt": ["$totalLandingPageViews", 0]},
                        {"$multiply": [{"$divide": ["$totalConversions", "$totalLandingPageViews"]}, 100]},
                        0
                    ]
                },
                "averageOrderValue": {
                    "$cond": [
                        {"$gt": ["$totalConversions", 0]},
                        {"$divide": ["$totalRevenue", "$totalConversions"]},
                        0
                    ]
                }
            }
        }
    ]
    
    funnel_result = await db.analytics.aggregate(funnel_pipeline).to_list(1)
    funnel_data = funnel_result[0] if funnel_result else {
        "totalImpressions": 0,
        "totalClicks": 0,
        "totalLandingPageViews": 0,
        "totalConversions": 0,
        "totalRevenue": 0,
        "clickThroughRate": 0,
        "landingPageConversionRate": 0,
        "conversionRate": 0,
        "averageOrderValue": 0
    }
    
    # Calculate drop-off rates
    impressions = funnel_data["totalImpressions"]
    clicks = funnel_data["totalClicks"]
    landing_views = funnel_data["totalLandingPageViews"]
    conversions = funnel_data["totalConversions"]
    
    funnel_stages = [
        {
            "stage": "Impressions",
            "count": impressions,
            "percentage": 100,
            "dropOffRate": 0
        },
        {
            "stage": "Clicks",
            "count": clicks,
            "percentage": (clicks / impressions * 100) if impressions > 0 else 0,
            "dropOffRate": ((impressions - clicks) / impressions * 100) if impressions > 0 else 0
        },
        {
            "stage": "Landing Page Views",
            "count": landing_views,
            "percentage": (landing_views / impressions * 100) if impressions > 0 else 0,
            "dropOffRate": ((clicks - landing_views) / clicks * 100) if clicks > 0 else 0
        },
        {
            "stage": "Conversions",
            "count": conversions,
            "percentage": (conversions / impressions * 100) if impressions > 0 else 0,
            "dropOffRate": ((landing_views - conversions) / landing_views * 100) if landing_views > 0 else 0
        }
    ]
    
    return {
        "dateRange": {
            "startDate": start_date.isoformat(),
            "endDate": now.isoformat(),
            "period": date_range
        },
        "campaignId": campaign_id,
        "funnel": funnel_stages,
        "metrics": {
            "clickThroughRate": round(funnel_data["clickThroughRate"], 2),
            "landingPageConversionRate": round(funnel_data["landingPageConversionRate"], 2),
            "overallConversionRate": round(funnel_data["conversionRate"], 2),
            "averageOrderValue": round(funnel_data["averageOrderValue"], 2),
            "totalRevenue": round(funnel_data["totalRevenue"], 2)
        },
        "generatedAt": now.isoformat()
    }

@router.get("/export-report")
async def export_analytics_report(
    current_user_id: str = Depends(get_current_user_id),
    report_type: str = Query("campaign", regex="^(campaign|ad|audience|funnel)$"),
    date_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    format: str = Query("json", regex="^(json|csv)$"),
    campaign_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📄 **Export Analytics Report**
    
    Export comprehensive analytics report in various formats.
    
    **Report Types:**
    - Campaign performance
    - Ad performance
    - Audience insights
    - Conversion funnel
    
    **Export Formats:**
    - JSON
    - CSV
    """
    
    # Calculate date range
    now = datetime.utcnow()
    if date_range == "7d":
        start_date = now - timedelta(days=7)
    elif date_range == "30d":
        start_date = now - timedelta(days=30)
    elif date_range == "90d":
        start_date = now - timedelta(days=90)
    else:  # 1y
        start_date = now - timedelta(days=365)
    
    # Build base query
    query = {
        "userId": ObjectId(current_user_id),
        "createdAt": {"$gte": start_date, "$lte": now}
    }
    
    if campaign_id:
        query["campaignId"] = ObjectId(campaign_id)
    
    # Generate report based on type
    if report_type == "campaign":
        cursor = db.campaigns.find(query)
        report_data = []
        async for doc in cursor:
            analytics = doc.get("analytics", {})
            report_data.append({
                "campaignId": str(doc["_id"]),
                "name": doc["name"],
                "objective": doc["objective"],
                "status": doc["status"],
                "impressions": analytics.get("impressions", 0),
                "clicks": analytics.get("clicks", 0),
                "conversions": analytics.get("conversions", 0),
                "spent": analytics.get("spent", 0),
                "ctr": analytics.get("ctr", 0),
                "cpc": analytics.get("cpc", 0),
                "cpa": analytics.get("cpa", 0),
                "createdAt": doc["createdAt"].isoformat()
            })
    
    elif report_type == "ad":
        cursor = db.ads.find(query)
        report_data = []
        async for doc in cursor:
            analytics = doc.get("analytics", {})
            report_data.append({
                "adId": str(doc["_id"]),
                "campaignId": str(doc["campaignId"]),
                "title": doc["title"],
                "type": doc["type"],
                "format": doc["format"],
                "status": doc["status"],
                "impressions": analytics.get("impressions", 0),
                "clicks": analytics.get("clicks", 0),
                "conversions": analytics.get("conversions", 0),
                "spent": analytics.get("spent", 0),
                "ctr": analytics.get("ctr", 0),
                "createdAt": doc["createdAt"].isoformat()
            })
    
    # Return report data
    return {
        "reportType": report_type,
        "dateRange": {
            "startDate": start_date.isoformat(),
            "endDate": now.isoformat(),
            "period": date_range
        },
        "format": format,
        "data": report_data,
        "totalRecords": len(report_data),
        "generatedAt": now.isoformat()
    }