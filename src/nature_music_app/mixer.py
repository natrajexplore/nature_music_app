"""Render composed events to a stereo WAV with reverb."""

import io
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

from . import sounds
from .composer import MOODS, Piece, compose
from .ragas import RAGAS, SCALES, phrase_semitones
from .sounds import SR
from .theory import SARGAM, chord_info, freq_to_key, freq_to_midi, key_to_freq, western_name

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
           seed: int, layers: list[str] | None = None, template: str = "free", *,
           key: str | None = None, tala: str | None = None, progression: str | None = None,
           volumes: dict[str, float] | None = None, reverb: float = 0.3,
           humanize: float = 0.3, swing: float = 0.0) -> tuple[np.ndarray, dict, Piece]:
    mood = MOODS[mood_key]
    scale = scale or mood.scale
    bpm = bpm or mood.bpm
    tala = tala or mood.tala
    changes = {}
    if layers is not None:
        changes["layers"] = layers
    if key is not None:
        changes["tonic"] = key_to_freq(key)
    if changes:
        mood = replace(mood, **changes)
    key = freq_to_key(mood.tonic)
    vol = {l: 1.0 for l in mood.layers} | (volumes or {})
    rng = np.random.default_rng(seed)

    piece = compose(mood, scale, bpm, duration, rng, template, tala, progression, humanize, swing)
    bar = piece.bar
    total = len(piece.chords) * bar + 3.0  # tail for reverb
    buf = np.zeros((int(total * SR), 2))
    active = set(mood.layers)

    for e in piece.events:
        if e.inst in TONAL:
            s = TONAL[e.inst](e.freq, rng, e.dur)
        elif e.inst == "log":
            s = sounds.log_drum(e.freq, rng, e.kind)
        else:
            s = PERCUSSIVE[e.inst](rng)
        _place(buf, s, e.t, e.gain * vol[e.inst], e.pan)

    # Continuous beds and the chord-following wind pad.
    if "river" in active:
        river = sounds.river_bed(total, mood.tonic / 2, rng)
        buf += (river * _ramp(river.size, piece.entry["river"]))[:, None] * 0.22 * vol["river"]
    if "rain" in active:
        rain = sounds.rain_bed(total, rng)
        buf += (rain * _ramp(rain.size, piece.entry["rain"]))[:, None] * 0.12 * vol["rain"]
    if "wind" in active:
        for b, chord in enumerate(piece.chords):
            if b * bar >= piece.entry["wind"]:
                pad = sounds.wind_pad(bar * 1.5, chord, rng)
                _place(buf, pad, b * bar, 0.35 * vol["wind"], rng.uniform(-0.3, 0.3))

    buf = _reverb(buf, rng, reverb)
    fade = min(2.5, total / 4)
    buf[-int(fade * SR):] *= np.linspace(1, 0, int(fade * SR))[:, None]
    buf /= max(np.max(np.abs(buf)), 1e-9) / 0.9

    meta = {"mood": mood_key, "scale": scale, "bpm": bpm, "seed": seed, "template": template,
            "key": key, "tala": tala, "progression": piece.prog[:4],
            "duration": round(buf.shape[0] / SR, 1), "layers": sorted(active),
            "bar_seconds": round(bar, 4), "step_seconds": round(piece.step, 4),
            "reverb": reverb, "humanize": humanize, "swing": swing,
            "volumes": {l: vol[l] for l in sorted(active)},
            **_score(piece, key)}
    return buf, meta, piece


def _score(piece: Piece, key: str) -> dict:
    """Notation for learners: per-bar chords and melody in sargam and Western names."""
    bars = []
    for b, (semis, mel) in enumerate(zip(piece.chord_semis, piece.melody)):
        sec = next(s["name"] for s in piece.sections if s["start"] <= b < s["end"])
        bars.append({
            "bar": b + 1, "section": sec, "chord": chord_info(key, semis),
            "melody": [{"step": st, "sargam": SARGAM[semi % 12],
                        "octave": semi // 12, "western": western_name(key, semi)}
                       for st, semi in mel],
        })
    base = round(freq_to_midi(piece.tonic))
    notes = [{"i": e.inst, "t": round(e.t, 3), "d": round(e.dur, 3),
              "m": round(freq_to_midi(e.freq))}
             for e in piece.events if e.inst in ("bird", "droplet")]
    sections = [{**s, "t": round(s["start"] * piece.bar, 2)} for s in piece.sections]
    return {"score": bars, "notes": notes, "sections": sections, "sa_midi": base}


def preview_phrase(scale_key: str, instrument: str = "droplet", phrase: str = "scale",
                   key: str = "C") -> bytes:
    """Play a raga phrase so a learner can hear it. Returns WAV bytes.

    phrase: "scale" (up then down), "aroha", "avaroha" or "pakad".
    """
    rng = np.random.default_rng(0)
    raga = RAGAS[scale_key]
    if phrase == "scale":
        semis = SCALES[scale_key] + [12]
        seq = semis + semis[-2::-1]
    else:
        seq = phrase_semitones(raga[phrase])
    base = key_to_freq(key) * (2 if instrument == "bird" else 1)
    step = 0.5 if phrase != "pakad" else 0.42
    buf = np.zeros((int((len(seq) * step + 2.5) * SR), 2))
    for i, semi in enumerate(seq):
        s = TONAL[instrument](base * 2 ** (semi / 12), rng, 0.7 if instrument == "droplet" else 0.5)
        _place(buf, s, i * step, 0.7, 0.0)
    buf = _reverb(buf, rng, 0.2)
    buf /= max(np.max(np.abs(buf)), 1e-9) / 0.9
    return to_wav_bytes(buf)


def to_wav_bytes(buf: np.ndarray) -> bytes:
    out = io.BytesIO()
    wavfile.write(out, SR, (buf * 32767).astype(np.int16))
    return out.getvalue()


def save_wav(buf: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(path, SR, (buf * 32767).astype(np.int16))
