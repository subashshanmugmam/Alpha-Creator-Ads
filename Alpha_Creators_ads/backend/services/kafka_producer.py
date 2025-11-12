"""
Kafka producer for message streaming.
"""

import json
import logging
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from core.config import settings

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Async Kafka producer for sending messages"""
    
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        
    async def start(self):
        """Start the Kafka producer"""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                compression_type="gzip",
                batch_size=16384,
                linger_ms=10,
                max_request_size=1048576,
                retry_backoff_ms=100,
                request_timeout_ms=30000,
            )
            
            await self.producer.start()
            logger.info("Kafka producer started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise
    
    async def send_message(
        self, 
        topic: str, 
        message: Dict[str, Any], 
        key: Optional[str] = None
    ) -> bool:
        """Send a message to Kafka topic"""
        if not self.producer:
            await self.start()
        
        try:
            # Send message
            future = await self.producer.send(topic, message, key=key)
            
            # Get metadata about the sent message
            record_metadata = await future
            
            logger.debug(
                f"Message sent to topic {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    async def send_batch(
        self, 
        topic: str, 
        messages: list[Dict[str, Any]], 
        keys: Optional[list[str]] = None
    ) -> int:
        """Send a batch of messages"""
        if not self.producer:
            await self.start()
        
        successful_sends = 0
        
        for i, message in enumerate(messages):
            key = keys[i] if keys and i < len(keys) else None
            success = await self.send_message(topic, message, key)
            if success:
                successful_sends += 1
        
        return successful_sends
    
    async def close(self):
        """Close the Kafka producer"""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("Kafka producer stopped")
            except Exception as e:
                logger.error(f"Error stopping Kafka producer: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
