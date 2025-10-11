- [Summary](#summary)
- [Project Structure](#project-structure)
- [Build and Command](#build-and-command)
- [Config Files](#config-files)
  - [`config/py`](#configpy)

## Summary

dspw is a Python library that provides a unified message protocol baseline (MPB) and transport abstraction for ingesting, normalizing, and redistributing financial or journalistic content from heterogeneous online sources such as Wall Street Journal (WSJ), Financial Times (FT), Bloomberg, and others.

It defines:

A normalized message schema for news, feeds, threads, and reports objects, designed to work seamlessly across Kafka and NATS brokers.

A Source metadata class (with UUID, canonical group ID, origin identifiers, etc.) forming the core of the MPB.

Inter-broker serialization utilities to translate and validate message payloads between Kafka and NATS in a unified object format.

Publisher–Subscriber interfaces to streamline ingestion pipelines, transformation logic, and event-driven analytics integration.

A distribution-ready Python package (PEP 621-compliant) supporting build, wheel packaging, and deployment to public or private registries (e.g., PyPI, GitHub Packages, or JFrog Artifactory).

The project can be extended for:

Event-sourcing pipelines and real-time news aggregation systems,

Quantitative research ingestion frameworks,

Sentiment analysis feeds or market intelligence dashboards that rely on unified feed ingestion from multiple third-party sources.

## Project Structure

```
dspw/
├── **init**.py
├── schema/
│ ├── **init**.py
│ └── news_event.py
├── mpb/
│ ├── **init**.py
│ └── source_protocol.py # Message Protocol Baseline (MPB)
├── serializers/
│ ├── **init**.py
│ ├── kafka_serializer.py
│ ├── nats_serializer.py
│ └── utils.py
├── bridge.py
├── config.py
└── pyproject.toml
```

## Build and Command

```sh
# create the distribution wheel and sdist
python3 -m build

# check the wheel structure
twine check dist/*

# upload to test pypi
twine upload --repository dspw dist/*

# install for verification
pip install -i https://test.pypi.org/simple/ dspw

```

## Config Files

### [`config/py`](./config.py)

How to use the config file, E.g.:

```py
from dspw import config

print(config.KAFKA["bootstrap_servers"])
print(config.MPB["serialization_format"])
print(config.SOURCE_REGISTRY["canonical_sources"]["ft"])

```
