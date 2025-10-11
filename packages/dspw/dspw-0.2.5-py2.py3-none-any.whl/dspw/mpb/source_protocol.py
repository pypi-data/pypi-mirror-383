from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import hashlib

class SourceProtocol(BaseModel):
    """
    Message Protocol Baseline (MPB)
    Defines the fundamental source identity and metadata contract.
    """

    protocol_version: str = Field(default="1.0", description="Version of MPB protocol")
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique UUID for message source instance")
    canonical_group_id: Optional[str] = Field(None, description="Logical grouping or domain of source (e.g., wsj|ft|bloomberg)")
    canonical_id: Optional[str] = Field(None, description="Canonical source identifier (e.g., wsj:article:12345)")
    source_name: str = Field(..., description="Human-readable name of the source, e.g., WSJ")
    provider_type: Optional[str] = Field(None, description="Publisher, Aggregator, Research, etc.")
    origin_url: Optional[HttpUrl] = None
    region: Optional[str] = None
    language: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    registered_at: datetime = Field(default_factory=datetime.utcnow)

    def lineage_hash(self) -> str:
        """
        Return deterministic lineage hash for tracking identity in downstream brokers.
        """
        base = f"{self.source_name}:{self.canonical_group_id or ''}:{self.canonical_id or ''}"
        return "sha256:" + hashlib.sha256(base.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Return as dict for serialization."""
        return self.model_dump(exclude_none=True)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SourceProtocol":
        """Instantiate from dict."""
        return SourceProtocol(**data)
