REG = {"name": "Asha", "email": "Asha@Example.com", "password": "secret123"}


def test_register_login_me(client):
    r = client.post("/auth/register", json=REG)
    assert r.status_code == 201
    assert r.json()["email"] == "asha@example.com"
    assert "password" not in r.text
    assert client.get("/auth/me").json()["name"] == "Asha"  # cookie session set on register

    client.post("/auth/logout")
    assert client.get("/auth/me").status_code == 401

    r = client.post("/auth/login", json={"email": "asha@example.com", "password": "secret123"})
    assert r.status_code == 200
    assert client.get("/auth/me").status_code == 200


def test_duplicate_email_rejected(client):
    client.post("/auth/register", json=REG)
    assert client.post("/auth/register", json=REG).status_code == 409


def test_weak_password_and_bad_email(client):
    assert client.post("/auth/register", json={**REG, "password": "short"}).status_code == 422
    assert client.post("/auth/register", json={**REG, "password": "onlyletters"}).status_code == 422
    assert client.post("/auth/register", json={**REG, "email": "nope"}).status_code == 422


def test_wrong_password(client):
    client.post("/auth/register", json=REG)
    client.post("/auth/logout")
    r = client.post("/auth/login", json={"email": REG["email"], "password": "wrong-pass1"})
    assert r.status_code == 401


def test_forgot_password_does_not_reveal_accounts(client):
    a = client.post("/auth/forgot-password", json={"email": "x@example.com"}).json()
    client.post("/auth/register", json=REG)
    b = client.post("/auth/forgot-password", json={"email": REG["email"]}).json()
    assert a == b


def test_protected_routes_need_login(client):
    assert client.get("/users/profile").status_code == 401
    assert client.get("/links/reports").status_code == 401


def test_delete_account(client):
    client.post("/auth/register", json=REG)
    assert client.delete("/users/account").status_code == 204
    r = client.post("/auth/login", json={"email": REG["email"], "password": REG["password"]})
    assert r.status_code == 401
