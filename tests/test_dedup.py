from src.ingestion.ingest_newsapi import deduplicate_articles


def test_deduplicate_articles():
    articles = [
        {"url": "https://example.com/a", "title": "A"},
        {"url": "https://example.com/b", "title": "B"},
        {"url": "https://example.com/a", "title": "A duplicate"},
    ]
    deduped = deduplicate_articles(articles)
    assert len(deduped) == 2
    urls = {a['url'] for a in deduped}
    assert "https://example.com/a" in urls
    assert "https://example.com/b" in urls
