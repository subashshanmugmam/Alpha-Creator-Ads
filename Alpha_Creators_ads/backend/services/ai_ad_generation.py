"""
AI-powered advertisement generation service.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
import anthropic
from dataclasses import dataclass
import random

from core.config import settings
from .nlp_engine import SentimentAnalyzer, EmotionAnalyzer


@dataclass
class AdRequest:
    """Ad generation request structure"""
    product_name: str
    product_description: str
    target_audience: Dict[str, Any]
    campaign_objective: str
    brand_voice: str
    platform: str
    ad_format: str
    budget_range: str
    keywords: List[str]
    emotions_to_target: List[str]


@dataclass
class GeneratedAd:
    """Generated advertisement structure"""
    headline: str
    description: str
    call_to_action: str
    keywords: List[str]
    target_emotions: List[str]
    estimated_performance: Dict[str, float]
    variations: List[Dict[str, str]]


class AIAdGenerator:
    """Main AI advertisement generation service"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        
    async def generate_ad(self, request: AdRequest) -> GeneratedAd:
        """Generate AI-powered advertisement"""
        
        # Create comprehensive prompt for AI generation
        prompt = self._create_generation_prompt(request)
        
        # Try OpenAI first, fallback to Anthropic
        ad_content = None
        if self.openai_client:
            try:
                ad_content = await self._generate_with_openai(prompt)
            except Exception as e:
                print(f"OpenAI generation failed: {e}")
        
        if not ad_content and self.anthropic_client:
            try:
                ad_content = await self._generate_with_anthropic(prompt)
            except Exception as e:
                print(f"Anthropic generation failed: {e}")
        
        # Fallback to rule-based generation if AI fails
        if not ad_content:
            ad_content = await self._generate_fallback(request)
        
        # Optimize for specific platform
        optimized_content = await self.optimize_for_platform(ad_content, request.platform)
        
        # Generate variations
        variations = await self.generate_variations(optimized_content, count=3)
        
        # Estimate performance metrics
        estimated_performance = await self._estimate_performance(request, optimized_content)
        
        return GeneratedAd(
            headline=optimized_content["headline"],
            description=optimized_content["description"],
            call_to_action=optimized_content["call_to_action"],
            keywords=request.keywords,
            target_emotions=request.emotions_to_target,
            estimated_performance=estimated_performance,
            variations=variations
        )
    
    def _create_generation_prompt(self, request: AdRequest) -> str:
        """Create a comprehensive prompt for AI generation"""
        
        audience_desc = ", ".join([f"{k}: {v}" for k, v in request.target_audience.items()])
        emotions_desc = ", ".join(request.emotions_to_target)
        keywords_desc = ", ".join(request.keywords)
        
        prompt = f"""
        Create a compelling advertisement with the following specifications:

        Product: {request.product_name}
        Description: {request.product_description}
        Target Audience: {audience_desc}
        Campaign Objective: {request.campaign_objective}
        Brand Voice: {request.brand_voice}
        Platform: {request.platform}
        Ad Format: {request.ad_format}
        Budget Range: {request.budget_range}
        Keywords to include: {keywords_desc}
        Emotions to target: {emotions_desc}

        Generate an ad with:
        1. A compelling headline (max 60 characters for most platforms)
        2. A detailed description that tells a story and connects emotionally
        3. A strong call-to-action that drives the desired behavior
        4. Integration of the specified keywords naturally
        5. Tone that matches the brand voice and target emotions

        Return the response in JSON format with keys: headline, description, call_to_action
        """
        
        return prompt
    
    async def _generate_with_openai(self, prompt: str) -> Dict[str, str]:
        """Generate ad using OpenAI GPT"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert advertising copywriter who creates compelling, emotion-driven advertisements."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        # Try to parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            lines = content.strip().split('\n')
            return {
                "headline": lines[0] if lines else "Premium Quality Product",
                "description": lines[1] if len(lines) > 1 else "Discover the difference quality makes.",
                "call_to_action": lines[2] if len(lines) > 2 else "Shop Now"
            }
    
    async def _generate_with_anthropic(self, prompt: str) -> Dict[str, str]:
        """Generate ad using Anthropic Claude"""
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        
        # Try to parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback parsing
            lines = content.strip().split('\n')
            return {
                "headline": lines[0] if lines else "Quality You Can Trust",
                "description": lines[1] if len(lines) > 1 else "Experience excellence like never before.",
                "call_to_action": lines[2] if len(lines) > 2 else "Learn More"
            }
    
    async def _generate_fallback(self, request: AdRequest) -> Dict[str, str]:
        """Fallback rule-based ad generation"""
        
        # Template-based generation
        headlines = [
            f"Discover {request.product_name}",
            f"Transform Your Life with {request.product_name}",
            f"The Future of {request.product_name.split()[-1]} is Here",
            f"Experience Premium {request.product_name}",
            f"Unlock the Power of {request.product_name}"
        ]
        
        descriptions = [
            f"Join thousands who have already discovered the benefits of {request.product_name}. {request.product_description}",
            f"Revolutionary {request.product_name} that changes everything. {request.product_description}",
            f"Premium quality meets innovation. {request.product_description}",
            f"Don't miss out on this game-changing {request.product_name}. {request.product_description}"
        ]
        
        call_to_actions = {
            "awareness": ["Learn More", "Discover Now", "Find Out How"],
            "engagement": ["Join Us", "Get Started", "Try It Free"],
            "conversion": ["Buy Now", "Shop Today", "Order Now"],
            "retention": ["Continue", "Upgrade", "Renew"]
        }
        
        cta_list = call_to_actions.get(request.campaign_objective, ["Get Started"])
        
        return {
            "headline": random.choice(headlines),
            "description": random.choice(descriptions),
            "call_to_action": random.choice(cta_list)
        }
        
    async def generate_variations(self, base_ad: Dict[str, str], count: int = 3) -> List[Dict[str, str]]:
        """Generate multiple variations of an ad"""
        
        variations = []
        
        # Headline variations
        headline_variations = [
            base_ad["headline"],
            base_ad["headline"].replace("Discover", "Experience"),
            base_ad["headline"].replace("Transform", "Revolutionize"),
            f"🔥 {base_ad['headline']}",
            f"New: {base_ad['headline']}"
        ]
        
        # Description variations
        description_variations = [
            base_ad["description"],
            f"Limited time: {base_ad['description']}",
            f"Exclusive offer: {base_ad['description']}",
            base_ad["description"] + " Don't wait - supplies are limited!",
            base_ad["description"] + " Join the revolution today."
        ]
        
        # CTA variations
        cta_variations = [
            base_ad["call_to_action"],
            f"{base_ad['call_to_action']} Today",
            f"{base_ad['call_to_action']} →",
            f"👉 {base_ad['call_to_action']}",
            f"{base_ad['call_to_action']} Now"
        ]
        
        for i in range(count):
            variation = {
                "headline": headline_variations[i % len(headline_variations)],
                "description": description_variations[i % len(description_variations)],
                "call_to_action": cta_variations[i % len(cta_variations)]
            }
            variations.append(variation)
        
        return variations
        
    async def optimize_for_platform(self, ad_content: Dict[str, str], platform: str) -> Dict[str, str]:
        """Optimize ad content for specific platform"""
        
        platform_optimizations = {
            "facebook": {
                "headline_max": 60,
                "description_max": 90,
                "style": "conversational",
                "emojis": True
            },
            "instagram": {
                "headline_max": 50,
                "description_max": 80,
                "style": "visual",
                "emojis": True,
                "hashtags": True
            },
            "twitter": {
                "headline_max": 50,
                "description_max": 120,
                "style": "concise",
                "emojis": True,
                "hashtags": True
            },
            "linkedin": {
                "headline_max": 70,
                "description_max": 150,
                "style": "professional",
                "emojis": False
            },
            "google": {
                "headline_max": 30,
                "description_max": 90,
                "style": "direct",
                "emojis": False
            }
        }
        
        platform_config = platform_optimizations.get(platform.lower(), platform_optimizations["facebook"])
        
        # Optimize headline length
        headline = ad_content["headline"]
        if len(headline) > platform_config["headline_max"]:
            headline = headline[:platform_config["headline_max"]-3] + "..."
        
        # Optimize description length
        description = ad_content["description"]
        if len(description) > platform_config["description_max"]:
            description = description[:platform_config["description_max"]-3] + "..."
        
        # Add platform-specific elements
        if platform_config.get("hashtags") and platform.lower() in ["instagram", "twitter"]:
            if not any(tag in description for tag in ["#", "@"]):
                description += " #premium #quality"
        
        if platform_config.get("emojis") and platform_config["style"] != "professional":
            if not any(char in headline for char in ["🔥", "✨", "💎", "🚀"]):
                headline = f"✨ {headline}"
        
        return {
            "headline": headline,
            "description": description,
            "call_to_action": ad_content["call_to_action"]
        }
    
    async def _estimate_performance(self, request: AdRequest, ad_content: Dict[str, str]) -> Dict[str, float]:
        """Estimate ad performance metrics"""
        
        # Analyze sentiment and emotional appeal
        sentiment_score = await self.sentiment_analyzer.analyze_sentiment(ad_content["description"])
        emotion_scores = await self.emotion_analyzer.analyze_emotions(ad_content["description"])
        
        # Base performance estimates
        base_ctr = 0.02  # 2% baseline CTR
        base_conversion_rate = 0.05  # 5% baseline conversion rate
        
        # Adjust based on sentiment
        sentiment_multiplier = 1.0
        if sentiment_score["sentiment"] == "positive":
            sentiment_multiplier = 1.2
        elif sentiment_score["sentiment"] == "negative":
            sentiment_multiplier = 0.8
        
        # Adjust based on emotions
        emotion_multiplier = 1.0
        target_emotions = set(request.emotions_to_target)
        detected_emotions = set(emotion_scores["emotions"].keys())
        
        emotion_match = len(target_emotions.intersection(detected_emotions)) / len(target_emotions)
        emotion_multiplier = 1.0 + (emotion_match * 0.3)  # Up to 30% boost for emotion alignment
        
        # Platform-specific adjustments
        platform_multipliers = {
            "facebook": 1.0,
            "instagram": 1.1,
            "twitter": 0.9,
            "linkedin": 0.8,
            "google": 1.2
        }
        
        platform_multiplier = platform_multipliers.get(request.platform.lower(), 1.0)
        
        # Budget impact (higher budget = better placement = better performance)
        budget_multiplier = 1.0
        if "high" in request.budget_range.lower():
            budget_multiplier = 1.3
        elif "medium" in request.budget_range.lower():
            budget_multiplier = 1.1
        
        # Calculate final estimates
        estimated_ctr = base_ctr * sentiment_multiplier * emotion_multiplier * platform_multiplier * budget_multiplier
        estimated_conversion_rate = base_conversion_rate * sentiment_multiplier * emotion_multiplier * budget_multiplier
        
        # Ensure realistic ranges
        estimated_ctr = min(max(estimated_ctr, 0.005), 0.15)  # 0.5% to 15%
        estimated_conversion_rate = min(max(estimated_conversion_rate, 0.01), 0.25)  # 1% to 25%
        
        return {
            "estimated_ctr": round(estimated_ctr, 4),
            "estimated_conversion_rate": round(estimated_conversion_rate, 4),
            "sentiment_score": round(sentiment_score["confidence"], 3),
            "emotion_alignment": round(emotion_match, 3),
            "performance_score": round((estimated_ctr * 10 + estimated_conversion_rate * 5), 2)
        }
    
    async def generate_batch_ads(self, requests: List[AdRequest]) -> List[GeneratedAd]:
        """Generate multiple ads in batch"""
        
        tasks = [self.generate_ad(request) for request in requests]
        return await asyncio.gather(*tasks)
    
    async def A_B_test_variations(self, request: AdRequest, variation_count: int = 5) -> List[GeneratedAd]:
        """Generate multiple variations for A/B testing"""
        
        variations = []
        
        # Generate base ad
        base_ad = await self.generate_ad(request)
        variations.append(base_ad)
        
        # Generate additional variations with different approaches
        for i in range(variation_count - 1):
            # Modify the request slightly for each variation
            modified_request = AdRequest(
                product_name=request.product_name,
                product_description=request.product_description,
                target_audience=request.target_audience,
                campaign_objective=request.campaign_objective,
                brand_voice=request.brand_voice,
                platform=request.platform,
                ad_format=request.ad_format,
                budget_range=request.budget_range,
                keywords=request.keywords,
                emotions_to_target=request.emotions_to_target[::-1]  # Reverse emotion order for variation
            )
            
            variation_ad = await self.generate_ad(modified_request)
            variations.append(variation_ad)
        
        return variations
