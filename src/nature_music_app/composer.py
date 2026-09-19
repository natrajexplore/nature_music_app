"""Rule-based composer: mood + raga + template -> per-instrument note events."""

from dataclasses import dataclass, field

import numpy as np

from .ragas import SCALES

# Chord roots as scale-degree indices, one per bar.
PROGRESSIONS = [[0, 3, 4, 0], [0, 5, 3, 4], [0, 2, 3, 0], [0, 4, 5, 3]]

RISING_ORDER = ["river", "wind", "droplet", "cricket", "bird", "rain", "fire", "thunder"]
ALAP_ENTRY = {"river": 0, "wind": 0, "bird": 0.25, "cricket": 0.25, "droplet": 0.4,
              "thunder": 0.5, "rain": 0.6, "fire": 0.6}
RHYTHM_ENTRY = {"rain": 0, "fire": 0, "thunder": 0, "bird": 0.3, "droplet": 0.3,
                "cricket": 0.3, "river": 0.5, "wind": 0.5}
RHYTHM_ACCENTS = {0, 3, 6}  # 3 + 3 + 2


@dataclass
class Mood:
    label: str
    scale: str
    bpm: int
    tonic: float
    layers: list[str] = field(default_factory=list)
    density: float = 0.6  # melody note probability per 8th note


MOODS: dict[str, Mood] = {
    "dawn": Mood("Dawn Chorus", "bhupali", 76, 220.0,
                 ["bird", "droplet", "river", "wind"], 0.65),
    "storm": Mood("Monsoon Storm", "bhairavi", 96, 196.0,
                  ["droplet", "rain", "thunder", "wind", "fire"], 0.5),
    "night": Mood("Calm Night", "yaman", 60, 233.08,
                  ["cricket", "droplet", "river", "wind"], 0.45),
    "campfire": Mood("Campfire", "minor", 84, 220.0,
                     ["fire", "cricket", "droplet", "wind", "bird"], 0.55),
}


@dataclass
class Event:
    inst: str
    t: float  # seconds
    freq: float
    dur: float
    gain: float
    pan: float  # -1 left .. 1 right


@dataclass
class Piece:
    events: list[Event]
    chords: list[list[float]]  # chord tone frequencies per bar
    prog: list[int]  # chord root scale degree per bar
    bar: float  # bar length in seconds
    entry: dict[str, float]  # second at which each layer enters


def degree_freq(tonic: float, scale: list[int], idx: int) -> float:
    octave, step = divmod(idx, len(scale))
    return tonic * 2 ** ((scale[step] + 12 * octave) / 12)


def _entry_bars(template: str, layers: list[str], n_bars: int) -> dict[str, int]:
    if template == "alap":
        return {l: round(ALAP_ENTRY.get(l, 0.5) * n_bars) for l in layers}
    if template == "rhythm_first":
        return {l: round(RHYTHM_ENTRY.get(l, 0.5) * n_bars) for l in layers}
    if template == "rising_story":
        ordered = [l for l in RISING_ORDER if l in layers]
        k = len(ordered)
        return {l: int(i / k * 0.7 * n_bars) for i, l in enumerate(ordered)}
    return {l: 0 for l in layers}


def _walk(idx: int, chord_idx: list[int], strong: bool, n: int, rng) -> int:
    if strong and rng.random() < 0.6:
        idx = int(rng.choice(chord_idx)) + n * 2
    else:
        idx += int(rng.choice([-2, -1, -1, 1, 1, 2]))
    return int(np.clip(idx, n, n * 3))


def _make_motif(n: int, rng) -> list[int | None]:
    idx, motif = n * 2, []
    for s in range(8):
        if s == 0 or rng.random() > 0.3:
            idx = int(np.clip(idx + int(rng.choice([-2, -1, 1, 1, 2])), n, n * 3))
            motif.append(idx)
        else:
            motif.append(None)
    motif[7] = n * 2  # end on Sa
    return motif


