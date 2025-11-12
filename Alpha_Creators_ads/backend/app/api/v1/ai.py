"""
AI-Powered Ad Generation API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import json
import openai
from bson import ObjectId

from app.database import get_db
from app.cache import CacheManager, CacheKeys
from app.utils.security import get_current_user_id
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY

@router.post("/generate-ad-content")
async def generate_ad_content(
    request_data: dict,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    cache: CacheManager = Depends()
):
    """
    🤖 **Generate AI-Powered Ad Content**
    
    Generate compelling ad content using advanced AI models.
    
    **Features:**
    - Multi-platform optimization
    - Brand-consistent messaging
    - A/B testing variations
    - Industry-specific templates
    - Performance prediction
    
    **Input Parameters:**
    - Product/service description
    - Target audience
    - Campaign objective
    - Brand voice/tone
    - Platform specifications
    """
    
    # Check user API quota
    user_doc = await db.users.find_one(
        {"_id": ObjectId(current_user_id)},
        {"subscription": 1, "apiUsage": 1}
    )
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check quota limits
    subscription_plan = user_doc["subscription"]["plan"]
    api_usage = user_doc["apiUsage"]
    
    quota_limits = {
        "free": settings.AI_GENERATION_QUOTA_FREE,
        "basic": settings.AI_GENERATION_QUOTA_BASIC,
        "professional": settings.AI_GENERATION_QUOTA_PROFESSIONAL,
        "enterprise": settings.AI_GENERATION_QUOTA_ENTERPRISE
    }
    
    if api_usage["apiCallsThisMonth"] >= quota_limits.get(subscription_plan, 10):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI generation quota exceeded for this month"
        )
    
    # Extract generation parameters
    product_description = request_data.get("productDescription", "")
    target_audience = request_data.get("targetAudience", "")
    campaign_objective = request_data.get("campaignObjective", "brand_awareness")
    brand_voice = request_data.get("brandVoice", "professional")
    platform = request_data.get("platform", "facebook")
    ad_format = request_data.get("adFormat", "single_image")
    variations_count = min(request_data.get("variationsCount", 3), 5)
    
    if not product_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product description is required"
        )
    
    try:
        # Generate ad content using OpenAI
        prompt = f"""
        Create {variations_count} high-converting ad variations for the following:
        
        Product/Service: {product_description}
        Target Audience: {target_audience}
        Campaign Objective: {campaign_objective}
        Brand Voice: {brand_voice}
        Platform: {platform}
        Ad Format: {ad_format}
        
        For each variation, provide:
        1. Headline (max 40 characters for {platform})
        2. Primary text (max 125 characters for {platform})
        3. Call-to-action suggestion
        4. Description/caption (max 30 words)
        5. Hashtag suggestions (if applicable for platform)
        6. Performance prediction score (1-10)
        7. Optimization tips
        
        Format the response as JSON with the following structure:
        {{
            "variations": [
                {{
                    "headline": "...",
                    "primaryText": "...",
                    "callToAction": "...",
                    "description": "...",
                    "hashtags": ["...", "..."],
                    "predictionScore": 8.5,
                    "optimizationTips": ["...", "..."]
                }}
            ],
            "insights": {{
                "audienceRecommendations": ["...", "..."],
                "platformSpecificTips": ["...", "..."],
                "budgetSuggestions": "...",
                "timingRecommendations": "..."
            }}
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert digital marketing specialist and copywriter with deep knowledge of advertising platforms and consumer psychology. Generate high-converting ad content that drives engagement and conversions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse AI response
        ai_content = json.loads(response.choices[0].message.content)
        
        # Store generation request in database for analytics
        generation_doc = {
            "userId": ObjectId(current_user_id),
            "requestData": request_data,
            "aiResponse": ai_content,
            "model": "gpt-4",
            "tokensUsed": response.usage.total_tokens,
            "createdAt": datetime.utcnow()
        }
        
        await db.ai_generations.insert_one(generation_doc)
        
        # Update user API usage
        await db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {
                "$inc": {
                    "apiUsage.apiCallsThisMonth": 1,
                    "apiUsage.adsGenerated": variations_count
                },
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        
        # Cache generated content
        cache_key = f"ai_generation:{current_user_id}:{datetime.utcnow().strftime('%Y%m%d')}"
        cached_generations = await cache.get(cache_key) or []
        cached_generations.append(ai_content)
        await cache.set(cache_key, cached_generations, ttl=86400)  # 24 hours
        
        logger.info(f"AI ad content generated for user {current_user_id}: {variations_count} variations")
        
        return {
            "success": True,
            "generatedContent": ai_content,
            "tokensUsed": response.usage.total_tokens,
            "remainingQuota": quota_limits.get(subscription_plan, 10) - (api_usage["apiCallsThisMonth"] + 1),
            "generatedAt": datetime.utcnow().isoformat()
        }
        
    except openai.error.RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI service rate limit exceeded. Please try again later."
        )
    except openai.error.InvalidRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid AI request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"AI generation error for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI content. Please try again."
        )

@router.post("/generate-images")
async def generate_ad_images(
    request_data: dict,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    🎨 **Generate AI-Powered Ad Images**
    
    Generate custom ad images using AI image generation models.
    
    **Features:**
    - DALL-E 3 integration
    - Brand-consistent styling
    - Multiple format support
    - Platform optimization
    - Style variations
    
    **Supported Formats:**
    - Square (1:1) - Instagram, Facebook
    - Landscape (16:9) - YouTube, LinkedIn
    - Portrait (9:16) - Stories, Reels
    - Custom dimensions
    """
    
    # Check user quota
    user_doc = await db.users.find_one(
        {"_id": ObjectId(current_user_id)},
        {"subscription": 1, "apiUsage": 1}
    )
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check image generation limits
    subscription_plan = user_doc["subscription"]["plan"]
    image_limits = {
        "free": 5,
        "basic": 25,
        "professional": 100,
        "enterprise": 500
    }
    
    # Count images generated this month
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    images_generated = await db.ai_generations.count_documents({
        "userId": ObjectId(current_user_id),
        "requestData.type": "image",
        "createdAt": {"$gte": current_month_start}
    })
    
    if images_generated >= image_limits.get(subscription_plan, 5):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Image generation limit exceeded for this month"
        )
    
    # Extract image generation parameters
    prompt = request_data.get("prompt", "")
    style = request_data.get("style", "modern")
    size = request_data.get("size", "1024x1024")
    count = min(request_data.get("count", 1), 4)
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image prompt is required"
        )
    
    try:
        # Generate images using DALL-E
        enhanced_prompt = f"""
        Create a professional advertising image with the following specifications:
        {prompt}
        
        Style: {style}
        Quality: High-resolution, commercial-grade
        Composition: Visually appealing, suitable for advertising
        Colors: Vibrant and attention-grabbing
        Text: No text overlay (will be added separately)
        """
        
        response = openai.Image.create(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=size,
            quality="hd",
            n=count
        )
        
        # Process generated images
        generated_images = []
        for i, image_data in enumerate(response.data):
            image_info = {
                "url": image_data.url,
                "prompt": enhanced_prompt,
                "size": size,
                "style": style,
                "generatedAt": datetime.utcnow().isoformat()
            }
            generated_images.append(image_info)
        
        # Store generation request
        generation_doc = {
            "userId": ObjectId(current_user_id),
            "requestData": {**request_data, "type": "image"},
            "aiResponse": {"images": generated_images},
            "model": "dall-e-3",
            "imagesGenerated": count,
            "createdAt": datetime.utcnow()
        }
        
        await db.ai_generations.insert_one(generation_doc)
        
        logger.info(f"AI images generated for user {current_user_id}: {count} images")
        
        return {
            "success": True,
            "images": generated_images,
            "imagesGenerated": count,
            "remainingQuota": image_limits.get(subscription_plan, 5) - (images_generated + count),
            "generatedAt": datetime.utcnow().isoformat()
        }
        
    except openai.error.RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI image service rate limit exceeded. Please try again later."
        )
    except Exception as e:
        logger.error(f"AI image generation error for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI images. Please try again."
        )

@router.post("/optimize-campaign")
async def optimize_campaign_ai(
    campaign_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    🚀 **AI-Powered Campaign Optimization**
    
    Analyze campaign performance and provide AI-driven optimization recommendations.
    
    **Analysis Areas:**
    - Audience targeting refinement
    - Budget allocation optimization
    - Creative performance insights
    - Bidding strategy recommendations
    - Schedule optimization
    """
    
    # Get campaign data
    campaign_doc = await db.campaigns.find_one({
        "_id": ObjectId(campaign_id),
        "userId": ObjectId(current_user_id)
    })
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get campaign analytics
    analytics_data = campaign_doc.get("analytics", {})
    
    # Get ads performance
    ads_cursor = db.ads.find(
        {"campaignId": ObjectId(campaign_id)},
        {"analytics": 1, "content": 1, "targeting": 1}
    )
    ads_performance = await ads_cursor.to_list(length=None)
    
    try:
        # Create optimization prompt
        optimization_prompt = f"""
        Analyze the following advertising campaign performance and provide detailed optimization recommendations:
        
        Campaign Analytics:
        - Impressions: {analytics_data.get('impressions', 0)}
        - Clicks: {analytics_data.get('clicks', 0)}
        - Conversions: {analytics_data.get('conversions', 0)}
        - CTR: {analytics_data.get('ctr', 0)}%
        - CPC: ${analytics_data.get('cpc', 0)}
        - CPA: ${analytics_data.get('cpa', 0)}
        - Total Spent: ${analytics_data.get('spent', 0)}
        
        Campaign Details:
        - Objective: {campaign_doc.get('objective')}
        - Budget: ${campaign_doc.get('budget', {}).get('amount', 0)}
        - Platforms: {', '.join(campaign_doc.get('platforms', []))}
        - Target Audience: {campaign_doc.get('targeting', {}).get('demographics', {})}
        
        Number of Active Ads: {len(ads_performance)}
        
        Provide optimization recommendations in JSON format:
        {{
            "overallScore": 8.5,
            "recommendations": [
                {{
                    "category": "targeting",
                    "priority": "high",
                    "title": "...",
                    "description": "...",
                    "expectedImpact": "...",
                    "implementation": "..."
                }}
            ],
            "budgetOptimization": {{
                "currentUtilization": "85%",
                "recommendedAdjustment": "+15%",
                "reasoning": "..."
            }},
            "audienceInsights": {{
                "topPerformingSegments": ["...", "..."],
                "underperformingSegments": ["...", "..."],
                "expansionOpportunities": ["...", "..."]
            }},
            "creativeRecommendations": {{
                "topPerformingElements": ["...", "..."],
                "improvementAreas": ["...", "..."],
                "newCreativeIdeas": ["...", "..."]
            }},
            "predictedImprovements": {{
                "ctrIncrease": "12%",
                "cpcReduction": "8%",
                "conversionsIncrease": "25%"
            }}
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert digital marketing analyst specializing in campaign optimization. Provide data-driven recommendations to improve advertising performance."
                },
                {
                    "role": "user",
                    "content": optimization_prompt
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        optimization_result = json.loads(response.choices[0].message.content)
        
        # Store optimization analysis
        optimization_doc = {
            "userId": ObjectId(current_user_id),
            "campaignId": ObjectId(campaign_id),
            "analysisData": {
                "campaignMetrics": analytics_data,
                "adsCount": len(ads_performance)
            },
            "recommendations": optimization_result,
            "model": "gpt-4",
            "createdAt": datetime.utcnow()
        }
        
        await db.campaign_optimizations.insert_one(optimization_doc)
        
        # Update campaign's last optimized timestamp
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "lastOptimized": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Campaign optimization analysis completed for {campaign_id}")
        
        return {
            "success": True,
            "optimization": optimization_result,
            "analyzedAt": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Campaign optimization error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate optimization recommendations"
        )

@router.get("/generation-history")
async def get_generation_history(
    current_user_id: str = Depends(get_current_user_id),
    limit: int = 20,
    offset: int = 0,
    generation_type: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📋 **Get AI Generation History**
    
    Retrieve user's AI generation history and analytics.
    """
    
    query = {"userId": ObjectId(current_user_id)}
    if generation_type:
        query["requestData.type"] = generation_type
    
    # Get total count
    total = await db.ai_generations.count_documents(query)
    
    # Get generations
    generations_cursor = db.ai_generations.find(query).sort("createdAt", -1).skip(offset).limit(limit)
    
    generations = []
    async for gen_doc in generations_cursor:
        generations.append({
            "id": str(gen_doc["_id"]),
            "type": gen_doc["requestData"].get("type", "content"),
            "requestData": gen_doc["requestData"],
            "model": gen_doc.get("model"),
            "tokensUsed": gen_doc.get("tokensUsed"),
            "imagesGenerated": gen_doc.get("imagesGenerated"),
            "createdAt": gen_doc["createdAt"].isoformat()
        })
    
    return {
        "generations": generations,
        "total": total,
        "limit": limit,
        "offset": offset,
        "hasMore": offset + len(generations) < total
    }

@router.get("/quota-usage")
async def get_quota_usage(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    📊 **Get AI Quota Usage**
    
    Retrieve current month's AI service usage and limits.
    """
    
    user_doc = await db.users.find_one(
        {"_id": ObjectId(current_user_id)},
        {"subscription": 1, "apiUsage": 1}
    )
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    subscription_plan = user_doc["subscription"]["plan"]
    api_usage = user_doc["apiUsage"]
    
    # Get quota limits
    content_quota = {
        "free": settings.AI_GENERATION_QUOTA_FREE,
        "basic": settings.AI_GENERATION_QUOTA_BASIC,
        "professional": settings.AI_GENERATION_QUOTA_PROFESSIONAL,
        "enterprise": settings.AI_GENERATION_QUOTA_ENTERPRISE
    }
    
    image_quota = {
        "free": 5,
        "basic": 25,
        "professional": 100,
        "enterprise": 500
    }
    
    # Count current month usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    images_generated = await db.ai_generations.count_documents({
        "userId": ObjectId(current_user_id),
        "requestData.type": "image",
        "createdAt": {"$gte": current_month_start}
    })
    
    return {
        "subscriptionPlan": subscription_plan,
        "contentGeneration": {
            "used": api_usage["apiCallsThisMonth"],
            "limit": content_quota.get(subscription_plan, 10),
            "remaining": content_quota.get(subscription_plan, 10) - api_usage["apiCallsThisMonth"]
        },
        "imageGeneration": {
            "used": images_generated,
            "limit": image_quota.get(subscription_plan, 5),
            "remaining": image_quota.get(subscription_plan, 5) - images_generated
        },
        "totalAdsGenerated": api_usage["adsGenerated"],
        "resetDate": (current_month_start.replace(month=current_month_start.month + 1)).isoformat()
    }