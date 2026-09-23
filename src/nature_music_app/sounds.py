"""Procedural nature sounds. Each function returns a mono float array at SR."""

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100


def _t(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def _filt(x: np.ndarray, kind: str, freq, order: int = 2) -> np.ndarray:
    sos = butter(order, freq, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def _norm(x: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(x))
    return x / peak if peak > 0 else x


def bird(freq: float, rng: np.random.Generator, dur: float = 0.4) -> np.ndarray:
    """Bird chirp tuned to `freq`: FM glide with vibrato and optional trill."""
    t = _t(dur)
    glide = rng.uniform(-0.06, 0.08)
    vib = rng.uniform(20, 45)
    inst = freq * (1 + glide * t / dur + 0.02 * np.sin(2 * np.pi * vib * t))
    phase = 2 * np.pi * np.cumsum(inst) / SR
    x = np.sin(phase) + 0.3 * np.sin(2 * phase)
    if rng.random() < 0.4:
        x *= 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(18, 30) * t)
    env = np.minimum(t / 0.012, 1) * np.exp(-t / (dur * 0.35))
    return x * env


def droplet(freq: float, rng: np.random.Generator, dur: float = 0.7) -> np.ndarray:
    """Water drop: a bubble whose pitch rises into `freq`, like a pluck."""
    t = _t(dur)
    inst = freq * (0.75 + 0.25 * (1 - np.exp(-t / 0.03)))
    phase = 2 * np.pi * np.cumsum(inst) / SR
    env = np.minimum(t / 0.003, 1) * np.exp(-t / 0.18)
    return (np.sin(phase) + 0.15 * np.sin(3 * phase)) * env


def cricket(freq: float, rng: np.random.Generator, dur: float = 0.5) -> np.ndarray:
    """Cricket chirp: bursts of a high tone pulsed at ~40 Hz."""
    t = _t(dur)
    carrier = np.sin(2 * np.pi * freq * t)
    pulses = np.clip(np.sin(2 * np.pi * 40 * t), 0, None) ** 2
    gate = (np.mod(t, 0.16) < 0.09).astype(float)
    return carrier * pulses * gate * np.exp(-t / (dur * 0.8))


def rain_tick(rng: np.random.Generator, dur: float = 0.06) -> np.ndarray:
    """Short bright noise burst: rain-as-hi-hat."""
    t = _t(dur)
    x = _filt(rng.standard_normal(t.size), "highpass", 4000)
    return x * np.exp(-t / 0.012)


def fire_crackle(rng: np.random.Generator, dur: float = 0.12) -> np.ndarray:
    """Wood snap: a few sharp clicks through a mid band-pass."""
    t = _t(dur)
    x = np.zeros(t.size)
    for _ in range(rng.integers(2, 6)):
        i = rng.integers(0, t.size // 2)
        x[i : i + 30] += rng.standard_normal(min(30, t.size - i)) * rng.uniform(0.4, 1)
    x = _filt(x, "bandpass", [800, 5000])
    return _norm(x) * np.exp(-t / 0.04)


def thunder(rng: np.random.Generator, dur: float = 3.5) -> np.ndarray:
    """Low rumble: low-passed noise plus a sub sine that decays slowly."""
    t = _t(dur)
    rumble = _filt(rng.standard_normal(t.size), "lowpass", 140, 3)
    sub = np.sin(2 * np.pi * 42 * t * (1 - 0.15 * t / dur))
    env = np.minimum(t / 0.15, 1) * np.exp(-t / 1.2)
    return _norm(rumble * 3 + sub) * env


# Tabla bols mapped to strokes: (bass "bayan" stroke, treble "dayan" stroke).
BOLS = {
    "Dha": ("open", "ring"), "Dhi": ("open", "ring"), "Dhin": ("open", "long"),
    "Ge": ("bend", None), "Na": (None, "ring"), "Ta": (None, "ring"),
    "Tin": (None, "long"), "Tu": (None, "long"), "Ti": (None, "click"),
    "Ka": ("click", None), "Te": (None, "click"),
}


def log_drum(freq: float, rng: np.random.Generator, bol: str = "Dha") -> np.ndarray:
    """Hollow log drum playing a tabla bol: a low booming 'bayan' and a tuned 'dayan'.

    The treble stroke is tuned to `freq` (Sa) with tabla-like harmonic overtones.
    """
    t = _t(0.9)
    bass, treble = BOLS.get(bol, ("open", "ring"))
    x = np.zeros(t.size)
    if bass in ("open", "bend"):
        f0 = 95 * (1 + 0.35 * np.exp(-t / 0.03))
        if bass == "bend":
            f0 = f0 * (1 + 0.25 * (1 - np.exp(-t / 0.12)))
        x += 0.9 * np.sin(2 * np.pi * np.cumsum(f0) / SR) * np.exp(-t / 0.28)
    elif bass == "click":
        x += 0.5 * _filt(rng.standard_normal(t.size), "bandpass", [150, 900]) * np.exp(-t / 0.015)
    if treble in ("ring", "long"):
        decay = 0.35 if treble == "long" else 0.18
        tone = sum(a * np.sin(2 * np.pi * freq * h * t) for h, a in ((1, 1), (2, 0.5), (3, 0.3), (4, 0.15)))
        x += 0.6 * tone * np.exp(-t / decay)
        x += 0.3 * _filt(rng.standard_normal(t.size), "highpass", 2000) * np.exp(-t / 0.004)
    elif treble == "click":
        x += 0.5 * _filt(rng.standard_normal(t.size), "bandpass", [1500, 6000]) * np.exp(-t / 0.012)
    return _norm(x) * np.minimum(t / 0.002, 1)


def rain_bed(dur: float, rng: np.random.Generator) -> np.ndarray:
    """Continuous rain wash."""
    n = int(dur * SR)
    x = _filt(rng.standard_normal(n), "bandpass", [2500, 9000])
    return _norm(x) * 0.5


def river_bed(dur: float, tonic: float, rng: np.random.Generator) -> np.ndarray:
    """River: flowing noise with a slow swell, plus a tuned drone on `tonic`."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    flow = _filt(rng.standard_normal(n), "bandpass", [200, 1800])
    flow *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * t + rng.uniform(0, 6))
    drone = _filt(rng.standard_normal(n), "bandpass", [tonic * 0.985, tonic * 1.015], 3)
    return _norm(flow) * 0.5 + _norm(drone) * 0.8


def wind_pad(dur: float, freqs: list[float], rng: np.random.Generator) -> np.ndarray:
    """Wind through the trees: noise resonating on each chord tone, with a swell."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        band = _filt(rng.standard_normal(n), "bandpass", [f * 0.99, f * 1.01], 3)
        out += _norm(band)
    env = np.sin(np.pi * t / dur) ** 2
    return _norm(out) * env
