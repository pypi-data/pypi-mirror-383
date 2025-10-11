import json
from confluent_kafka import Producer, Consumer, KafkaError

from dspw.mpb.serializers.utils import get_content_hash
from dspw.schema.news_event import NewsEvent

class KafkaSerializer:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def send(self, topic: str, event: NewsEvent):
        key = event.canonical_id.encode()
        value = event.to_json().encode()
        self.producer.produce(topic=topic, key=key, value=value)
        self.producer.flush()

    @staticmethod
    def deserialize(record_value: bytes) -> NewsEvent:
        return NewsEvent.from_json(record_value.decode("utf-8"))
