REG = {"name": "Asha", "email": "asha@example.com", "password": "secret123"}


def test_consent_default_grant_withdraw(client):
    assert client.get("/users/consent").status_code == 401
    client.post("/auth/register", json=REG)
    assert client.get("/users/consent").json() == {"media_retention": False, "model_training": False}

    client.put("/users/consent", json={"consent_type": "model_training", "granted": True})
    assert client.get("/users/consent").json()["model_training"] is True

    client.put("/users/consent", json={"consent_type": "model_training", "granted": False})
    assert client.get("/users/consent").json()["model_training"] is False
    assert client.put("/users/consent", json={"consent_type": "bogus", "granted": True}).status_code == 422
