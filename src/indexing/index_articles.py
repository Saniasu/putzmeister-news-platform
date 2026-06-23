import os
import json
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------
# Azure Search Configuration
# -------------------------------------

SEARCH_ENDPOINT = "https://putzmeister-search.search.windows.net"
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
INDEX_NAME = "news-index"

client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_API_KEY)
)


def prepare_document(article):
    """
    Convert enriched article to Azure Search document
    """

    entities = [
        entity.get("text", "")
        for entity in article.get("entities", [])
    ]

    return {
        "article_hash": article.get("article_hash"),
        "title": article.get("title"),
        "description": article.get("description"),
        "content": article.get("content"),
        "author": article.get("author"),
        "source_name": article.get("source", {}).get("name"),
        "publishedAt": article.get("publishedAt"),
        "sentiment_label": article.get("sentiment_label"),
        "sentiment_score": float(
            article.get("sentiment_score", 0)
        ),
        "key_phrases": article.get("key_phrases", []),
        "entities": entities,
        "embedding": article.get("embedding", [])
    }


def upload_silver_articles():

    silver_root = Path("data/silver")

    all_documents = []

    for date_folder in silver_root.iterdir():

        if not date_folder.is_dir():
            continue

        for json_file in date_folder.glob("*.json"):

            print(f"Processing {json_file}")

            with open(
                json_file,
                "r",
                encoding="utf-8"
            ) as file:

                articles = json.load(file)

            for article in articles:

                document = prepare_document(article)

                all_documents.append(document)

    print(
        f"\nUploading {len(all_documents)} documents..."
    )

    results = client.upload_documents(
        documents=all_documents
    )

    success_count = sum(
        1 for result in results
        if result.succeeded
    )

    print(
        f"Successfully indexed "
        f"{success_count} documents."
    )


if __name__ == "__main__":

    upload_silver_articles()