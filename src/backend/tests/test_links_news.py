from app import link_service
from app.routers import news

REG = {"name": "Asha", "email": "asha@example.com", "password": "secret123"}


def test_extract_urls():
    text = "Shop: https://example.com/buy?x=1, also see bit.ly/abc and shop.example.com/sale. mail me a@b.com"
    urls = link_service.extract_urls(text)
    assert "https://example.com/buy?x=1" in urls
    assert "https://shop.example.com/sale" in urls
    assert not any("a@b.com" in u for u in urls)


def test_private_hosts_blocked():
    assert link_service.is_safe_host("127.0.0.1") is False
    assert link_service.is_safe_host("169.254.169.254") is False
    code, result, _ = link_service.check_url("http://localhost:8000/admin")
    assert result == "unreachable" and code is None
    assert link_service.check_url("ftp://example.com")[1] == "invalid"


def test_link_analyze_stores_and_isolates_users(client, monkeypatch):
    monkeypatch.setattr("app.routers.links.check_url", lambda u: (404, "broken", "Server returned HTTP 404"))
    client.post("/auth/register", json=REG)
    r = client.post("/links/analyze", json={"text": "visit https://example.com/gone"})
    assert r.status_code == 200
    item = r.json()[0]
    assert item["validation_result"] == "broken"
    assert len(client.get("/links/reports").json()) == 1
    assert client.get(f"/links/reports/{item['id']}").status_code == 200

    client.post("/auth/logout")
    client.post("/auth/register", json={**REG, "email": "other@example.com"})
    assert client.get(f"/links/reports/{item['id']}").status_code == 404
    assert client.get("/links/reports").json() == []


def test_link_analyze_requires_input(client):
    client.post("/auth/register", json=REG)
    assert client.post("/links/analyze", json={"text": "no links here"}).status_code == 422


def test_news_refresh_and_list(client, monkeypatch):
    class FakeParsed:
        feed = {"title": "Social Today"}
        entries = [
            {"title": "Instagram launches new feature", "link": "https://x.test/1", "summary": "<p>Hello</p>"},
            {"title": "Algorithm change hits reach", "link": "https://x.test/2", "summary": "x"},
        ]

    monkeypatch.setattr(news.feedparser, "parse", lambda url: FakeParsed())
    monkeypatch.setattr(news.settings, "news_feeds", ["https://feed.test/rss"])
    client.post("/auth/register", json=REG)
    assert client.post("/news/refresh").json() == {"added": 2}
    assert client.post("/news/refresh").json() == {"added": 0}  # deduplicated by URL

    client.post("/auth/logout")  # reading news is public
    items = client.get("/news").json()
    assert len(items) == 2
    assert {i["category"] for i in items} == {"features", "algorithm"}
    assert client.get("/news", params={"category": "algorithm"}).json()[0]["title"].startswith("Algorithm")
    assert client.get(f"/news/{items[0]['id']}").status_code == 200
    assert client.get("/news/999").status_code == 404
    assert client.get("/news/categories").status_code == 200
    assert len(client.get("/news/trending").json()) == 2
