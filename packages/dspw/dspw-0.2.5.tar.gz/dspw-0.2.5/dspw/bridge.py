import asyncio
import json
from .serializers.kafka_serializer import KafkaSerializer
from .serializers.nats_serializer import NATSSerializer
from .schema.news_event import NewsEvent

class NewswireBridge:
    def __init__(self, kafka_bootstrap: str, nats_server: str):
        self.kafka = KafkaSerializer(kafka_bootstrap)
        self.nats = NATSSerializer(nats_server)

    async def start(self):
        await self.nats.connect()

    async def kafka_to_nats(self, topic: str, nats_subject: str):
        """
        Consume Kafka topic and publish to NATS subject
        """
        from confluent_kafka import Consumer
        c = Consumer({
            "bootstrap.servers": self.kafka.producer.list_topics().orig_broker_name,
            "group.id": "bridge-group",
            "auto.offset.reset": "earliest"
        })
        c.subscribe([topic])
        print(f"[Bridge] Forwarding Kafka → NATS ({topic} → {nats_subject})")
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"[Kafka Error] {msg.error()}")
                continue
            event = NewsEvent.from_json(msg.value().decode())
            await self.nats.publish(nats_subject, event)

    async def nats_to_kafka(self, subject: str, topic: str):
        """
        Subscribe NATS subject and produce to Kafka topic
        """
        async def handler(event: NewsEvent):
            self.kafka.send(topic, event)
        await self.nats.subscribe(subject, handler)