def compose(mood: Mood, scale_name: str, bpm: int, duration: float,
            rng: np.random.Generator, template: str = "free") -> Piece:
    scale = SCALES[scale_name]
    n = len(scale)
    beat = 60 / bpm
    bar = 4 * beat
    step = beat / 2  # 8th note
    n_bars = max(1, int(duration / bar))
    prog = [d % n for d in PROGRESSIONS[rng.integers(len(PROGRESSIONS))]]
    layers = mood.layers
    entry_bar = _entry_bars(template, layers, n_bars)
    tonic = mood.tonic
    motif = _make_motif(n, rng) if template == "theme_var" else None

    events: list[Event] = []
    chords: list[list[float]] = []
    bar_roots: list[int] = []
    melody_idx = n * 2

    for b in range(n_bars):
        root = prog[b % len(prog)]
        bar_roots.append(root)
        chord_idx = [root, root + 2, root + 4]
        chords.append([degree_freq(tonic, scale, i + n) for i in chord_idx])
        t0 = b * bar

        def on(inst: str) -> bool:
            return inst in layers and b >= entry_bar[inst]

        # Melody notes for this bar: (step, scale index, length in steps).
        notes: list[tuple[int, int, float]] = []
        if on("bird"):
            if template == "call_response":
                half = 4 * (b % 2)
                for s in range(half, half + 4):
                    if s == half + 3:  # call ends on the 3rd (open), response on the root (home)
                        melody_idx = chord_idx[1 if b % 2 == 0 else 0] + n * 2
                        notes.append((s, melody_idx, 2.5))
                    elif rng.random() < min(0.95, mood.density + 0.2):
                        melody_idx = _walk(melody_idx, chord_idx, s % 2 == 0, n, rng)
                        notes.append((s, melody_idx, 1.6))
            elif template == "theme_var":
                m = motif[:4] + motif[4:][::-1] if b % 4 == 3 else motif
                shift = 2 if b % 4 == 2 else 0
                for s, idx in enumerate(m):
                    if idx is not None:
                        notes.append((s, int(np.clip(idx + shift, n, n * 3)), 1.6))
            else:
                dens = mood.density - (0.25 if b % 4 == 3 else 0.0)
                if template == "alap":
                    dens *= min(1.0, 0.3 + (b - entry_bar["bird"]) / max(1, n_bars * 0.5))
                for s in range(8):
                    if template == "alap" and s % 2:
                        continue
                    if rng.random() < dens:
                        melody_idx = _walk(melody_idx, chord_idx, s % 2 == 0, n, rng)
                        notes.append((s, melody_idx, 3.0 if template == "alap" else 1.6))
        for s, idx, length in notes:
            events.append(Event("bird", t0 + s * step, degree_freq(tonic, scale, idx),
                                step * length, 0.55, rng.uniform(-0.6, 0.6)))

        for s in range(8):
            t = t0 + s * step
            strong = s % 2 == 0

            if on("droplet"):
                idx = chord_idx[s % 3] + n  # arpeggio, one octave up
                events.append(Event("droplet", t, degree_freq(tonic, scale, idx),
                                    0.7, 0.4 if strong else 0.25, rng.uniform(-0.8, 0.8)))

            if on("cricket") and s % 4 == 1 and rng.random() < 0.6:
                events.append(Event("cricket", t, 4200 + rng.uniform(-150, 150),
                                    0.5, 0.18, rng.uniform(-1, 1)))

            if on("rain"):
                if template == "rhythm_first":
                    gain = 0.5 if s in RHYTHM_ACCENTS else 0.08
                else:
                    gain = 0.35 if strong else 0.18
                events.append(Event("rain", t, 0, 0.06, gain, rng.uniform(-0.7, 0.7)))

            if on("fire") and rng.random() < (0.25 if strong else 0.5):
                events.append(Event("fire", t + rng.uniform(0, step), 0, 0.12,
                                    rng.uniform(0.3, 0.7), rng.uniform(-0.5, 0.5)))

        if on("thunder") and (b - entry_bar["thunder"]) % 4 == 0:
            events.append(Event("thunder", t0, 0, 3.5, 0.9, 0.0))

    entry = {l: entry_bar[l] * bar for l in layers}
    return Piece(events, chords, bar_roots, bar, entry)
