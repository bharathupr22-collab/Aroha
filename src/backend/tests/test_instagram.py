from urllib.parse import parse_qs, urlparse

from app.routers import instagram as ig

REG = {"name": "Asha", "email": "asha@example.com", "password": "secret123"}


class FakeResp:
    def __init__(self, data, status=200):
        self._d, self.status_code = data, status

    def json(self):
        return self._d


def fake_client(account_type="BUSINESS", followers=100):
    class C:
        def __init__(self, *a, **k): ...
        def __enter__(self): return self
        def __exit__(self, *a): return False

        def post(self, url, data=None):
            return FakeResp({"access_token": "short", "user_id": 42})

        def get(self, url, params=None):
            if url == ig.LONG_TOKEN_URL:
                return FakeResp({"access_token": "long-token", "expires_in": 5000000})
            fields = params["fields"]
            if "username" in fields:
                return FakeResp({"user_id": "42", "username": "asha_ig", "account_type": account_type})
            return FakeResp({"followers_count": followers, "media_count": 7})
    return C


def configure(monkeypatch):
    monkeypatch.setattr(ig.settings, "meta_app_id", "app")
    monkeypatch.setattr(ig.settings, "meta_app_secret", "secret")


def state_from(client):
    url = client.get("/instagram/connect").json()["authorize_url"]
    return parse_qs(urlparse(url).query)["state"][0], url


def test_not_configured(client, monkeypatch):
    # Temporarily hide the .env keys to test the 503 error
    monkeypatch.setattr(ig.settings, "meta_app_id", "")
    monkeypatch.setattr(ig.settings, "meta_app_secret", "")
    client.post("/auth/register", json=REG)
    assert client.get("/instagram/connect").status_code == 503
    assert client.get("/instagram/account").status_code in (404, 401)


def test_connect_sync_growth_disconnect(client, monkeypatch):
    configure(monkeypatch)
    client.post("/auth/register", json=REG)
    state, url = state_from(client)
    assert "instagram_business_manage_insights" in url

    monkeypatch.setattr(ig.httpx, "Client", fake_client())
    r = client.get("/instagram/callback", params={"code": "abc#_", "state": state})
    assert r.status_code == 200 and r.json()["username"] == "asha_ig"
    assert client.get("/instagram/account").json()["username"] == "asha_ig"

    assert client.post("/instagram/sync").status_code == 200
    assert client.get("/instagram/growth").json()["net_follower_change"] is None
    monkeypatch.setattr(ig.httpx, "Client", fake_client(followers=130))
    client.post("/instagram/sync")
    assert client.get("/instagram/growth").json()["net_follower_change"] == 30
    assert client.get("/instagram/analytics").json()["followers_count"]["value"] == 130

    assert client.post("/instagram/disconnect").status_code == 200
    assert client.get("/instagram/account").status_code == 404


def test_personal_account_rejected_and_bad_state(client, monkeypatch):
    configure(monkeypatch)
    client.post("/auth/register", json=REG)
    state, _ = state_from(client)
    monkeypatch.setattr(ig.httpx, "Client", fake_client(account_type="PERSONAL"))
    assert client.get("/instagram/callback", params={"code": "x", "state": state}).status_code == 422
    assert client.get("/instagram/callback", params={"code": "x", "state": "forged"}).status_code == 400
