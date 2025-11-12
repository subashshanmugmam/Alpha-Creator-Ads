"""
Natural Language Processing and Sentiment Analysis Engine.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
import numpy as np
from dataclasses import dataclass, asdict

# ML/NLP imports (will be installed)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    import spacy
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("ML/NLP libraries not installed. Install requirements.txt")

from core.config import settings
from services.kafka_consumer import KafkaConsumer
from services.kafka_producer import KafkaProducer

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    overall_sentiment: str  # positive, negative, neutral
    confidence: float
    emotion_scores: Dict[str, float]
    subjectivity: float
    polarity: float


@dataclass
class EmotionResult:
    """Emotion detection result"""
    emotions: Dict[str, float]  # emotion: confidence
    dominant_emotion: str
    emotional_intensity: float


@dataclass
class EntityResult:
    """Named entity recognition result"""
    entities: List[Dict[str, Any]]
    topics: List[str]
    intent: Optional[str]
    confidence: float


@dataclass
class NLPAnalysisResult:
    """Complete NLP analysis result"""
    post_id: str
    platform: str
    content: str
    sentiment: SentimentResult
    emotions: EmotionResult
    entities: EntityResult
    processed_at: datetime
    processing_time: float


class SentimentAnalyzer:
    """Multi-level sentiment analysis"""
    
    def __init__(self):
        self.vader_analyzer = None
        self.bert_pipeline = None
        self.emotion_pipeline = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize sentiment analysis models"""
        try:
            # VADER for quick sentiment
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
            # BERT-based sentiment analysis
            self.bert_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Emotion detection
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                tokenizer="j-hartmann/emotion-english-distilroberta-base"
            )
            
            logger.info("Sentiment analysis models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing sentiment models: {e}")
    
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """Perform comprehensive sentiment analysis"""
        try:
            # VADER sentiment
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # BERT sentiment
            bert_result = self.bert_pipeline(text)[0]
            
            # TextBlob for subjectivity
            blob = TextBlob(text)
            
            # Emotion scores
            emotion_results = self.emotion_pipeline(text)
            emotion_scores = {result['label']: result['score'] for result in emotion_results}
            
            # Determine overall sentiment
            overall_sentiment = self._determine_overall_sentiment(
                vader_scores, bert_result['label']
            )
            
            return SentimentResult(
                overall_sentiment=overall_sentiment,
                confidence=bert_result['score'],
                emotion_scores=emotion_scores,
                subjectivity=float(blob.sentiment.subjectivity),
                polarity=float(blob.sentiment.polarity)
            )
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return SentimentResult(
                overall_sentiment="neutral",
                confidence=0.0,
                emotion_scores={},
                subjectivity=0.0,
                polarity=0.0
            )
    
    def _determine_overall_sentiment(self, vader_scores: Dict, bert_label: str) -> str:
        """Combine VADER and BERT results for overall sentiment"""
        # Map BERT labels to standard format
        bert_mapping = {
            "LABEL_0": "negative",
            "LABEL_1": "neutral", 
            "LABEL_2": "positive"
        }
        
        bert_sentiment = bert_mapping.get(bert_label, "neutral")
        
        # VADER compound score
        compound = vader_scores['compound']
        if compound >= 0.05:
            vader_sentiment = "positive"
        elif compound <= -0.05:
            vader_sentiment = "negative"
        else:
            vader_sentiment = "neutral"
        
        # Combine results (prefer BERT for accuracy)
        if bert_sentiment == vader_sentiment:
            return bert_sentiment
        elif abs(compound) > 0.6:  # Strong VADER signal
            return vader_sentiment
        else:
            return bert_sentiment


