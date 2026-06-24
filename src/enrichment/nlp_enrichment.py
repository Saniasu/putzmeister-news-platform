
import os
import json
from datetime import datetime

import spacy
from sentence_transformers import SentenceTransformer
from azure.storage.blob import BlobServiceClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

# Load NLP models
nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

LANGUAGE_ENDPOINT = os.getenv("LANGUAGE_ENDPOINT")
LANGUAGE_API_KEY = os.getenv("LANGUAGE_API_KEY")

text_analytics_client = TextAnalyticsClient(
    endpoint=LANGUAGE_ENDPOINT,
    credential=AzureKeyCredential(LANGUAGE_API_KEY)
)


def analyze_sentiment(text):
    """
    Analyze sentiment using Azure AI Language Service
    """

    if not text:
        return 0.0, "Neutral"

    try:

        response = text_analytics_client.analyze_sentiment(
            [text]
        )[0]

        sentiment_label = response.sentiment.capitalize()

        confidence_scores = response.confidence_scores

        sentiment_score = max(
            confidence_scores.positive,
            confidence_scores.neutral,
            confidence_scores.negative
        )

        return round(sentiment_score, 3), sentiment_label

    except Exception as e:

        print(f"Sentiment analysis failed: {e}")

        return 0.0, "Neutral"


def extract_entities(text):
    """
    Extract named entities using Azure AI Language Service
    """

    if not text:
        return []

    try:

        response = text_analytics_client.recognize_entities(
            [text]
        )[0]

        entities = []

        for entity in response.entities:

            entities.append({
                "text": entity.text,
                "label": entity.category
            })

        return entities

    except Exception as e:

        print(f"Entity extraction failed: {e}")

        return []


def detect_pii(entities):
    """
    Detect PII entities from extracted entities
    """

    pii_labels = {
        "PERSON",
        "ORG",
        "GPE"
    }

    detected_pii = list(set([
        entity["label"]
        for entity in entities
        if entity["label"] in pii_labels
    ]))

    contains_pii = len(detected_pii) > 0

    return contains_pii, detected_pii


def extract_key_phrases(text):
    """
    Extract key phrases using Azure AI Language Service
    """

    if not text:
        return []

    try:

        response = text_analytics_client.extract_key_phrases(
            [text]
        )[0]

        return response.key_phrases

    except Exception as e:

        print(f"Key phrase extraction failed: {e}")

        return []


def generate_embedding(text):
    """
    Generate vector embedding
    """

    if not text:
        return []

    embedding = embedding_model.encode(text)

    return embedding.tolist()


def enrich_article(article):
    """
    Apply NLP enrichment to one article
    """

    text = " ".join([
        article.get("title") or "",
        article.get("description") or "",
        article.get("content") or ""
    ])

    sentiment_score, sentiment_label = analyze_sentiment(text)

    article["sentiment_score"] = sentiment_score
    article["sentiment_label"] = sentiment_label

    entities = extract_entities(text)

    article["entities"] = entities

    contains_pii, pii_entities = detect_pii(entities)

    article["contains_pii"] = contains_pii
    article["pii_entities"] = pii_entities

    article["key_phrases"] = extract_key_phrases(text)

    article["embedding"] = generate_embedding(text)

    return article


def upload_to_blob(file_path, file_name):
    """
    Upload enriched Silver layer file to Azure Blob Storage
    """

    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )

        container_name = "silver-zone"

        today = "2026-06-22"

        blob_name = f"{today}/{file_name}"

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
            f"Uploaded {file_name} to Azure Blob Storage"
        )

    except Exception as e:
        print(f"Blob upload failed: {e}")


def process_raw_files():
    """
    Process raw articles and write enriched articles
    to the silver layer.
    Already processed articles are skipped.
    """

    today = "2026-06-22"

    raw_path = os.path.join("data", "raw", today)

    silver_path = os.path.join("data", "silver", today)

    os.makedirs(silver_path, exist_ok=True)

    for file_name in os.listdir(raw_path):

        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(raw_path, file_name)

        with open(file_path, "r", encoding="utf-8") as file:
            articles = json.load(file)

        output_file = os.path.join(
            silver_path,
            file_name
        )

        enriched_articles = []

        existing_hashes = set()

        # Load existing enriched articles
        if os.path.exists(output_file):

            with open(output_file, "r", encoding="utf-8") as existing_file:

                existing_articles = json.load(existing_file)

                for article in existing_articles:
                    existing_hashes.add(
                        article.get("article_hash")
                    )

                enriched_articles.extend(existing_articles)

        new_count = 0
        skipped_count = 0

        for article in articles:

            article_hash = article.get("article_hash")

            # Skip already enriched articles
            if article_hash in existing_hashes:
                skipped_count += 1
                continue

            enriched_article = enrich_article(article)

            enriched_articles.append(enriched_article)

            new_count += 1

        with open(output_file, "w", encoding="utf-8") as file:

            json.dump(
                enriched_articles,
                file,
                indent=4
            )

        upload_to_blob(output_file, file_name)

        print(
            f"{file_name}: "
            f"New={new_count}, "
            f"Skipped={skipped_count}"
        )


if __name__ == "__main__":

    process_raw_files()

    print("\nLayer 2 enrichment completed successfully.")

