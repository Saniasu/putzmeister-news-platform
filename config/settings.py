import os

NEWSAPI_PAGE_SIZE = int(os.getenv("NEWSAPI_PAGE_SIZE", "100"))
NEWSAPI_CATEGORIES = "categories.json"
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT", "")
AZURE_CONTAINER = os.getenv("AZURE_CONTAINER", "news-landing")
DATA_RAW_PATH = "data/raw"
DATA_SILVER_PATH = "data/silver"
DATA_GOLD_PATH = "data/gold"

# Dedup
URL_HASH_FIELD = "url_hash"

# Embedding model size note
EMBEDDING_SIZE = 1536
