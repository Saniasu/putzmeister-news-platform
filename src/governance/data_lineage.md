# Data Lineage and Governance

## Overview

The Putzmeister News Platform implements end-to-end data lineage from ingestion through API serving. Data lineage provides visibility into how data flows, transforms, and is consumed across the platform.

---

## End-to-End Data Lineage

```text
NewsAPI
   ↓
Raw Layer (JSON files)
   ↓
Deduplication & Validation
   ↓
Silver Layer (NLP Enrichment)
   ↓
Gold Layer (Analytics Aggregation)
   ↓
Azure AI Search Index
   ↓
FastAPI / Render API
   ↓
End Users
```

---

## Layer Description

### 1. Raw Layer

* Source: NewsAPI
* Storage: JSON files in `data/raw/`
* Purpose: Preserve original articles without modification.

### 2. Silver Layer

* NLP enrichment applied:

  * Sentiment Analysis
  * Named Entity Recognition
  * Key Phrase Extraction
  * Embedding Generation
  * PII Detection

* Storage: `data/silver/`

### 3. Gold Layer

* Aggregated analytical datasets:

  * Sentiment Summary
  * Trending Keywords
  * Top Entities

* Storage: `data/gold/`

### 4. Azure AI Search Layer

Enriched articles are indexed into Azure AI Search to support semantic search and retrieval.

Index:

`news-index`

### 5. API Serving Layer

FastAPI retrieves indexed documents from Azure AI Search and exposes them through REST endpoints.

---

## Microsoft Purview Integration

Microsoft Purview can scan and catalog the following assets:

* Azure Blob Storage
* Azure AI Search Index
* Future SQL databases
* Data Lake Storage

Purview automatically discovers metadata and builds lineage graphs across connected assets.

---

## ADF Lineage vs Databricks Lineage

### Azure Data Factory (ADF) Lineage

* Tracks orchestration activities.
* Captures pipeline execution history.
* Shows dataset movement between services.
* Focuses on data movement.

Example:

```text
Blob Storage → Copy Activity → SQL Database
```

### Azure Databricks Lineage

* Tracks notebook transformations.
* Captures column-level transformations.
* Focuses on data processing logic.

Example:

```text
Raw Articles → NLP Transformation → Gold Dataset
```

---

## Classification vs Sensitivity Labels

### Classification

Classification identifies sensitive information.

Examples:

* PERSON
* EMAIL
* LOCATION
* ORGANIZATION

In this project, custom PII detection is implemented using SpaCy.

### Sensitivity Labels

Sensitivity labels define protection policies.

Examples:

* Public
* Internal
* Confidential
* Highly Confidential

Labels are typically enforced through Microsoft Purview and Microsoft Information Protection.

---

## Purview REST API

Microsoft Purview REST APIs can be used to:

* Export lineage graphs.
* Retrieve metadata catalogs.
* Access asset classifications.
* Integrate governance information into external systems.

Example Use Cases:

* Compliance reporting.
* Governance dashboards.
* Automated metadata auditing.

---

## Governance Features Implemented in this Project

### Implemented

* API Audit Logging
* PII Detection
* Metadata Enrichment
* Search Activity Tracking

### Future Azure Enhancements

* Microsoft Purview Integration
* Azure Monitor
* Application Insights
* Automated Lineage Visualization
* Sensitivity Label Enforcement

```
```
