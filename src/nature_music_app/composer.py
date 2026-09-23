"""Rule-based composer: mood + raga + template -> per-instrument note events."""

from dataclasses import dataclass, field

import numpy as np

from .ragas import RAGAS, SARGAM_SEMITONES, SCALES, phrase_semitones
from .talas import TALAS, khali_steps, vibhag_starts

# Chord roots as scale-degree indices, one per bar.
PROGRESSIONS: dict[str, dict] = {
    "home_journey": {"name": "Home Journey", "degrees": [0, 3, 4, 0],
                     "idea": "Leave home, travel, come back. The classic I-IV-V-I shape."},
    "gentle": {"name": "Gentle Wave", "degrees": [0, 5, 3, 4],
               "idea": "Dips into a softer chord before rising again (I-vi-IV-V in major)."},
    "folk": {"name": "Folk Circle", "degrees": [0, 2, 3, 0],
             "idea": "Small steps away from home, like a village song."},
    "anthem": {"name": "Anthem", "degrees": [0, 4, 5, 3],
               "idea": "The famous pop/film loop (I-V-vi-IV in major)."},
    "drone": {"name": "Drone (Raga Style)", "degrees": [0, 0, 0, 0],
              "idea": "Stay on Sa the whole time, the way Indian classical music does. All colour comes from the melody."},
}

RISING_ORDER = ["river", "wind", "droplet", "cricket", "bird", "rain", "fire", "thunder"]
ALAP_ENTRY = {"river": 0, "wind": 0, "bird": 0.25, "cricket": 0.25, "droplet": 0.4,
              "thunder": 0.5, "rain": 0.6, "fire": 0.6}
RHYTHM_ENTRY = {"rain": 0, "fire": 0, "thunder": 0, "bird": 0.3, "droplet": 0.3,
                "cricket": 0.3, "river": 0.5, "wind": 0.5}


@dataclass
class Mood:
    label: str
    scale: str
    bpm: int
    tonic: float
    layers: list[str] = field(default_factory=list)
    density: float = 0.6  # melody note probability per 8th note
    icon: str = "🎵"
    story: str = ""  # the real-life scenario, in plain words
    template: str = "free"  # suggested composing method
    tala: str = "keherwa"  # suggested rhythm cycle


