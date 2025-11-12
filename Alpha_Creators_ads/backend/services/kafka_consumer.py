"""
Kafka consumer for processing messages.
"""

import json
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from core.config import settings

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Async Kafka consumer for processing messages"""
    
    def __init__(self, topics: List[str], group_id: str):
        self.topics = topics
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        
    async def start(self):
        """Start the Kafka consumer"""
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                max_poll_records=500,
                fetch_max_wait_ms=500,
                session_timeout_ms=30000,
                heartbeat_interval_ms=3000,
            )
            
            await self.consumer.start()
            logger.info(f"Kafka consumer started for topics: {self.topics}")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise
    
    async def consume(self) -> AsyncGenerator[Any, None]:
        """Consume messages from Kafka topics"""
        if not self.consumer:
            await self.start()
        
        try:
            async for message in self.consumer:
                try:
                    logger.debug(
                        f"Received message from topic {message.topic} "
                        f"partition {message.partition} offset {message.offset}"
                    )
                    yield message
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
                    
        except KafkaError as e:
            logger.error(f"Kafka consumer error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected consumer error: {e}")
            raise
    
    async def consume_batch(self, timeout_ms: int = 1000) -> List[Any]:
        """Consume a batch of messages"""
        if not self.consumer:
            await self.start()
        
        try:
            messages = await self.consumer.getmany(timeout_ms=timeout_ms)
            batch = []
            
            for topic_partition, partition_messages in messages.items():
                for message in partition_messages:
                    batch.append(message)
            
            return batch
            
        except Exception as e:
            logger.error(f"Error consuming batch: {e}")
            return []
    
    async def seek_to_beginning(self):
        """Seek to the beginning of all partitions"""
        if self.consumer:
            self.consumer.seek_to_beginning()
    
    async def seek_to_end(self):
        """Seek to the end of all partitions"""
        if self.consumer:
            self.consumer.seek_to_end()
    
    async def commit(self):
        """Manually commit current offset"""
        if self.consumer:
            await self.consumer.commit()
    
    async def close(self):
        """Close the Kafka consumer"""
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("Kafka consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping Kafka consumer: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
