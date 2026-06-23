
import os
import json
from collections import Counter
from spacy.lang.en.stop_words import STOP_WORDS

import pandas as pd
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

"""
Databricks Gold Layer Simulation

Local Implementation Notes:

- Gold CSV files are overwritten on each run.
  This simulates Delta Lake REPLACE WHERE semantics.

- Running the pipeline multiple times does not
  create duplicate records (idempotent writes).

- In production, Databricks Delta MERGE would
  be used for incremental upserts.

- MLflow would track:
    * NLP model versions
    * Embedding model versions
    * Experiment metrics
- This local implementation simulates Azure Databricks processing.
"""


def upload_to_blob(file_path, file_name, date_folder):
    """
    Upload Gold layer files to Azure Blob Storage
    """

    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )

        container_name = "gold-zone"

        blob_name = f"{date_folder}/{file_name}"

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


def load_silver_articles():
    """
    Load all articles from the latest Silver layer folder.
    """

    silver_root = os.path.join("data", "silver")

    if not os.path.exists(silver_root):
        print("Silver layer not found.")
        return []

    available_dates = sorted(os.listdir(silver_root))

    if not available_dates:
        print("No Silver data available.")
        return []

    latest_date = available_dates[-1]

    silver_path = os.path.join(
        silver_root,
        latest_date
    )

    print(f"Using Silver folder: {latest_date}")

    all_articles = []

    for file_name in os.listdir(silver_path):

        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(
            silver_path,
            file_name
        )

        with open(file_path, "r", encoding="utf-8") as file:

            articles = json.load(file)

            category = file_name.replace(".json", "")

            for article in articles:
                article["category"] = category

            all_articles.extend(articles)

    print(f"Loaded {len(all_articles)} enriched articles.")

    return all_articles


def generate_sentiment_summary(articles):
    """
    Generate average sentiment score by category.
    """

    if not articles:
        return

    today = sorted(
        os.listdir(
            os.path.join("data", "silver")
        )
    )[-1]

    gold_path = os.path.join(
        "data",
        "gold",
        today
    )

    os.makedirs(gold_path, exist_ok=True)

    rows = []

    for article in articles:

        rows.append({
            "date": today,
            "category": article.get("category"),
            "sentiment_score":
                article.get(
                    "sentiment_score",
                    0
                )
        })

    df = pd.DataFrame(rows)

    summary = (
        df.groupby(
            ["date", "category"]
        )["sentiment_score"]
        .mean()
        .reset_index()
    )

    summary.rename(
        columns={
            "sentiment_score":
            "average_sentiment_score"
        },
        inplace=True
    )

    output_file = os.path.join(
        gold_path,
        "gold_sentiment_summary.csv"
    )

    summary.to_csv(
        output_file,
        index=False
    )

    print(
        "Created:",
        output_file
    )

    upload_to_blob(
        output_file,
        "gold_sentiment_summary.csv",
        today
    )


def generate_top_entities(articles):
    """
    Generate top entities from all articles.
    """

    if not articles:
        return

    today = sorted(
        os.listdir(
            os.path.join("data", "silver")
        )
    )[-1]

    gold_path = os.path.join(
        "data",
        "gold",
        today
    )

    os.makedirs(gold_path, exist_ok=True)

    entity_counter = Counter()

    for article in articles:

        entities = article.get(
            "entities",
            []
        )

        for entity in entities:

            entity_text = entity.get(
                "text"
            )

            entity_label = entity.get(
                "label"
            )

            if entity_label in [
                "PERSON",
                "ORG",
                "GPE"
            ]:

                key = (
                    entity_text,
                    entity_label
                )

                entity_counter[key] += 1

    rows = []

    for (
        entity,
        label
    ), count in entity_counter.most_common(50):

        rows.append({
            "entity": entity,
            "label": label,
            "frequency": count
        })

    df = pd.DataFrame(rows)

    output_file = os.path.join(
        gold_path,
        "gold_top_entities.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        "Created:",
        output_file
    )

    upload_to_blob(
        output_file,
        "gold_top_entities.csv",
        today
    )


def generate_trending_keywords():
    """
    Generate trending keywords using
    the last 7 Silver batches.
    """

    silver_root = os.path.join(
        "data",
        "silver"
    )

    available_dates = sorted(
        os.listdir(silver_root)
    )

    latest_dates = available_dates[-7:]

    keyword_counter = Counter()

    for date_folder in latest_dates:

        folder_path = os.path.join(
            silver_root,
            date_folder
        )

        for file_name in os.listdir(folder_path):

            if not file_name.endswith(".json"):
                continue

            file_path = os.path.join(
                folder_path,
                file_name
            )

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                articles = json.load(file)

                for article in articles:

                    phrases = article.get(
                        "key_phrases",
                        []
                    )

                    for phrase in phrases:

                        phrase = phrase.lower().strip()

                        if (
                            phrase in STOP_WORDS
                            or len(phrase) < 3
                        ):
                            continue

                        keyword_counter[phrase] += 1

    rows = []

    for keyword, count in keyword_counter.most_common(50):

        rows.append({
            "keyword": keyword,
            "frequency": count
        })

    df = pd.DataFrame(rows)

    latest_date = available_dates[-1]

    gold_path = os.path.join(
        "data",
        "gold",
        latest_date
    )

    os.makedirs(
        gold_path,
        exist_ok=True
    )

    output_file = os.path.join(
        gold_path,
        "gold_trending_keywords.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        "Created:",
        output_file
    )

    upload_to_blob(
        output_file,
        "gold_trending_keywords.csv",
        latest_date
    )


if __name__ == "__main__":

    articles = load_silver_articles()

    print(
        f"Total articles loaded: {len(articles)}"
    )

    generate_sentiment_summary(
        articles
    )

    generate_top_entities(
        articles
    )

    generate_trending_keywords()

