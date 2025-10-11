"""
config.py — Central configuration module for newswire_bridge
Defines environment-driven settings for Kafka, NATS, and Message Protocol Baseline (MPB).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Optional: Load .env if exists
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


# ------------------------------------------------------------------------------
# GLOBAL SETTINGS
# ------------------------------------------------------------------------------

APP_NAME = "newswire_bridge"
APP_VERSION = "0.1.0"
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# ------------------------------------------------------------------------------
# KAFKA CONFIGURATION
# ------------------------------------------------------------------------------

KAFKA = {
    "enabled": os.getenv("KAFKA_ENABLED", "true").lower() == "true",
    "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    "topic_ingest": os.getenv("KAFKA_TOPIC_INGEST", "news.ingest"),
    "topic_processed": os.getenv("KAFKA_TOPIC_PROCESSED", "news.processed"),
    "security_protocol": os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
    "sasl_mechanism": os.getenv("KAFKA_SASL_MECHANISM", ""),
    "sasl_username": os.getenv("KAFKA_SASL_USERNAME", ""),
    "sasl_password": os.getenv("KAFKA_SASL_PASSWORD", ""),
    "client_id": f"{APP_NAME}-kafka-client",
}

# ------------------------------------------------------------------------------
# NATS CONFIGURATION
# ------------------------------------------------------------------------------

NATS = {
    "enabled": os.getenv("NATS_ENABLED", "true").lower() == "true",
    "servers": os.getenv("NATS_SERVERS", "nats://localhost:4222").split(","),
    "subject_ingest": os.getenv("NATS_SUBJECT_INGEST", "news.ingest"),
    "subject_processed": os.getenv("NATS_SUBJECT_PROCESSED", "news.processed"),
    "user": os.getenv("NATS_USER", ""),
    "password": os.getenv("NATS_PASSWORD", ""),
    "name": f"{APP_NAME}-nats-client",
}

# ------------------------------------------------------------------------------
# MESSAGE PROTOCOL BASELINE (MPB)
# ------------------------------------------------------------------------------

MPB = {
    "version": "1.0",
    "schema_registry_url": os.getenv("MPB_SCHEMA_REGISTRY_URL", ""),
    "default_content_type": "application/json",
    "serialization_format": "json",  # or "avro", "protobuf"
    "validate_schema": os.getenv("MPB_VALIDATE_SCHEMA", "true").lower() == "true",
}

# ------------------------------------------------------------------------------
# SOURCE METADATA
# ------------------------------------------------------------------------------

SOURCE_REGISTRY = {
    "canonical_sources": {
        "wsj": {"id": "SRC-WSJ", "name": "Wall Street Journal", "category": "finance"},
        "ft": {"id": "SRC-FT", "name": "Financial Times", "category": "business"},
        "bloomberg": {"id": "SRC-BBG", "name": "Bloomberg", "category": "markets"},
        "reuters": {"id": "SRC-REU", "name": "Reuters", "category": "general"},
    },
    "uuid_namespace": os.getenv("MPB_UUID_NAMESPACE", "d4b03e68-65c4-43d1-9ffb-c0f11b3cddc8"),
}

# ------------------------------------------------------------------------------
# SERIALIZATION SETTINGS
# ------------------------------------------------------------------------------

SERIALIZATION = {
    "indent": int(os.getenv("JSON_INDENT", 2)),
    "ensure_ascii": False,
    "sort_keys": True,
}

# ------------------------------------------------------------------------------
# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------

LOGGING = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
}

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

def as_dict() -> dict:
    """Return all config as a consolidated dict for debugging or introspection."""
    return {
        "app": {"name": APP_NAME, "version": APP_VERSION, "debug": DEBUG_MODE},
        "kafka": KAFKA,
        "nats": NATS,
        "mpb": MPB,
        "source_registry": SOURCE_REGISTRY,
        "serialization": SERIALIZATION,
        "logging": LOGGING,
    }

