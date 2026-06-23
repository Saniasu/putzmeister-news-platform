import os
import json
from datetime import datetime

import spacy
from textblob import TextBlob
from sentence_transformers import SentenceTransformer

# Load NLP models
nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def analyze_sentiment(text):
    """
    Analyze sentiment using TextBlob
    """

    if not text:
        return 0.0, "Neutral"

    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0:
        label = "Positive"
    elif polarity < 0:
        label = "Negative"
    else:
        label = "Neutral"

    return round(polarity, 3), label


def extract_entities(text):
    """
    Extract named entities using spaCy
    """

    if not text:
        return []

    doc = nlp(text)

    entities = []

    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    return entities


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
    Extract noun phrases as key phrases
    """

    if not text:
        return []

    doc = nlp(text)

    phrases = list(set(
        chunk.text.strip()
        for chunk in doc.noun_chunks
    ))

    return phrases


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

        print(
            f"{file_name}: "
            f"New={new_count}, "
            f"Skipped={skipped_count}"
        )


if __name__ == "__main__":

    process_raw_files()

    print("\nLayer 2 enrichment completed successfully.")