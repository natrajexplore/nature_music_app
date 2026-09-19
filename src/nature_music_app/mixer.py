"""Render composed events to a stereo WAV with reverb."""

import io
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

from . import sounds
from .composer import MOODS, compose
from .ragas import SCALES
from .sounds import SR

TONAL = {"bird": sounds.bird, "droplet": sounds.droplet, "cricket": sounds.cricket}
PERCUSSIVE = {"rain": sounds.rain_tick, "fire": sounds.fire_crackle, "thunder": sounds.thunder}


def _place(buf: np.ndarray, sample: np.ndarray, t: float, gain: float, pan: float) -> None:
    i = int(t * SR)
    if i >= buf.shape[0]:
        return
    n = min(sample.size, buf.shape[0] - i)
    left = np.cos((pan + 1) * np.pi / 4)  # equal-power panning
    right = np.sin((pan + 1) * np.pi / 4)
    buf[i : i + n, 0] += sample[:n] * gain * left
    buf[i : i + n, 1] += sample[:n] * gain * right


def _reverb(buf: np.ndarray, rng: np.random.Generator, mix: float = 0.3) -> np.ndarray:
    n = int(2.2 * SR)
    decay = np.exp(-np.arange(n) / (0.6 * SR))
    out = np.empty_like(buf)
    for ch in range(2):
        ir = rng.standard_normal(n) * decay
        ir /= np.sqrt(np.sum(ir**2))
        wet = fftconvolve(buf[:, ch], ir)[: buf.shape[0]]
        out[:, ch] = buf[:, ch] * (1 - mix) + wet * mix
    return out


def _ramp(n: int, start_s: float, fade_s: float = 2.0) -> np.ndarray:
    """0 before `start_s`, then a linear fade-in to 1."""
    t = np.arange(n) / SR
    return np.clip((t - start_s) / fade_s, 0, 1) if start_s > 0 else np.ones(n)


def render(mood_key: str, scale: str | None, bpm: int | None, duration: float,
           seed: int, layers: list[str] | None = None,
           template: str = "free") -> tuple[np.ndarray, dict]:
    mood = MOODS[mood_key]
    scale = scale or mood.scale
    bpm = bpm or mood.bpm
    if layers is not None:
        mood = type(mood)(**{**mood.__dict__, "layers": layers})
    rng = np.random.default_rng(seed)

    piece = compose(mood, scale, bpm, duration, rng, template)
    bar = piece.bar
    total = len(piece.chords) * bar + 3.0  # tail for reverb
    buf = np.zeros((int(total * SR), 2))
    active = set(mood.layers)

    for e in piece.events:
        if e.inst in TONAL:
            s = TONAL[e.inst](e.freq, rng, e.dur)
        else:
            s = PERCUSSIVE[e.inst](rng)
        _place(buf, s, e.t, e.gain, e.pan)

    # Continuous beds and the chord-following wind pad.
    if "river" in active:
        river = sounds.river_bed(total, mood.tonic / 2, rng)
        buf += (river * _ramp(river.size, piece.entry["river"]))[:, None] * 0.22
    if "rain" in active:
        rain = sounds.rain_bed(total, rng)
        buf += (rain * _ramp(rain.size, piece.entry["rain"]))[:, None] * 0.12
    if "wind" in active:
        for b, chord in enumerate(piece.chords):
            if b * bar >= piece.entry["wind"]:
                pad = sounds.wind_pad(bar * 1.5, chord, rng)
                _place(buf, pad, b * bar, 0.35, rng.uniform(-0.3, 0.3))

    buf = _reverb(buf, rng)
    buf /= max(np.max(np.abs(buf)), 1e-9) / 0.9
    meta = {"mood": mood_key, "scale": scale, "bpm": bpm, "seed": seed, "template": template,
            "duration": round(buf.shape[0] / SR, 1), "layers": sorted(active),
            "progression": piece.prog[:4]}
    return buf, meta


def preview_scale(scale_key: str, instrument: str = "droplet") -> bytes:
    """Play a scale up then down so a beginner can hear the raga. Returns WAV bytes."""
    rng = np.random.default_rng(0)
    base = 440.0 if instrument == "bird" else 220.0
    semis = SCALES[scale_key] + [12]
    seq = semis + semis[-2::-1]
    step = 0.5
    buf = np.zeros((int((len(seq) * step + 2.5) * SR), 2))
    for i, semi in enumerate(seq):
        s = TONAL[instrument](base * 2 ** (semi / 12), rng, 0.7 if instrument == "droplet" else 0.5)
        _place(buf, s, i * step, 0.7, 0.0)
    buf = _reverb(buf, rng, 0.2)
    buf /= max(np.max(np.abs(buf)), 1e-9) / 0.9
    out = io.BytesIO()
    wavfile.write(out, SR, (buf * 32767).astype(np.int16))
    return out.getvalue()


def save_wav(buf: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(path, SR, (buf * 32767).astype(np.int16))
