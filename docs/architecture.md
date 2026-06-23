# Architecture Decisions

## Data Layers
Project will use explicit data layers in ADLS/Blob Storage:

- data/raw: raw JSON landing from NewsAPI
- data/silver: enriched articles with sentiment, entities, embeddings
- data/gold: aggregated analytics and persistent tables
- data/metadata: schemas, manifests, and lineage helper files

## Polling: Logic Apps vs ADF HTTP

### Logic Apps
Pros:
- Event-driven and simple scheduling
- Low-code with built-in connectors
- Better suited for simple API polling workflows

### ADF HTTP
Pros:
- Rich ETL orchestration for complex pipelines
- Better for heavy data transformations and mapping

Decision: Logic Apps preferred for NewsAPI polling because the task is schedule-based API retrieval rather than complex ETL.

## Eventing: Event Grid vs Event Hub

### Event Grid
- Optimized for discrete event notifications (file arrivals)
- Low latency, serverless-friendly

### Event Hub
- Optimized for high-throughput streaming scenarios
- Better for millions of events per second

Decision: Event Grid is preferred because ingestion produces periodic file-arrival events rather than high-volume streaming.
