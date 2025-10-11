import asyncio
import json
from nats.aio.client import Client as NATS

from dspw.schema.news_event import NewsEvent

class NATSSerializer:

    def __init__(self, servers: str = "nats://localhost:4222"):
        self.nc = NATS()
        self.servers = servers

    async def connect(self):
        await self.nc.connect(servers=[self.servers])

    async def publish(self, subject: str, event: NewsEvent):
        msg = event.to_json().encode()
        await self.nc.publish(subject, msg)

    async def subscribe(self, subject: str, cb):
        async def message_handler(msg):
            event = NewsEvent.from_json(msg.data.decode())
            await cb(event)
        await self.nc.subscribe(subject, cb=message_handler)

    async def close(self):
        await self.nc.close()
