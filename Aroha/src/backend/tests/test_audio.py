import io
import wave

import numpy as np

REG = {"name": "Asha", "email": "asha@example.com", "password": "secret123"}
RATE = 8000


def wav(samples: np.ndarray) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((np.clip(samples, -1, 1) * 32767).astype(np.int16).tobytes())
    return buf.getvalue()


def music(seed: int, seconds=6) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(RATE * seconds) / RATE
    out = np.zeros_like(t)
    for k in range(0, seconds * 4):  # a sequence of random notes
        f = rng.uniform(200, 3000)
        m = (t >= k / 4) & (t < (k + 1) / 4)
        out[m] = 0.4 * np.sin(2 * np.pi * f * t[m]) + 0.2 * np.sin(2 * np.pi * 2 * f * t[m])
    return out


def post(client, path, audio, **form):
    return client.post(path, files={"file": ("a.wav", wav(audio), "audio/wav")}, data=form)


def test_intact_missing_replaced(client):
    client.post("/auth/register", json=REG)
    ref = music(1)
    rid = post(client, "/audio/upload-reference", ref).json()["reference_id"]

    same = post(client, "/audio/analyze", ref, reference_id=rid).json()
    assert same["status"] == "intact"

    noisy = ref + np.random.default_rng(0).normal(0, 0.01, len(ref))
    assert post(client, "/audio/analyze", noisy, reference_id=rid).json()["status"] == "intact"

    assert post(client, "/audio/analyze", np.zeros(len(ref)), reference_id=rid).json()["status"] == "missing"
    assert post(client, "/audio/analyze", music(2), reference_id=rid).json()["status"] in ("replaced", "changed")

    half = ref.copy()
    half[len(half) // 2:] = 0
    assert post(client, "/audio/analyze", half, reference_id=rid).json()["status"] == "partially_silent"

    assert len(client.get("/audio/history").json()) == 5


def test_validation_and_access(client):
    assert client.get("/audio/history").status_code == 401
    client.post("/auth/register", json=REG)
    r = client.post("/audio/upload-reference", files={"file": ("a.wav", b"not a wav", "audio/wav")})
    assert r.status_code == 422
    assert post(client, "/audio/analyze", music(1), reference_id=999).status_code == 404
    assert client.get("/audio/report/12345").status_code == 404
