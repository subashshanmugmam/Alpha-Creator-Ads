"""
NLP and sentiment analysis endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from core.database import get_db_session
from models import User, SocialMediaPost
from services.authentication import get_current_user
from services.nlp_engine import SentimentAnalyzer, EmotionAnalyzer, EntityExtractor

router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class SentimentRequest(BaseModel):
    text: str
    analyze_emotions: bool = True
    extract_entities: bool = True

class SentimentResult(BaseModel):
    sentiment: str
    confidence: float
    polarity: float
    subjectivity: float

class EmotionResult(BaseModel):
    emotions: Dict[str, float]
    dominant_emotion: str
    emotion_intensity: float

class EntityResult(BaseModel):
    entities: List[Dict[str, Any]]
    persons: List[str]
    organizations: List[str]
    locations: List[str]
    products: List[str]

class NLPAnalysisResult(BaseModel):
    text: str
    sentiment: SentimentResult
    emotions: Optional[EmotionResult] = None
    entities: Optional[EntityResult] = None
    keywords: List[str]
    text_length: int
    word_count: int
    analyzed_at: datetime

class BatchAnalysisRequest(BaseModel):
    texts: List[str]
    analyze_emotions: bool = True
    extract_entities: bool = True

class BatchAnalysisResult(BaseModel):
    results: List[NLPAnalysisResult]
    total_processed: int
    processing_time: float

class TrendingTopics(BaseModel):
    topics: List[Dict[str, Any]]
    sentiment_distribution: Dict[str, int]
    emotion_distribution: Dict[str, int]
    time_period: str

class ContentRecommendation(BaseModel):
    recommended_emotions: List[str]
    suggested_keywords: List[str]
    optimal_sentiment: str
    content_suggestions: List[str]
    target_audience_emotions: Dict[str, float]


# Initialize NLP services
sentiment_analyzer = SentimentAnalyzer()
emotion_analyzer = EmotionAnalyzer()
entity_extractor = EntityExtractor()


@router.post("/analyze", response_model=NLPAnalysisResult)
async def analyze_text(
    request: SentimentRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze text for sentiment, emotions, and entities"""
    
    start_time = datetime.utcnow()
    
    try:
        # Perform sentiment analysis
        sentiment_result = await sentiment_analyzer.analyze_sentiment(request.text)
        
        sentiment = SentimentResult(
            sentiment=sentiment_result["sentiment"],
            confidence=sentiment_result["confidence"],
            polarity=sentiment_result["polarity"],
            subjectivity=sentiment_result["subjectivity"]
        )
        
        # Perform emotion analysis if requested
        emotions = None
        if request.analyze_emotions:
            emotion_result = await emotion_analyzer.analyze_emotions(request.text)
            emotions = EmotionResult(
                emotions=emotion_result["emotions"],
                dominant_emotion=emotion_result["dominant_emotion"],
                emotion_intensity=emotion_result["emotion_intensity"]
            )
        
        # Extract entities if requested
        entities = None
        if request.extract_entities:
            entity_result = await entity_extractor.extract_entities(request.text)
            entities = EntityResult(
                entities=entity_result["entities"],
                persons=entity_result["persons"],
                organizations=entity_result["organizations"],
                locations=entity_result["locations"],
                products=entity_result["products"]
            )
        
        # Extract keywords (simplified implementation)
        keywords = await sentiment_analyzer.extract_keywords(request.text)
        
        # Calculate text statistics
        word_count = len(request.text.split())
        text_length = len(request.text)
        
        return NLPAnalysisResult(
            text=request.text,
            sentiment=sentiment,
            emotions=emotions,
            entities=entities,
            keywords=keywords,
            text_length=text_length,
            word_count=word_count,
            analyzed_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/batch-analyze", response_model=BatchAnalysisResult)
async def batch_analyze_texts(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Analyze multiple texts in batch"""
    
    if len(request.texts) > 100:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Maximum 100 texts allowed per batch"
        )
    
    start_time = datetime.utcnow()
    results = []
    
    try:
        for text in request.texts:
            # Create individual analysis request
            analysis_request = SentimentRequest(
                text=text,
                analyze_emotions=request.analyze_emotions,
                extract_entities=request.extract_entities
            )
            
            # Perform analysis for each text
            result = await analyze_text(analysis_request, current_user)
            results.append(result)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return BatchAnalysisResult(
            results=results,
            total_processed=len(results),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )


@router.get("/trending", response_model=TrendingTopics)
async def get_trending_topics(
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    platform: Optional[str] = Query(None, regex="^(twitter|facebook|instagram|all)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get trending topics based on recent social media analysis"""
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Build query for social media posts
    query = """
    SELECT content, sentiment, emotions, entities, keywords
    FROM social_media_posts 
    WHERE created_at >= :start_time
    """
    
    params = {"start_time": start_time}
    
    if platform and platform != "all":
        query += " AND platform = :platform"
        params["platform"] = platform
    
    query += " ORDER BY created_at DESC LIMIT 1000"
    
    result = await db.execute(query, params)
    posts = result.all()
    
    # Analyze trending topics
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    emotion_counts = {}
    keyword_frequency = {}
    entity_frequency = {}
    
    for post in posts:
        # Count sentiment distribution
        if post.sentiment:
            sentiment_counts[post.sentiment] = sentiment_counts.get(post.sentiment, 0) + 1
        
        # Count emotion distribution
        if post.emotions:
            emotions = json.loads(post.emotions) if isinstance(post.emotions, str) else post.emotions
            for emotion, score in emotions.items():
                if score > 0.5:  # Only count strong emotions
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Count keyword frequency
        if post.keywords:
            keywords = json.loads(post.keywords) if isinstance(post.keywords, str) else post.keywords
            for keyword in keywords:
                keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
        
        # Count entity frequency
        if post.entities:
            entities = json.loads(post.entities) if isinstance(post.entities, str) else post.entities
            for entity in entities:
                entity_name = entity.get("text", "")
                if entity_name:
                    entity_frequency[entity_name] = entity_frequency.get(entity_name, 0) + 1
    
    # Get top trending topics (combination of keywords and entities)
    all_topics = {}
    all_topics.update(keyword_frequency)
    all_topics.update(entity_frequency)
    
    # Sort by frequency and get top topics
    trending_topics = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)[:20]
    
    topics = [
        {
            "topic": topic,
            "frequency": freq,
            "type": "keyword" if topic in keyword_frequency else "entity",
            "growth_rate": 0.0  # Simplified - would calculate actual growth
        }
        for topic, freq in trending_topics
    ]
    
    time_period = f"Last {hours} hours"
    
    return TrendingTopics(
        topics=topics,
        sentiment_distribution=sentiment_counts,
        emotion_distribution=emotion_counts,
        time_period=time_period
    )


@router.get("/recommendations", response_model=ContentRecommendation)
async def get_content_recommendations(
    target_audience: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    campaign_goal: Optional[str] = Query("engagement", regex="^(awareness|engagement|conversion|retention)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get content recommendations based on audience analysis and trends"""
    
    # Analyze recent successful campaigns for insights
    query = """
    SELECT ac.headline, ac.description, ac.ctr, c.target_audience_emotions
    FROM ad_creatives ac
    JOIN campaigns c ON ac.campaign_id = c.id
    WHERE c.owner_id = :owner_id
    AND ac.ctr > 0.05  -- High performing ads (CTR > 5%)
    ORDER BY ac.ctr DESC
    LIMIT 50
    """
    
    result = await db.execute(query, {"owner_id": current_user.id})
    successful_ads = result.all()
    
    # Analyze what emotions and keywords work best
    recommended_emotions = []
    suggested_keywords = []
    target_audience_emotions = {}
    
    # Default recommendations based on campaign goal
    if campaign_goal == "awareness":
        recommended_emotions = ["curiosity", "excitement", "surprise"]
        optimal_sentiment = "positive"
    elif campaign_goal == "engagement":
        recommended_emotions = ["joy", "excitement", "nostalgia"]
        optimal_sentiment = "positive"
    elif campaign_goal == "conversion":
        recommended_emotions = ["urgency", "desire", "trust"]
        optimal_sentiment = "positive"
    else:  # retention
        recommended_emotions = ["satisfaction", "loyalty", "comfort"]
        optimal_sentiment = "positive"
    
    # Analyze successful ads for patterns
    if successful_ads:
        emotion_performance = {}
        for ad in successful_ads:
            if ad.target_audience_emotions:
                emotions = json.loads(ad.target_audience_emotions) if isinstance(ad.target_audience_emotions, str) else ad.target_audience_emotions
                for emotion, score in emotions.items():
                    if emotion not in emotion_performance:
                        emotion_performance[emotion] = []
                    emotion_performance[emotion].append(ad.ctr)
        
        # Calculate average CTR for each emotion
        for emotion, ctrs in emotion_performance.items():
            target_audience_emotions[emotion] = sum(ctrs) / len(ctrs)
        
        # Update recommendations based on performance
        top_emotions = sorted(target_audience_emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        recommended_emotions = [emotion for emotion, _ in top_emotions]
    
    # Generate keyword suggestions based on industry
    industry_keywords = {
        "technology": ["innovation", "digital", "smart", "future", "efficient"],
        "fashion": ["style", "trendy", "elegant", "fashionable", "chic"],
        "food": ["delicious", "fresh", "authentic", "gourmet", "healthy"],
        "travel": ["adventure", "discover", "explore", "memorable", "exotic"],
        "finance": ["secure", "profitable", "investment", "growth", "reliable"],
        "healthcare": ["wellness", "healthy", "care", "professional", "trusted"],
        "education": ["learn", "knowledge", "skill", "growth", "expert"],
        "entertainment": ["fun", "exciting", "thrilling", "amazing", "spectacular"]
    }
    
    if industry and industry in industry_keywords:
        suggested_keywords = industry_keywords[industry]
    else:
        suggested_keywords = ["quality", "premium", "exclusive", "limited", "special"]
    
    # Generate content suggestions
    content_suggestions = [
        f"Create content that evokes {recommended_emotions[0] if recommended_emotions else 'positive emotions'}",
        f"Use {optimal_sentiment} language and tone",
        f"Incorporate keywords: {', '.join(suggested_keywords[:3])}",
        "Focus on benefits rather than features",
        "Include social proof or testimonials",
        "Create urgency with limited-time offers",
        "Use storytelling to connect emotionally",
        "Optimize for mobile viewing"
    ]
    
    return ContentRecommendation(
        recommended_emotions=recommended_emotions,
        suggested_keywords=suggested_keywords,
        optimal_sentiment=optimal_sentiment,
        content_suggestions=content_suggestions,
        target_audience_emotions=target_audience_emotions
    )


@router.get("/sentiment-history")
async def get_sentiment_history(
    platform: Optional[str] = Query(None, regex="^(twitter|facebook|instagram|all)$"),
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get historical sentiment trends"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = """
    SELECT 
        DATE_TRUNC('day', created_at) as date,
        sentiment,
        COUNT(*) as count,
        AVG(CASE WHEN sentiment = 'positive' THEN 1 WHEN sentiment = 'negative' THEN -1 ELSE 0 END) as sentiment_score
    FROM social_media_posts 
    WHERE created_at >= :start_date
    """
    
    params = {"start_date": start_date}
    
    if platform and platform != "all":
        query += " AND platform = :platform"
        params["platform"] = platform
    
    query += " GROUP BY DATE_TRUNC('day', created_at), sentiment ORDER BY date"
    
    result = await db.execute(query, params)
    data = result.all()
    
    # Format data for time series
    sentiment_history = {}
    for row in data:
        date_str = row.date.strftime("%Y-%m-%d")
        if date_str not in sentiment_history:
            sentiment_history[date_str] = {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "sentiment_score": 0.0
            }
        
        sentiment_history[date_str][row.sentiment] = row.count
        sentiment_history[date_str]["sentiment_score"] = float(row.sentiment_score)
    
    return {
        "sentiment_history": sentiment_history,
        "period": f"Last {days} days",
        "platform": platform or "all"
    }


@router.post("/keywords/extract")
async def extract_keywords_from_text(
    text: str,
    max_keywords: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """Extract keywords from text using NLP"""
    
    try:
        keywords = await sentiment_analyzer.extract_keywords(text, max_keywords=max_keywords)
        
        return {
            "text": text,
            "keywords": keywords,
            "keyword_count": len(keywords),
            "extracted_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Keyword extraction failed: {str(e)}"
        )


@router.get("/models/status")
async def get_model_status(
    current_user: User = Depends(get_current_user)
):
    """Get status of NLP models"""
    
    # Only allow advertisers to check model status
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return {
        "sentiment_analyzer": {
            "status": "active",
            "model": "VADER + RoBERTa",
            "accuracy": 0.89,
            "last_updated": "2024-01-15T10:00:00Z"
        },
        "emotion_analyzer": {
            "status": "active", 
            "model": "BERT-based emotion classifier",
            "accuracy": 0.85,
            "last_updated": "2024-01-15T10:00:00Z"
        },
        "entity_extractor": {
            "status": "active",
            "model": "spaCy en_core_web_sm",
            "accuracy": 0.92,
            "last_updated": "2024-01-15T10:00:00Z"
        }
    }
