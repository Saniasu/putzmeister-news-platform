import subprocess
import sys

def run_ingestion():
    print("\nStarting Layer 1 - Ingestion")
    subprocess.run(
        [sys.executable, "src/ingestion/ingest_newsapi.py"],
        check=True
    )


def run_enrichment():
    print("\nStarting Layer 2 - NLP Enrichment")
    subprocess.run(
        [sys.executable, "src/enrichment/nlp_enrichment.py"],
        check=True
    )


def run_gold_aggregation():
    print("\nStarting Layer 3 - Gold Aggregation")
    subprocess.run(
        [sys.executable, "src/orchestration/databricks_gold.py"],
        check=True
    )


def refresh_search_index():
    print("\nRefreshing Search Index")
    print("Search index refresh simulated.")


if __name__ == "__main__":

    print("\nADF Nightly Pipeline Started")

    run_ingestion()

    run_enrichment()

    run_gold_aggregation()

    refresh_search_index()

    print("\nADF Nightly Pipeline Completed Successfully")