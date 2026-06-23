# Governance and Purview

This folder contains guidance for Purview scanning, classification, and lineage.

## Goals
- Scan Blob Storage landing and silver zones
- Scan the Search index metadata, if possible
- Track lineage from raw JSON ingestion through enrichment, gold analytics, and search
- Flag PII and sensitive data from named entities

## Notes
- Use Purview classification rules for PII detection, not only sensitivity labels.
- ADF lineage is created from pipeline datasets and activities.
- Databricks lineage is created from notebook activity metadata and Delta table operations.
- Use the Purview REST API if you need to export lineage or automate asset registration.
