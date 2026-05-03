import json
import logging
from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

class KafkaProducerClient:
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.broker_url,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        logger.info(f"Kafka producer connected to {self.broker_url}")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer disconnected")

    async def send_message(self, topic: str, message: dict):
        if not self.producer:
            logger.error("Kafka producer is not initialized. Call start() first.")
            return False
            
        try:
            await self.producer.send_and_wait(topic, message)
            logger.info(f"Message sent to topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            return False

# Create a singleton instance
kafka_producer = None

def get_kafka_producer() -> KafkaProducerClient:
    global kafka_producer
    if kafka_producer is None:
        import os
        broker_url = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
        kafka_producer = KafkaProducerClient(broker_url)
    return kafka_producer
