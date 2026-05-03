import os
import json
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
from src.core.database import engine
from sqlmodel import Session
from src.repository.catalog_repository import CatalogRepository
from src.services.catalog_service import CatalogService
from src.services.elasticsearch_service import get_elasticsearch_service

logger = logging.getLogger(__name__)

class KafkaConsumerClient:
    def __init__(self, broker_url: str, topic: str, group_id: str):
        self.broker_url = broker_url
        self.topic = topic
        self.group_id = group_id
        self.consumer = None
        self.task = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.broker_url,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer started for topic {self.topic}")
        # Start background task to consume messages
        self.task = asyncio.create_task(self.consume())

    async def stop(self):
        if self.task:
            self.task.cancel()
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    async def consume(self):
        try:
            async for msg in self.consumer:
                logger.info(f"Received message on topic {msg.topic}: {msg.value}")
                await self.process_message(msg.value)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")

    async def process_message(self, message: dict):
        if not message:
            return
            
        # Create a new DB session for processing this message
        with Session(engine) as session:
            repository = CatalogRepository(session)
            es_service = get_elasticsearch_service()
            service = CatalogService(repository, es_service)
            await service.handle_broker_message(message)

# Singleton instance
kafka_consumer = None

def get_kafka_consumer() -> KafkaConsumerClient:
    global kafka_consumer
    if kafka_consumer is None:
        broker_url = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
        group_id = os.getenv("GROUP_ID", "catalog-service-group")
        kafka_consumer = KafkaConsumerClient(broker_url, "order_events", group_id)
    return kafka_consumer
