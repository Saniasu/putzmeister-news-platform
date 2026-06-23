# News NLP Pipeline Project

## Overview
This project implements a layered Azure-based news ingestion and NLP pipeline using NewsAPI data.
The goal is to ingest raw articles, enrich them with sentiment, entities, and vector embeddings, store a silver dataset in ADLS Gen2, index the data in Azure AI Search, and expose a search API with analytics.

## Project Goal
- Ingest news from `newsapi.org`
- Enrich articles with Azure Cognitive Services and Azure OpenAI
- Store enriched data in a silver layer in ADLS Gen2
- Compute gold analytics via Databricks/ADF
- Index documents into Azure AI Search with hybrid keyword + vector search
- Serve search and trend analytics through an Azure Function API
- Track governance with Microsoft Purview

## Architecture Layers
1. **Layer 1 — Ingestion**
   - Logic App polls NewsAPI by category
   - Raw JSON is written to Blob Storage landing zone
   - Event Grid fans out to two Azure Functions: NLP job trigger and audit logging
   - Key design: idempotent ingestion using URL hash deduplication

2. **Layer 2 — NLP Enrichment**
   - Azure Function reads raw articles and calls Language API for sentiment, entities, key phrases
   - Another process calls Azure OpenAI for embeddings
   - Results merge into a silver layer in ADLS Gen2
   - Key design: batch limits, partial failure handling, skip already-processed articles

3. **Layer 3 — Batch Orchestration**
   - ADF orchestrates nightly pipeline: ingestion → enrichment → gold aggregation → search refresh
   - Databricks computes gold outputs: sentiment trends, top entities, trending keywords
   - Key design: idempotent writes, Delta merge semantics, MLflow tracking model versions

4. **Layer 4 — Indexing**
   - Azure AI Search hybrid index with keyword fields and vector field
   - Uses BM25 + HNSW cosine similarity; optional semantic reranker
   - Key design: hybrid search benefits, HNSW tuning, ADLS as long-term storage

5. **Layer 5 — API Serving**
   - Azure Function exposes the search endpoint
   - Azure API Management handles rate limiting, response caching, OAuth validation
   - Key design: API versioning, cache behavior with near-real-time index refresh

6. **Layer 6 — Governance**
   - Purview scans storage, SQL, and Search assets
   - Builds lineage from raw JSON to Search index
   - Flags PII via entity recognition and custom classification
   - Key design: Purview lineage model, classification vs sensitivity labels

## What We Are Doing First
We are starting by setting up the repository structure and documentation.
This is the foundation so we can build each layer in sequence with clarity.

### Current Scope
- create project skeleton
- define layer responsibilities
- prepare the first implementation step for Layer 1

### Project Structure (added)

```
data/
   raw/          # Blob landing zone for raw NewsAPI JSON
   silver/       # Enriched articles (sentiment, entities, embeddings)
   gold/         # Aggregated analytics outputs
   metadata/     # Manifests, schemas, lineage helper files

logs/
   audit_log.csv
   ingestion.log
   enrichment.log

config/
   settings.py
   categories.json
   .env

tests/          # Basic pytest suites
docs/           # Architecture and decision docs
infrastructure/  # IaC templates and deployment scripts
```

## Next Step: Layer 1 Setup
We will now scaffold the ingestion layer:
- Create an Azure Function skeleton to poll NewsAPI
- Add deduplication logic with URL hashing
- Outline the Blob Storage landing zone layout
- Document the Logic App vs ADF HTTP decision

### Polling & Eventing Decisions

**Logic Apps vs ADF HTTP**

Logic Apps is preferred for NewsAPI polling because ingestion is schedule-based API retrieval rather than a complex ETL workflow. Logic Apps offers simple scheduling, low-code connectors, and straightforward retries for HTTP calls.

**Event Grid vs Event Hub**

Event Grid is chosen for file-arrival notifications because the workload is discrete file events (landing JSON batches) rather than a high-throughput streaming scenario. Event Grid integrates well with Functions and serverless patterns.

## How to Run
This repository is currently scaffolded and not yet deployed.
Once we implement each layer, we will add setup instructions and sample Azure deployment guidance.

## Files and Directories
- `src/ingestion/` — ingestion Azure Function and scripts
- `src/enrichment/` — NLP and embeddings enrichment code
- `src/orchestration/` — pipeline orchestration and analytics code
- `src/indexing/` — Azure Search schema and index code
- `src/api/` — API serving function
- `src/governance/` — Purview guidance and governance helpers
- `infrastructure/` — deployment templates and environment configuration
