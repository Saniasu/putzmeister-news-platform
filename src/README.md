# Source Overview

This directory contains the code for the six pipeline layers.

- `src/ingestion/` — NewsAPI ingestion and raw blob landing.
- `src/enrichment/` — NLP and embedding enrichment scaffolds.
- `src/orchestration/` — Data engineering and trend analytics logic.
- `src/indexing/` — Azure AI Search index schema definition.
- `src/api/` — Search API function scaffold.
- `src/governance/` — Purview and governance guidance.

## Working plan
1. Implement ingestion layer code and local Azure Function template.
2. Add enrichment logic with Azure Language and OpenAI APIs.
3. Define ADF/Databricks orchestration for the gold layer.
4. Define Search index and API serving path.
5. Add governance and Purview configuration.
