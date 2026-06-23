import os
import json
from datetime import datetime

import requests
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

from dedup import (
    generate_url_hash,
    load_existing_hashes,
    save_hashes
)

from audit_logger import log_ingestion

# Load environment variables
load_dotenv(".env")

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)
if NEWSAPI_KEY:
    print("NewsAPI key loaded successfully.")
else:
    print("NewsAPI key not found.")
BASE_URL = "https://newsapi.org/v2/top-headlines"


def load_categories():
    with open("config/categories.json", "r") as file:
        return json.load(file)


def fetch_news(category):
    params = {
        "country": "us",
        "category": category,
        "pageSize": 100,
        "apiKey": NEWSAPI_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json().get("articles", [])

    print(f"Error fetching {category}: {response.status_code}")
    return []


def save_raw_data(category, articles):
    today = datetime.now().strftime("%Y-%m-%d")

    output_dir = os.path.join("data", "raw", today)
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(
        output_dir,
        f"{category}.json"
    )

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(articles, file, indent=4)

    print(f"Saved {category} news to {file_path}")
    upload_to_blob(file_path, category)

def upload_to_blob(file_path, category):
    """
    Upload raw JSON file to Azure Blob Storage
    """

    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )

        container_name = "raw-landing-zone"

        today = datetime.now().strftime("%Y-%m-%d")

        blob_name = f"{today}/{category}.json"

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )

        with open(file_path, "rb") as data:
            blob_client.upload_blob(
                data,
                overwrite=True
            )

        print(
            f"Uploaded {category}.json "
            f"to Azure Blob Storage"
        )

    except Exception as e:
        print(
            f"Blob upload failed: {e}"
        )


def main():

    categories = load_categories()

    existing_hashes = load_existing_hashes()

    total_batch_articles = 0
    total_new_articles = 0
    total_duplicates = 0

    for category in categories:

        print(f"\nFetching {category} news...")

        articles = fetch_news(category)

        total_articles = len(articles)

        new_articles = []
        duplicate_count = 0

        for article in articles:

            url = article.get("url")

            if not url:
                continue

            article_hash = generate_url_hash(url)

            if article_hash in existing_hashes:
                duplicate_count += 1
                continue

            existing_hashes.add(article_hash)
            article["article_hash"] = article_hash

            new_articles.append(article)

        save_raw_data(category, new_articles)

        log_ingestion(
            category=category,
            total_articles=total_articles,
            new_articles=len(new_articles),
            duplicate_articles=duplicate_count,
            status="SUCCESS"
        )

        total_batch_articles += total_articles
        total_new_articles += len(new_articles)
        total_duplicates += duplicate_count

    save_hashes(existing_hashes)

    metadata = {
        "execution_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "categories_processed": len(categories),
        "total_articles": total_batch_articles,
        "new_articles": total_new_articles,
        "duplicates": total_duplicates,
        "pipeline_status": "SUCCESS"
    }

    os.makedirs("data/metadata", exist_ok=True)

    with open(
        "data/metadata/ingestion_metadata.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(metadata, file, indent=4)

    print("Metadata file created successfully.")

    print("\nLayer 1 ingestion completed successfully.")

if __name__ == "__main__":
    main()
