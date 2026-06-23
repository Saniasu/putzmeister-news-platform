from fastapi import FastAPI, HTTPException
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from cachetools import TTLCache
from collections import defaultdict
from dotenv import load_dotenv
import os
import time

load_dotenv()

# -------------------------------------
# FastAPI App
# -------------------------------------

app = FastAPI(
    title="Putzmeister News Search API",
    version="1.0"
)

# -------------------------------------
# Azure Search Configuration
# -------------------------------------

SEARCH_ENDPOINT = "https://putzmeister-search.search.windows.net"
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
INDEX_NAME = "news-index"

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_API_KEY)
)

# -------------------------------------
# Caching
# Cache expires after 300 seconds (5 min)
# -------------------------------------

cache = TTLCache(maxsize=100, ttl=300)

# -------------------------------------
# Simple Rate Limiting
# Max 100 requests/minute/IP
# -------------------------------------

request_counts = defaultdict(list)


def check_rate_limit(client_ip: str):

    current_time = time.time()

    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if current_time - t < 60
    ]

    if len(request_counts[client_ip]) >= 100:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    request_counts[client_ip].append(current_time)


# -------------------------------------
# API Version 1
# -------------------------------------

@app.get("/api/v1/search")
def search_news(query: str):

    client_ip = "local-user"

    check_rate_limit(client_ip)

    if query in cache:
        return {
            "source": "cache",
            "results": cache[query]
        }

    results = search_client.search(
        search_text=query,
        top=5
    )

    articles = []

    for result in results:

        articles.append({
            "title": result.get("title"),
            "source": result.get("source_name"),
            "publishedAt": result.get("publishedAt"),
            "sentiment": result.get("sentiment_label")
        })

    cache[query] = articles

    return {
        "source": "azure-search",
        "results": articles
    }