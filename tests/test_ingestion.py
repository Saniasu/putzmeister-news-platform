from src.ingestion.ingest_newsapi import hash_article_url


def test_hash_length():
    h = hash_article_url("https://example.com/test")
    assert isinstance(h, str)
    assert len(h) == 64