MOODS: dict[str, Mood] = {
    "dawn": Mood(
        "Dawn Chorus", "bhupali", 76, 220.0, ["bird", "droplet", "river", "wind"], 0.65,
        icon="🌅", template="rising_story",
        story="First light. One bird starts singing, then the whole forest joins in."),
    "storm": Mood(
        "Monsoon Storm", "bhairavi", 96, 196.0,
        ["bird", "droplet", "rain", "thunder", "wind", "fire"], 0.5,
        icon="⛈️", template="rhythm_first",
        story="Dark clouds roll in. Rain hammers the roof and thunder shakes the sky."),
    "night": Mood(
        "Calm Night", "yaman", 60, 233.08, ["bird", "cricket", "droplet", "river", "wind"], 0.45,
        icon="🌙", template="alap", tala="rupak",
        story="A quiet evening. Crickets sing, a stream murmurs and the moon rises."),
    "campfire": Mood(
        "Campfire", "minor", 84, 220.0, ["fire", "cricket", "droplet", "wind", "bird", "log"], 0.55,
        icon="🔥", template="free", tala="dadra",
        story="Friends around a fire. Logs crackle and stories are told into the dark."),
    "morning_walk": Mood(
        "Morning Walk", "hamsadhwani", 88, 246.94, ["bird", "droplet", "wind", "river", "log"], 0.7,
        icon="🚶", template="call_response",
        story="You stroll through a park at 6 a.m. Birds call to each other along the path."),
    "rainy_window": Mood(
        "Rainy Day Indoors", "desh", 66, 220.0, ["bird", "rain", "droplet", "wind"], 0.4,
        icon="🌧️", template="alap", tala="dadra",
        story="You sit by the window with hot tea. Soft rain taps the glass and you feel nostalgic."),
    "riverside": Mood(
        "Riverside Meditation", "bhairav", 56, 196.0, ["river", "wind", "bird", "droplet"], 0.35,
        icon="🧘", template="raga_phrase", tala="teentaal",
        story="You sit on a river bank, breathe slowly and let your thoughts flow away."),
    "bedtime": Mood(
        "Bedtime Lullaby", "durga", 54, 261.63, ["bird", "cricket", "droplet", "wind", "river"], 0.35,
        icon="😴", template="theme_var", tala="dadra",
        story="The lights are off. A gentle repeating tune rocks you to sleep."),
    "festival": Mood(
        "Village Festival", "kafi", 108, 220.0, ["bird", "droplet", "rain", "fire", "log"], 0.75,
        icon="🎉", template="rhythm_first",
        story="Drums, lamps and dancing. The whole village celebrates till late night."),
    "forest_trek": Mood(
        "Forest Adventure", "major", 100, 261.63,
        ["bird", "droplet", "river", "wind", "thunder"], 0.65,
        icon="🥾", template="rising_story",
        story="You hike deeper into the jungle. Every turn reveals a new sound."),
    "missing_you": Mood(
        "Missing Someone", "bageshri", 58, 233.08, ["droplet", "wind", "rain", "river", "bird"], 0.4,
        icon="💔", template="call_response", tala="dadra",
        story="A long-distance longing. You ask a question into the night and hope for an answer."),
    "study_focus": Mood(
        "Study & Focus", "bhupali", 72, 261.63, ["droplet", "river", "bird", "log"], 0.35,
        icon="📚", template="raga_phrase", tala="teentaal",
        story="Deep work time. A calm repeating pattern keeps your mind steady."),
    "sunset": Mood(
        "Sunset by the Sea", "marwa", 68, 174.61, ["droplet", "wind", "river", "bird"], 0.45,
        icon="🌇", template="alap", tala="rupak",
        story="The sky turns orange and the day slowly lets go. Bittersweet and beautiful."),
    "riyaz": Mood(
        "Daily Riyaz (Practice)", "yaman", 80, 261.63, ["river", "bird", "log", "droplet"], 0.5,
        icon="🪷", template="raga_phrase", tala="teentaal",
        story="A musician's daily practice: a drone for Sa, a steady tabla cycle and the raga's signature phrase."),
}


@dataclass
class Event:
    inst: str
    t: float  # seconds
    freq: float
    dur: float
    gain: float
    pan: float  # -1 left .. 1 right
    kind: str = ""  # tabla bol for the log drum


@dataclass
class Piece:
    events: list[Event]
    chords: list[list[float]]  # chord tone frequencies per bar
    chord_semis: list[list[int]]  # chord tones as semitones above Sa per bar
    prog: list[int]  # chord root scale degree per bar
    bar: float  # bar (tala cycle) length in seconds
    step: float  # one matra in seconds
    entry: dict[str, float]  # second at which each layer enters
    sections: list[dict]  # song form
    melody: list[list[tuple[float, int]]]  # per bar: (step, semitones above the melody's Sa)
    tonic: float


def degree_semi(scale: list[int], idx: int) -> int:
    octave, step = divmod(idx, len(scale))
    return scale[step] + 12 * octave


def degree_freq(tonic: float, scale: list[int], idx: int) -> float:
    return tonic * 2 ** (degree_semi(scale, idx) / 12)


def chord_degrees(scale: list[int], root: int) -> list[int]:
    """Scale indices of a root-position chord on `root`, built from the raga's own notes.

    Prefers a 3rd (3-4 semitones) and a perfect 5th. Pentatonic ragas often lack
    one, so a 4th or 2nd stands in for the 3rd (a 'sus' chord) and the octave
    stands in for a missing 5th. The chord is always rooted on its degree, so the
    home chord always contains Sa as its lowest note.
    """
    n = len(scale)

    def find(interval: int) -> int:
        for k in range(1, n):
            if (degree_semi(scale, root + k) - scale[root]) % 12 == interval:
                return k
        return 0

    third, third_iv = next(((k, iv) for iv in (4, 3, 5, 2) if (k := find(iv))), (1, None))
    fifth = find(7)
    if not fifth and third_iv == 3:
        fifth = find(6)  # diminished
    if not fifth and third_iv == 4:
        fifth = find(8)  # augmented
    if not fifth or fifth <= third:
        fifth = n  # octave
    return [root, root + third, root + fifth]


