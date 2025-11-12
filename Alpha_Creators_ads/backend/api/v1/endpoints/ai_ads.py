"""
AI advertisement generation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from core.database import get_db_session
from models import User, Campaign, AdCreative
from services.authentication import get_current_user
from services.ai_ad_generation import AIAdGenerator, AdRequest, GeneratedAd

router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class AdGenerationRequest(BaseModel):
    campaign_id: Optional[str] = None
    product_name: str
    product_description: str
    target_audience: Dict[str, Any]
    campaign_objective: str = "engagement"
    brand_voice: str = "professional"
    platform: str = "facebook"
    ad_format: str = "single_image"
    budget_range: str = "medium"
    keywords: List[str] = []
    emotions_to_target: List[str] = ["joy", "excitement"]

class BatchAdGenerationRequest(BaseModel):
    requests: List[AdGenerationRequest]
    save_to_campaigns: bool = False

class AdGenerationResponse(BaseModel):
    id: str
    headline: str
    description: str
    call_to_action: str
    keywords: List[str]
    target_emotions: List[str]
    estimated_performance: Dict[str, float]
    variations: List[Dict[str, str]]
    generated_at: datetime

class ABTestRequest(BaseModel):
    campaign_id: Optional[str] = None
    product_name: str
    product_description: str
    target_audience: Dict[str, Any]
    campaign_objective: str = "engagement"
    brand_voice: str = "professional"
    platform: str = "facebook"
    ad_format: str = "single_image"
    budget_range: str = "medium"
    keywords: List[str] = []
    emotions_to_target: List[str] = ["joy", "excitement"]
    variation_count: int = 5

class OptimizationRequest(BaseModel):
    ad_id: str
    performance_data: Dict[str, float]
    optimization_goal: str = "ctr"

# Initialize AI ad generator
ai_generator = AIAdGenerator()


@router.post("/generate", response_model=AdGenerationResponse)
async def generate_ad(
    request: AdGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate a single AI-powered advertisement"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can generate ads"
        )
    
    # Validate campaign if provided
    if request.campaign_id:
        campaign_result = await db.execute(
            "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
            {"id": request.campaign_id, "owner_id": current_user.id}
        )
        if not campaign_result.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
    
    try:
        # Create ad request for the AI generator
        ad_request = AdRequest(
            product_name=request.product_name,
            product_description=request.product_description,
            target_audience=request.target_audience,
            campaign_objective=request.campaign_objective,
            brand_voice=request.brand_voice,
            platform=request.platform,
            ad_format=request.ad_format,
            budget_range=request.budget_range,
            keywords=request.keywords,
            emotions_to_target=request.emotions_to_target
        )
        
        # Generate the ad
        generated_ad = await ai_generator.generate_ad(ad_request)
        
        # Save to database if campaign_id is provided
        if request.campaign_id:
            creative_id = str(uuid.uuid4())
            
            await db.execute("""
                INSERT INTO ad_creatives (
                    id, campaign_id, headline, description, call_to_action,
                    keywords, target_emotions, estimated_performance,
                    variations, created_at, updated_at
                ) VALUES (
                    :id, :campaign_id, :headline, :description, :call_to_action,
                    :keywords, :target_emotions, :estimated_performance,
                    :variations, :created_at, :updated_at
                )
            """, {
                "id": creative_id,
                "campaign_id": request.campaign_id,
                "headline": generated_ad.headline,
                "description": generated_ad.description,
                "call_to_action": generated_ad.call_to_action,
                "keywords": ",".join(generated_ad.keywords),
                "target_emotions": ",".join(generated_ad.target_emotions),
                "estimated_performance": str(generated_ad.estimated_performance),
                "variations": str(generated_ad.variations),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            await db.commit()
        
        return AdGenerationResponse(
            id=str(uuid.uuid4()),
            headline=generated_ad.headline,
            description=generated_ad.description,
            call_to_action=generated_ad.call_to_action,
            keywords=generated_ad.keywords,
            target_emotions=generated_ad.target_emotions,
            estimated_performance=generated_ad.estimated_performance,
            variations=generated_ad.variations,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ad generation failed: {str(e)}"
        )


@router.post("/batch-generate", response_model=List[AdGenerationResponse])
async def batch_generate_ads(
    request: BatchAdGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate multiple advertisements in batch"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can generate ads"
        )
    
    if len(request.requests) > 50:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Maximum 50 ads allowed per batch"
        )
    
    try:
        # Convert to AI generator requests
        ad_requests = []
        for req in request.requests:
            ad_request = AdRequest(
                product_name=req.product_name,
                product_description=req.product_description,
                target_audience=req.target_audience,
                campaign_objective=req.campaign_objective,
                brand_voice=req.brand_voice,
                platform=req.platform,
                ad_format=req.ad_format,
                budget_range=req.budget_range,
                keywords=req.keywords,
                emotions_to_target=req.emotions_to_target
            )
            ad_requests.append(ad_request)
        
        # Generate ads in batch
        generated_ads = await ai_generator.generate_batch_ads(ad_requests)
        
        # Convert to response format
        responses = []
        for i, generated_ad in enumerate(generated_ads):
            response = AdGenerationResponse(
                id=str(uuid.uuid4()),
                headline=generated_ad.headline,
                description=generated_ad.description,
                call_to_action=generated_ad.call_to_action,
                keywords=generated_ad.keywords,
                target_emotions=generated_ad.target_emotions,
                estimated_performance=generated_ad.estimated_performance,
                variations=generated_ad.variations,
                generated_at=datetime.utcnow()
            )
            responses.append(response)
            
            # Save to database if requested
            if request.save_to_campaigns and request.requests[i].campaign_id:
                background_tasks.add_task(
                    save_ad_to_campaign,
                    db, request.requests[i].campaign_id, generated_ad
                )
        
        return responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch ad generation failed: {str(e)}"
        )


@router.post("/ab-test", response_model=List[AdGenerationResponse])
async def generate_ab_test_variations(
    request: ABTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate multiple ad variations for A/B testing"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can generate ads"
        )
    
    if request.variation_count > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 variations allowed"
        )
    
    # Validate campaign if provided
    if request.campaign_id:
        campaign_result = await db.execute(
            "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
            {"id": request.campaign_id, "owner_id": current_user.id}
        )
        if not campaign_result.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
    
    try:
        # Create ad request for the AI generator
        ad_request = AdRequest(
            product_name=request.product_name,
            product_description=request.product_description,
            target_audience=request.target_audience,
            campaign_objective=request.campaign_objective,
            brand_voice=request.brand_voice,
            platform=request.platform,
            ad_format=request.ad_format,
            budget_range=request.budget_range,
            keywords=request.keywords,
            emotions_to_target=request.emotions_to_target
        )
        
        # Generate A/B test variations
        generated_ads = await ai_generator.A_B_test_variations(ad_request, request.variation_count)
        
        # Convert to response format
        responses = []
        for generated_ad in generated_ads:
            response = AdGenerationResponse(
                id=str(uuid.uuid4()),
                headline=generated_ad.headline,
                description=generated_ad.description,
                call_to_action=generated_ad.call_to_action,
                keywords=generated_ad.keywords,
                target_emotions=generated_ad.target_emotions,
                estimated_performance=generated_ad.estimated_performance,
                variations=generated_ad.variations,
                generated_at=datetime.utcnow()
            )
            responses.append(response)
        
        return responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A/B test generation failed: {str(e)}"
        )


@router.post("/optimize")
async def optimize_ad_performance(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Optimize an existing ad based on performance data"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can optimize ads"
        )
    
    # Get the existing ad
    ad_result = await db.execute("""
        SELECT ac.* FROM ad_creatives ac
        JOIN campaigns c ON ac.campaign_id = c.id
        WHERE ac.id = :ad_id AND c.owner_id = :owner_id
    """, {"ad_id": request.ad_id, "owner_id": current_user.id})
    
    ad = ad_result.first()
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    # Analyze performance and suggest optimizations
    performance_analysis = {
        "current_performance": request.performance_data,
        "optimization_suggestions": [],
        "estimated_improvement": {}
    }
    
    # Get performance data
    ctr = request.performance_data.get("ctr", 0)
    conversion_rate = request.performance_data.get("conversion_rate", 0)
    
    # Provide optimization suggestions based on performance
    if ctr < 0.02:  # Low CTR
        performance_analysis["optimization_suggestions"].extend([
            "Consider using more emotional language in the headline",
            "Add urgency or scarcity elements",
            "Test different call-to-action phrases",
            "Include numbers or statistics in the headline"
        ])
    
    if conversion_rate < 0.05:  # Low conversion rate
        performance_analysis["optimization_suggestions"].extend([
            "Strengthen the value proposition in the description",
            "Add social proof or testimonials",
            "Simplify the call-to-action",
            "Test different landing page alignment"
        ])
    
    # Estimate potential improvements
    performance_analysis["estimated_improvement"] = {
        "ctr_improvement": f"+{15 if ctr < 0.02 else 5}%",
        "conversion_improvement": f"+{20 if conversion_rate < 0.05 else 8}%",
        "confidence_level": "medium"
    }
    
    return performance_analysis


@router.get("/templates")
async def get_ad_templates(
    platform: str = "facebook",
    industry: Optional[str] = None,
    objective: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get pre-built ad templates"""
    
    # Define templates by platform and industry
    templates = {
        "facebook": {
            "ecommerce": [
                {
                    "name": "Product Showcase",
                    "headline": "Discover {product_name}",
                    "description": "Transform your {category} experience with {product_name}. Join thousands of satisfied customers.",
                    "call_to_action": "Shop Now",
                    "emotions": ["excitement", "desire"],
                    "keywords": ["quality", "premium", "exclusive"]
                },
                {
                    "name": "Limited Offer",
                    "headline": "Limited Time: {discount}% Off {product_name}",
                    "description": "Don't miss out! Get {product_name} at an unbeatable price. Offer expires soon.",
                    "call_to_action": "Claim Deal",
                    "emotions": ["urgency", "excitement"],
                    "keywords": ["limited", "deal", "exclusive"]
                }
            ],
            "technology": [
                {
                    "name": "Innovation Focus",
                    "headline": "The Future of {category} is Here",
                    "description": "Experience cutting-edge {product_name} that revolutionizes how you work.",
                    "call_to_action": "Learn More",
                    "emotions": ["curiosity", "excitement"],
                    "keywords": ["innovation", "future", "revolutionary"]
                }
            ]
        },
        "instagram": {
            "lifestyle": [
                {
                    "name": "Visual Story",
                    "headline": "✨ Your {category} Journey Starts Here",
                    "description": "Transform your lifestyle with {product_name}. See the difference. #lifestyle #premium",
                    "call_to_action": "Discover",
                    "emotions": ["aspiration", "joy"],
                    "keywords": ["lifestyle", "transform", "premium"]
                }
            ]
        }
    }
    
    platform_templates = templates.get(platform, {})
    
    if industry:
        industry_templates = platform_templates.get(industry, [])
        return {"templates": industry_templates, "platform": platform, "industry": industry}
    
    # Return all templates for the platform
    all_templates = []
    for industry_name, industry_templates in platform_templates.items():
        for template in industry_templates:
            template["industry"] = industry_name
            all_templates.append(template)
    
    return {"templates": all_templates, "platform": platform}


async def save_ad_to_campaign(db: AsyncSession, campaign_id: str, generated_ad: GeneratedAd):
    """Background task to save generated ad to campaign"""
    
    creative_id = str(uuid.uuid4())
    
    await db.execute("""
        INSERT INTO ad_creatives (
            id, campaign_id, headline, description, call_to_action,
            keywords, target_emotions, estimated_performance,
            variations, created_at, updated_at
        ) VALUES (
            :id, :campaign_id, :headline, :description, :call_to_action,
            :keywords, :target_emotions, :estimated_performance,
            :variations, :created_at, :updated_at
        )
    """, {
        "id": creative_id,
        "campaign_id": campaign_id,
        "headline": generated_ad.headline,
        "description": generated_ad.description,
        "call_to_action": generated_ad.call_to_action,
        "keywords": ",".join(generated_ad.keywords),
        "target_emotions": ",".join(generated_ad.target_emotions),
        "estimated_performance": str(generated_ad.estimated_performance),
        "variations": str(generated_ad.variations),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    await db.commit()
