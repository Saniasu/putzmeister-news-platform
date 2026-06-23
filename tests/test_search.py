from src.api.search_function import search_news


def test_search_scaffold():
    res = search_news({"query":"test"})
    assert "message" in res
    assert res["message"].startswith("This is a scaffold")
