from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from dspw.mpb.source_protocol import SourceProtocol

class NewsEvent(BaseModel):
    schema_version: str = "1.4"
    event_id: str
    canonical_id: str
    source: SourceProtocol                 # ⬅ replaced with MPB class
    type: str
    title: Optional[str] = None
    summary: Optional[str] = None
    body_text: Optional[str] = None
    published_at: Optional[datetime] = None
    first_seen_at: Optional[datetime] = None
    authors: List[Dict[str, Any]] = []
    media: List[Dict[str, Any]] = []
    tags: List[str] = []
    content_hash: Optional[str] = None
    ingest_meta: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)

    @staticmethod
    def from_json(data: str) -> "NewsEvent":
        return NewsEvent.model_validate_json(data)
