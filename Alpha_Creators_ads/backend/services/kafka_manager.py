"""
Kafka Manager for centralized message streaming management.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError, KafkaConnectionError
from datetime import datetime
import traceback

from core.config import settings

logger = logging.getLogger(__name__)


class KafkaManager:
    """Centralized Kafka management for producers and consumers"""
    
    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.producers: Dict[str, AIOKafkaProducer] = {}
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self.consumer_tasks: Dict[str, asyncio.Task] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.is_running = False
        
    async def start(self):
        """Start the Kafka manager"""
        try:
            logger.info("Starting Kafka Manager...")
            self.is_running = True
            
            # Initialize default producer
            await self.create_producer("default")
            
            # Initialize default consumers
            await self.create_consumer("social_media_posts", ["social_media_posts"])
            await self.create_consumer("nlp_analysis", ["nlp_analysis"])
            await self.create_consumer("ad_optimization", ["ad_optimization"])
            
            logger.info("Kafka Manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka Manager: {e}")
            raise
    
    async def stop(self):
        """Stop the Kafka manager and cleanup resources"""
        try:
            logger.info("Stopping Kafka Manager...")
            self.is_running = False
            
            # Stop all consumer tasks
            for task_name, task in self.consumer_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        logger.info(f"Consumer task {task_name} cancelled")
            
            # Stop all consumers
            for consumer_name, consumer in self.consumers.items():
                try:
                    await consumer.stop()
                    logger.info(f"Consumer {consumer_name} stopped")
                except Exception as e:
                    logger.error(f"Error stopping consumer {consumer_name}: {e}")
            
            # Stop all producers
            for producer_name, producer in self.producers.items():
                try:
                    await producer.stop()
                    logger.info(f"Producer {producer_name} stopped")
                except Exception as e:
                    logger.error(f"Error stopping producer {producer_name}: {e}")
            
            logger.info("Kafka Manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Kafka Manager: {e}")
    
    async def create_producer(self, name: str, **kwargs) -> AIOKafkaProducer:
        """Create a new Kafka producer"""
        try:
            producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                compression_type='gzip',
                max_batch_size=16384,
                linger_ms=10,
                **kwargs
            )
            
            await producer.start()
            self.producers[name] = producer
            
            logger.info(f"Kafka producer '{name}' created and started")
            return producer
            
        except Exception as e:
            logger.error(f"Failed to create producer '{name}': {e}")
            raise
    
    async def create_consumer(
        self, 
        name: str, 
        topics: List[str], 
        group_id: Optional[str] = None,
        **kwargs
    ) -> AIOKafkaConsumer:
        """Create a new Kafka consumer"""
        try:
            if not group_id:
                group_id = f"{name}_group"
            
            consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                **kwargs
            )
            
            await consumer.start()
            self.consumers[name] = consumer
            
            logger.info(f"Kafka consumer '{name}' created for topics {topics}")
            return consumer
            
        except Exception as e:
            logger.error(f"Failed to create consumer '{name}': {e}")
            raise
    
    async def send_message(
        self, 
        topic: str, 
        message: Dict[str, Any], 
        key: Optional[str] = None,
        producer_name: str = "default"
    ):
        """Send a message to a Kafka topic"""
        try:
            producer = self.producers.get(producer_name)
            if not producer:
                raise ValueError(f"Producer '{producer_name}' not found")
            
            # Add metadata
            enriched_message = {
                **message,
                "timestamp": datetime.utcnow().isoformat(),
                "producer": producer_name
            }
            
            # Send message
            await producer.send(
                topic, 
                value=enriched_message, 
                key=key.encode('utf-8') if key else None
            )
            
            logger.debug(f"Message sent to topic '{topic}': {key}")
            
        except Exception as e:
            logger.error(f"Failed to send message to topic '{topic}': {e}")
            raise
    
    def register_message_handler(self, consumer_name: str, handler: Callable):
        """Register a message handler for a consumer"""
        self.message_handlers[consumer_name] = handler
        logger.info(f"Handler registered for consumer '{consumer_name}'")
    
    async def start_consumer_loop(self, consumer_name: str):
        """Start the message consumption loop for a consumer"""
        try:
            consumer = self.consumers.get(consumer_name)
            handler = self.message_handlers.get(consumer_name)
            
            if not consumer:
                logger.error(f"Consumer '{consumer_name}' not found")
                return
            
            if not handler:
                logger.warning(f"No handler registered for consumer '{consumer_name}'")
                return
            
            logger.info(f"Starting consumer loop for '{consumer_name}'")
            
            async for message in consumer:
                try:
                    if not self.is_running:
                        break
                    
                    # Process message with handler
                    await handler(message.value)
                    
                    # Commit offset
                    await consumer.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing message in '{consumer_name}': {e}")
                    logger.error(traceback.format_exc())
                    
        except Exception as e:
            logger.error(f"Consumer loop error for '{consumer_name}': {e}")
            logger.error(traceback.format_exc())
    
    async def start_all_consumers(self):
        """Start consumption loops for all registered consumers"""
        for consumer_name in self.consumers.keys():
            if consumer_name not in self.consumer_tasks:
                task = asyncio.create_task(self.start_consumer_loop(consumer_name))
                self.consumer_tasks[consumer_name] = task
                logger.info(f"Started consumer task for '{consumer_name}'")
    
    async def get_topic_metadata(self, topic: str) -> Dict[str, Any]:
        """Get metadata for a Kafka topic"""
        try:
            producer = self.producers.get("default")
            if not producer:
                raise ValueError("Default producer not available")
            
            cluster = producer.client.cluster
            metadata = cluster.topics().get(topic)
            
            if metadata:
                return {
                    "topic": topic,
                    "partitions": len(metadata.partitions),
                    "replicas": len(metadata.partitions[0].replicas) if metadata.partitions else 0,
                    "available": True
                }
            else:
                return {
                    "topic": topic,
                    "available": False,
                    "error": "Topic not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting metadata for topic '{topic}': {e}")
            return {
                "topic": topic,
                "available": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Kafka connections"""
        health_status = {
            "kafka_manager": "healthy",
            "producers": {},
            "consumers": {},
            "bootstrap_servers": self.bootstrap_servers
        }
        
        # Check producers
        for name, producer in self.producers.items():
            try:
                # Try to get cluster metadata as health check
                cluster = producer.client.cluster
                bootstrap_connected = len(cluster.brokers()) > 0
                
                health_status["producers"][name] = {
                    "status": "healthy" if bootstrap_connected else "unhealthy",
                    "bootstrap_connected": bootstrap_connected,
                    "brokers_count": len(cluster.brokers())
                }
            except Exception as e:
                health_status["producers"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check consumers
        for name, consumer in self.consumers.items():
            try:
                # Check if consumer is still running
                is_running = not consumer._closed
                
                health_status["consumers"][name] = {
                    "status": "healthy" if is_running else "unhealthy",
                    "running": is_running,
                    "subscribed_topics": list(consumer.subscription())
                }
            except Exception as e:
                health_status["consumers"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Overall health
        all_producers_healthy = all(
            p.get("status") == "healthy" 
            for p in health_status["producers"].values()
        )
        all_consumers_healthy = all(
            c.get("status") == "healthy" 
            for c in health_status["consumers"].values()
        )
        
        if not all_producers_healthy or not all_consumers_healthy:
            health_status["kafka_manager"] = "degraded"
        
        return health_status
    
    # Convenience methods for common operations
    
    async def send_social_media_post(self, post_data: Dict[str, Any]):
        """Send social media post data"""
        await self.send_message("social_media_posts", post_data, key=post_data.get("id"))
    
    async def send_nlp_analysis(self, analysis_data: Dict[str, Any]):
        """Send NLP analysis data"""
        await self.send_message("nlp_analysis", analysis_data, key=analysis_data.get("post_id"))
    
    async def send_ad_optimization(self, optimization_data: Dict[str, Any]):
        """Send ad optimization data"""
        await self.send_message("ad_optimization", optimization_data, key=optimization_data.get("campaign_id"))
    
    async def send_user_event(self, event_data: Dict[str, Any]):
        """Send user event data"""
        await self.send_message("user_events", event_data, key=event_data.get("user_id"))
    
    async def send_campaign_event(self, event_data: Dict[str, Any]):
        """Send campaign event data"""
        await self.send_message("campaign_events", event_data, key=event_data.get("campaign_id"))


# Global Kafka manager instance
kafka_manager = KafkaManager()


# Message handlers for different types of data

async def handle_social_media_message(message: Dict[str, Any]):
    """Handle incoming social media messages"""
    try:
        logger.info(f"Processing social media message: {message.get('id', 'unknown')}")
        
        # Import here to avoid circular imports
        from services.nlp_engine import SentimentAnalyzer, EmotionAnalyzer
        
        # Analyze sentiment and emotions
        nlp_analyzer = SentimentAnalyzer()
        emotion_analyzer = EmotionAnalyzer()
        
        content = message.get('content', '')
        if content:
            # Perform NLP analysis
            sentiment_result = await nlp_analyzer.analyze_sentiment(content)
            emotion_result = await emotion_analyzer.analyze_emotions(content)
            
            # Send analysis results
            analysis_data = {
                "post_id": message.get('id'),
                "platform": message.get('platform'),
                "sentiment": sentiment_result,
                "emotions": emotion_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await kafka_manager.send_nlp_analysis(analysis_data)
        
    except Exception as e:
        logger.error(f"Error handling social media message: {e}")


async def handle_nlp_analysis_message(message: Dict[str, Any]):
    """Handle NLP analysis results"""
    try:
        logger.info(f"Processing NLP analysis: {message.get('post_id', 'unknown')}")
        
        # Store analysis results in database or trigger further processing
        # This could trigger ad optimization or audience insights updates
        
        # Example: Trigger RL optimization if sentiment is strongly negative
        sentiment = message.get('sentiment', {})
        if sentiment.get('sentiment') == 'negative' and sentiment.get('confidence', 0) > 0.8:
            # Send signal for potential campaign optimization
            optimization_data = {
                "trigger": "negative_sentiment",
                "severity": sentiment.get('confidence'),
                "post_id": message.get('post_id'),
                "platform": message.get('platform'),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await kafka_manager.send_ad_optimization(optimization_data)
        
    except Exception as e:
        logger.error(f"Error handling NLP analysis message: {e}")


async def handle_ad_optimization_message(message: Dict[str, Any]):
    """Handle ad optimization triggers"""
    try:
        logger.info(f"Processing optimization trigger: {message.get('trigger', 'unknown')}")
        
        # Import here to avoid circular imports
        from services.reinforcement_learning import rl_manager
        
        # Process optimization triggers
        campaign_id = message.get('campaign_id')
        if campaign_id:
            # Run RL optimization cycle
            await rl_manager.run_optimization_cycle(campaign_id)
        
    except Exception as e:
        logger.error(f"Error handling ad optimization message: {e}")


# Register message handlers
def register_default_handlers():
    """Register default message handlers"""
    kafka_manager.register_message_handler("social_media_posts", handle_social_media_message)
    kafka_manager.register_message_handler("nlp_analysis", handle_nlp_analysis_message)
    kafka_manager.register_message_handler("ad_optimization", handle_ad_optimization_message)
