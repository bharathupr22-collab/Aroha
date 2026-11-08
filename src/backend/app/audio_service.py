"""Audio fingerprinting and loss detection (WAV input; other formats need FFmpeg conversion first)."""
import io
import wave

import numpy as np

SAMPLE_RATE = 8000
FRAME = 1024
HOP = 512
BANDS = 16
SILENCE_RMS = 0.005


def load_wav(data: bytes) -> np.ndarray:
    """Decode PCM WAV bytes to mono float32 at SAMPLE_RATE."""
    try:
        with wave.open(io.BytesIO(data)) as w:
            ch, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
            raw = w.readframes(n)
    except (wave.Error, EOFError) as exc:
        raise ValueError("Unsupported or corrupt WAV file") from exc
    if width not in (1, 2, 4):
        raise ValueError("Unsupported sample width")
    dtype = {1: np.uint8, 2: np.int16, 4: np.int32}[width]
    x = np.frombuffer(raw, dtype=dtype).astype(np.float32)
    x = (x - 128) / 128 if width == 1 else x / float(np.iinfo(dtype).max)
    if ch > 1:
        x = x[: len(x) - len(x) % ch].reshape(-1, ch).mean(axis=1)
    if rate != SAMPLE_RATE and len(x):
        idx = np.linspace(0, len(x) - 1, int(len(x) * SAMPLE_RATE / rate))
        x = np.interp(idx, np.arange(len(x)), x).astype(np.float32)
    return x


def fingerprint(x: np.ndarray) -> np.ndarray:
    """Per-frame boolean band-energy-rise pattern, shape (frames-1, BANDS-1)."""
    if len(x) < FRAME * 2:
        raise ValueError("Audio too short to fingerprint")
    window = np.hanning(FRAME)
    frames = np.stack([x[i:i + FRAME] * window for i in range(0, len(x) - FRAME, HOP)])
    spec = np.abs(np.fft.rfft(frames, axis=1)) ** 2
    edges = np.linspace(1, spec.shape[1], BANDS + 1).astype(int)
    energy = np.stack([spec[:, a:b].sum(axis=1) for a, b in zip(edges[:-1], edges[1:])], axis=1)
    # Floor relative to the loudest band so noise in near-empty bands cannot flip bits.
    energy = np.log(np.maximum(energy, energy.max() * 1e-3))
    d = np.diff(energy, axis=1)           # change across bands
    return np.diff(d, axis=0) > 0         # change of that pattern over time


def encode(fp: np.ndarray) -> str:
    return f"{fp.shape[0]}x{fp.shape[1]}:" + np.packbits(fp.flatten()).tobytes().hex()


def decode(s: str) -> np.ndarray:
    shape, hexdata = s.split(":", 1)
    r, c = map(int, shape.split("x"))
    bits = np.unpackbits(np.frombuffer(bytes.fromhex(hexdata), dtype=np.uint8))
    return bits[: r * c].reshape(r, c).astype(bool)


def similarity(ref: np.ndarray, test: np.ndarray) -> float:
    """Best bit-match ratio (0-1) of the shorter print slid over the longer one."""
    short, long_ = (ref, test) if len(ref) <= len(test) else (test, ref)
    n = len(short)
    best = 0.0
    step = max(1, n // 20)
    for off in range(0, len(long_) - n + 1, step):
        best = max(best, float((short == long_[off:off + n]).mean()))
    return best


def silent_ratio(x: np.ndarray) -> float:
    if len(x) < FRAME:
        return 1.0
    n = len(x) // FRAME
    rms = np.sqrt((x[: n * FRAME].reshape(n, FRAME) ** 2).mean(axis=1))
    return float((rms < SILENCE_RMS).mean())


def analyse(reference_fp: str | None, test_wav: bytes) -> tuple[str, float, dict]:
    """Return (status, similarity, details). status: missing|partially_silent|replaced|changed|intact."""
    x = load_wav(test_wav)
    silent = silent_ratio(x)
    if len(x) == 0 or silent >= 0.98:
        return "missing", 0.0, {"silent_ratio": round(silent, 3)}
    details = {"silent_ratio": round(silent, 3), "duration_s": round(len(x) / SAMPLE_RATE, 2)}
    if reference_fp is None:
        return ("partially_silent" if silent > 0.2 else "intact"), 1.0, details
    sim = similarity(decode(reference_fp), fingerprint(x))
    details["similarity"] = round(sim, 3)
    if silent > 0.2:
        return "partially_silent", sim, details
    if sim >= 0.85:
        return "intact", sim, details
    if sim >= 0.65:
        return "changed", sim, details
    return "replaced", sim, details
