import hashlib
import json
import os


HASH_FILE = "data/metadata/processed_hashes.json"


def generate_url_hash(url):
    """
    Generate SHA-256 hash for an article URL.
    """
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def load_existing_hashes():
    """
    Load previously processed article hashes.
    """

    if not os.path.exists(HASH_FILE):
        return set()

    with open(HASH_FILE, "r") as file:
        hashes = json.load(file)

    return set(hashes)


def save_hashes(hashes):
    """
    Save processed hashes to metadata storage.
    """

    os.makedirs("data/metadata", exist_ok=True)

    with open(HASH_FILE, "w") as file:
        json.dump(list(hashes), file, indent=4)