class EmotionAnalyzer:
    """Emotion detection and analysis"""
    
    def __init__(self):
        self.emotion_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize emotion detection models"""
        try:
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                tokenizer="j-hartmann/emotion-english-distilroberta-base"
            )
            logger.info("Emotion analysis models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing emotion models: {e}")
    
    async def analyze_emotions(self, text: str) -> EmotionResult:
        """Detect emotions in text"""
        try:
            if not self.emotion_model:
                return EmotionResult(
                    emotions={},
                    dominant_emotion="neutral",
                    emotional_intensity=0.0
                )
            
            # Get emotion predictions
            results = self.emotion_model(text)
            
            # Convert to emotion scores dict
            emotions = {}
            for result in results:
                emotions[result['label']] = result['score']
            
            # Find dominant emotion
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            
            # Calculate emotional intensity (max confidence)
            emotional_intensity = max(emotions.values()) if emotions else 0.0
            
            return EmotionResult(
                emotions=emotions,
                dominant_emotion=dominant_emotion,
                emotional_intensity=emotional_intensity
            )
            
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return EmotionResult(
                emotions={},
                dominant_emotion="neutral",
                emotional_intensity=0.0
            )


class EntityExtractor:
    """Named entity recognition and topic extraction"""
    
    def __init__(self):
        self.nlp_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NER models"""
        try:
            # Load spaCy model
            self.nlp_model = spacy.load("en_core_web_sm")
            logger.info("NER models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing NER models: {e}")
    
    async def extract_entities(self, text: str) -> EntityResult:
        """Extract entities, topics, and intent"""
        try:
            if not self.nlp_model:
                return EntityResult(
                    entities=[],
                    topics=[],
                    intent=None,
                    confidence=0.0
                )
            
            # Process text with spaCy
            doc = self.nlp_model(text)
            
            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 1.0  # spaCy doesn't provide confidence by default
                })
            
            # Extract topics (simplified - use noun phrases)
            topics = [chunk.text.lower() for chunk in doc.noun_chunks]
            
            # Intent classification (simplified keyword-based)
            intent = self._classify_intent(text.lower())
            
            return EntityResult(
                entities=entities,
                topics=topics,
                intent=intent,
                confidence=0.8  # Placeholder confidence
            )
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return EntityResult(
                entities=[],
                topics=[],
                intent=None,
                confidence=0.0
            )
    
    def _classify_intent(self, text: str) -> Optional[str]:
        """Simple intent classification based on keywords"""
        purchase_keywords = ["buy", "purchase", "order", "shop", "deal", "sale", "discount"]
        complaint_keywords = ["complain", "problem", "issue", "bad", "terrible", "awful"]
        research_keywords = ["review", "compare", "opinion", "recommend", "suggest"]
        
        if any(keyword in text for keyword in purchase_keywords):
            return "purchase_intent"
        elif any(keyword in text for keyword in complaint_keywords):
            return "complaint"
        elif any(keyword in text for keyword in research_keywords):
            return "research"
        else:
            return "general"


class NLPProcessingService:
    """Main NLP processing service"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.entity_extractor = EntityExtractor()
        self.kafka_consumer = KafkaConsumer(
            topics=["social_media_posts"],
            group_id="nlp_processors"
        )
        self.kafka_producer = KafkaProducer()
        self.processing_stats = {
            "processed_count": 0,
            "error_count": 0,
            "avg_processing_time": 0.0
        }
    
    async def start_processing(self):
        """Start NLP processing of social media posts"""
        logger.info("Starting NLP processing service...")
        
        async for message in self.kafka_consumer.consume():
            try:
                start_time = datetime.utcnow()
                
                # Parse the message
                post_data = json.loads(message.value)
                
                # Process the post
                result = await self.process_post(post_data)
                
                # Calculate processing time
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                result.processing_time = processing_time
                
                # Send to next stage
                await self.kafka_producer.send_message(
                    topic="nlp_analysis_results",
                    message=asdict(result)
                )
                
                # Update stats
                self._update_stats(processing_time)
                
                if self.processing_stats["processed_count"] % 100 == 0:
                    logger.info(f"Processed {self.processing_stats['processed_count']} posts")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                self.processing_stats["error_count"] += 1
    
    async def process_post(self, post_data: Dict) -> NLPAnalysisResult:
        """Process a single social media post"""
        content = post_data.get("content", "")
        
        # Run all analyses concurrently
        sentiment_task = self.sentiment_analyzer.analyze_sentiment(content)
        emotion_task = self.emotion_analyzer.analyze_emotions(content)
        entity_task = self.entity_extractor.extract_entities(content)
        
        sentiment_result, emotion_result, entity_result = await asyncio.gather(
            sentiment_task, emotion_task, entity_task
        )
        
        return NLPAnalysisResult(
            post_id=post_data.get("post_id", ""),
            platform=post_data.get("platform", ""),
            content=content,
            sentiment=sentiment_result,
            emotions=emotion_result,
            entities=entity_result,
            processed_at=datetime.utcnow(),
            processing_time=0.0  # Will be set by caller
        )
    
    def _update_stats(self, processing_time: float):
        """Update processing statistics"""
        self.processing_stats["processed_count"] += 1
        
        # Update average processing time
        count = self.processing_stats["processed_count"]
        current_avg = self.processing_stats["avg_processing_time"]
        self.processing_stats["avg_processing_time"] = (
            (current_avg * (count - 1) + processing_time) / count
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.processing_stats.copy()
    
    async def stop_processing(self):
        """Stop NLP processing"""
        logger.info("Stopping NLP processing service...")
        await self.kafka_consumer.close()
        await self.kafka_producer.close()


# Singleton instance
nlp_service = NLPProcessingService()