def form(n_bars: int) -> list[dict]:
    """Split the piece into intro, theme, development, return and outro."""
    if n_bars < 5:
        return [{"name": "Theme", "start": 0, "end": n_bars, "energy": 0.85}]
    intro = max(1, n_bars // 8)
    outro = max(1, n_bars // 10)
    body = n_bars - intro - outro
    a = body // 3
    b = body // 3
    parts = [("Intro", intro, 0.55), ("Theme (A)", a, 0.8), ("Development (B)", b, 1.0),
             ("Return (A')", body - a - b, 0.9), ("Outro", outro, 0.5)]
    out, pos = [], 0
    for name, length, energy in parts:
        out.append({"name": name, "start": pos, "end": pos + length, "energy": energy})
        pos += length
    return out


def _entry_bars(template: str, layers: list[str], n_bars: int) -> dict[str, int]:
    if template == "alap":
        return {l: round(ALAP_ENTRY.get(l, 0.5) * n_bars) for l in layers}
    if template == "rhythm_first":
        return {l: round(RHYTHM_ENTRY.get(l, 0.5) * n_bars) for l in layers}
    if template == "rising_story":
        ordered = [l for l in RISING_ORDER if l in layers]
        ordered += [l for l in layers if l not in ordered]
        k = len(ordered)
        return {l: int(i / k * 0.7 * n_bars) for i, l in enumerate(ordered)}
    return {l: 0 for l in layers}


class Melody:
    """Moves through the raga while obeying its aroha (up) and avaroha (down) rules."""

    def __init__(self, raga_key: str, rng):
        raga = RAGAS[raga_key]
        self.scale = SCALES[raga_key]
        self.n = len(self.scale)
        self.rng = rng
        self.up = {s % 12 for s in phrase_semitones(raga["aroha"])}
        self.down = {s % 12 for s in phrase_semitones(raga["avaroha"])}
        self.vadi = SARGAM_SEMITONES[raga["vadi"]] if raga["vadi"] else None
        self.idx = self.n * 2
        self.lo, self.hi = self.n, self.n * 3

    def _legal(self, target: int, direction: int) -> int:
        allowed = self.up if direction > 0 else self.down
        for _ in range(self.n):
            if degree_semi(self.scale, target) % 12 in allowed or not self.lo < target < self.hi:
                break
            target += direction
        return int(np.clip(target, self.lo, self.hi))

    def move_to(self, target: int) -> int:
        target = int(np.clip(target, self.lo, self.hi))
        if target != self.idx:
            target = self._legal(target, 1 if target > self.idx else -1)
        self.idx = target
        return target

    def walk(self, chord_idx: list[int], strong: bool, register: int = 0) -> int:
        centre = self.n * 2 + register
        if strong and self.vadi is not None and self.rng.random() < 0.2:
            vadi_deg = self.scale.index(self.vadi)
            return self.move_to(centre - (centre % self.n) + vadi_deg)
        if strong and self.rng.random() < 0.6:
            return self.move_to(int(self.rng.choice(chord_idx)) + centre - (centre % self.n))
        step = int(self.rng.choice([-2, -1, -1, 1, 1, 2]))
        # Gently pull back toward the centre of the register.
        if abs(self.idx + step - centre) > self.n:
            step = -step
        return self.move_to(self.idx + step)


def _make_motif(n: int, steps: int, rng) -> list[int | None]:
    idx, motif = n * 2, []
    for s in range(steps):
        if s == 0 or rng.random() > 0.3:
            idx = int(np.clip(idx + int(rng.choice([-2, -1, 1, 1, 2])), n, n * 3))
            motif.append(idx)
        else:
            motif.append(None)
    motif[-1] = n * 2  # end on Sa
    return motif


def compose(mood: Mood, scale_name: str, bpm: int, duration: float,
            rng: np.random.Generator, template: str = "free", tala_key: str = "keherwa",
            progression: str | None = None, humanize: float = 0.3,
            swing: float = 0.0) -> Piece:
    scale = SCALES[scale_name]
    n = len(scale)
    tala = TALAS[tala_key]
    steps = tala["matras"]
    beat = 60 / bpm
    step = beat / 2  # one matra = an 8th note
    bar = steps * step
    n_bars = max(1, int(duration / bar))
    if progression is None:
        progression = list(PROGRESSIONS)[rng.integers(len(PROGRESSIONS) - 1)]  # not drone
    prog = [d % n for d in PROGRESSIONS[progression]["degrees"]]
    layers = mood.layers
    entry_bar = _entry_bars(template, layers, n_bars)
    tonic = mood.tonic
    motif = _make_motif(n, steps, rng) if template == "theme_var" else None
    pakad = phrase_semitones(RAGAS[scale_name]["pakad"])
    sections = form(n_bars)
    vib = set(vibhag_starts(tala))
    khali = khali_steps(tala)
    groove = set(tala["groove"])
    mel = Melody(scale_name, rng)

    events: list[Event] = []
    chords: list[list[float]] = []
    chord_semis: list[list[int]] = []
    bar_roots: list[int] = []
    melody: list[list[tuple[int, int]]] = []
    melody_carry: list[tuple[float, int, float]] = []

    def when(t: float, s: int) -> float:
        jitter = rng.normal(0, 0.006 * humanize) if humanize else 0.0
        return max(0.0, t + (swing * step * 0.33 if s % 2 else 0.0) + jitter)

    def vel(g: float) -> float:
        return g * (1 + rng.uniform(-0.2, 0.2) * humanize)

    for b in range(n_bars):
        last = b == n_bars - 1
        sec = next(x for x in sections if x["start"] <= b < x["end"])
        energy = sec["energy"]
        register = 2 if sec["name"].startswith("Development") else 0
        root = 0 if last else prog[b % len(prog)]
        bar_roots.append(root)
        chord_idx = chord_degrees(scale, root)
        chords.append([degree_freq(tonic, scale, i + n) for i in chord_idx])
        chord_semis.append([degree_semi(scale, i) for i in chord_idx])
        t0 = b * bar

        def on(inst: str) -> bool:
            return inst in layers and b >= entry_bar[inst]

        # Melody notes for this bar: (step, semitone above Sa, length in steps).
        notes: list[tuple[float, int, float]] = []
        if on("bird") and last:
            notes.append((0, 0, steps * 0.9))  # final cadence: land on Sa
            mel.idx = n * 2
        elif on("bird"):
            if template == "call_response":
                h = steps // 2
                start = h * (b % 2)
                for s in range(start, start + h):
                    if s == start + h - 1:  # call ends on the 3rd (open), response on the root (home)
                        target = chord_idx[1 if b % 2 == 0 else 0] + n * 2
                        notes.append((s, degree_semi(scale, mel.move_to(target)) - 12 * 2, 2.5))
                    elif rng.random() < min(0.95, mood.density + 0.2):
                        idx = mel.walk(chord_idx, s in vib or s % 2 == 0, register)
                        notes.append((s, degree_semi(scale, idx) - 24, 1.6))
            elif template == "theme_var":
                m = motif[: steps // 2] + motif[steps // 2:][::-1] if b % 4 == 3 else motif
                shift = 2 if b % 4 == 2 else 0
                for s, idx in enumerate(m):
                    if idx is not None:
                        i2 = int(np.clip(idx + shift, n, n * 3))
                        notes.append((s, degree_semi(scale, i2) - 24, 1.6))
            elif template == "raga_phrase" and b % 4 in (0, 1):
                # Pakad spread over two bars, starting on bar 0 of each group of 4.
                if b % 4 == 0:
                    span = 2 * steps if b + 1 < n_bars - 1 else steps
                    gap = span / len(pakad)
                    for i, semi in enumerate(pakad):
                        notes.append((i * gap, semi, gap * 1.1))
                    mel.idx = n * 2
                else:
                    notes = [(s - steps, semi, d) for s, semi, d in melody_carry if s >= steps]
            else:
                dens = (mood.density - (0.25 if b % 4 == 3 else 0.0)) * (0.6 + 0.4 * energy)
                if template == "alap":
                    dens *= min(1.0, 0.3 + (b - entry_bar["bird"]) / max(1, n_bars * 0.5))
                end_phrase = template == "raga_phrase" and b % 4 == 3
                for s in range(steps):
                    if template == "alap" and s % 2:
                        continue
                    if end_phrase and s == steps - 2:
                        notes.append((s, degree_semi(scale, mel.move_to(n * 2)) - 24, 2.0))
                        break
                    if rng.random() < dens:
                        idx = mel.walk(chord_idx, s in vib or s % 2 == 0, register)
                        notes.append((s, degree_semi(scale, idx) - 24,
                                      3.0 if template == "alap" else 1.6))
        if template == "raga_phrase" and b % 4 == 0:
            melody_carry = notes
            notes = [x for x in notes if x[0] < steps]
        melody.append([(round(s, 2), semi) for s, semi, _ in notes])
        for s, semi, length in notes:
            events.append(Event("bird", when(t0 + s * step, int(s)), tonic * 4 * 2 ** (semi / 12),
                                step * length, vel(0.55 * (0.8 + 0.2 * energy)),
                                rng.uniform(-0.6, 0.6)))

        for s in range(steps):
            t = when(t0 + s * step, s)
            strong = s in vib or s % 2 == 0

            if on("droplet") and not (last and s > 0):
                idx = chord_idx[s % 3] + n  # arpeggio, one octave up
                g = (0.4 if strong else 0.25) * (0.7 + 0.3 * energy)
                if last:
                    for i in chord_idx:  # final chord, all together
                        events.append(Event("droplet", t, degree_freq(tonic, scale, i + n),
                                            1.5, 0.35, rng.uniform(-0.5, 0.5)))
                else:
                    events.append(Event("droplet", t, degree_freq(tonic, scale, idx),
                                        0.7, vel(g), rng.uniform(-0.8, 0.8)))

            if on("cricket") and s % 4 == 1 and rng.random() < 0.6:
                events.append(Event("cricket", t, 4200 + rng.uniform(-150, 150),
                                    0.5, 0.18, rng.uniform(-1, 1)))

            if on("rain") and not last:
                if template == "rhythm_first":
                    gain = 0.5 if s in groove else 0.08
                else:
                    gain = 0.35 if strong else 0.18
                events.append(Event("rain", t, 0, 0.06, vel(gain * energy), rng.uniform(-0.7, 0.7)))

            if on("fire") and not last and rng.random() < (0.25 if strong else 0.5) * energy:
                events.append(Event("fire", t + rng.uniform(0, step), 0, 0.12,
                                    rng.uniform(0.3, 0.7), rng.uniform(-0.5, 0.5)))

            if on("log") and not (last and s > 0):
                bol = tala["theka"][s]
                g = 0.75 if s == 0 else 0.45 if s in khali else 0.55 if s in vib else 0.4
                events.append(Event("log", t, tonic * 2, 0.6, vel(g * (0.7 + 0.3 * energy)),
                                    0.15, bol))

        if on("thunder") and ((b - entry_bar["thunder"]) % 4 == 0 or last):
            events.append(Event("thunder", t0, 0, 3.5, 0.9 * (0.6 + 0.4 * energy), 0.0))

    entry = {l: entry_bar[l] * bar for l in layers}
    return Piece(events, chords, chord_semis, bar_roots, bar, step, entry, sections, melody, tonic)
