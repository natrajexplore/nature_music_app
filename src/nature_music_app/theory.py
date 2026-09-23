"""Small music-theory helpers: keys, note names, chord naming and Roman numerals."""

import math

KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SARGAM = ["Sa", "re", "Re", "ga", "Ga", "Ma", "Ma#", "Pa", "dha", "Dha", "ni", "Ni"]
ROMAN = ["I", "bII", "II", "bIII", "III", "IV", "#IV", "V", "bVI", "VI", "bVII", "VII"]

# (third, fifth) above the root -> (quality, chord-symbol suffix)
TRIADS = {
    (4, 7): ("major", ""),
    (3, 7): ("minor", "m"),
    (3, 6): ("diminished", "dim"),
    (4, 8): ("augmented", "aug"),
    (5, 7): ("suspended 4th", "sus4"),
    (2, 7): ("suspended 2nd", "sus2"),
}


def key_to_freq(key: str) -> float:
    """Sa frequency for a key, kept in a comfortable F3..E4 range."""
    pc = KEYS.index(key)
    midi = 60 + pc if pc <= 4 else 48 + pc
    return midi_to_freq(midi)


def freq_to_key(freq: float) -> str:
    return KEYS[round(freq_to_midi(freq)) % 12]


def midi_to_freq(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def freq_to_midi(freq: float) -> float:
    return 69 + 12 * math.log2(freq / 440.0)


def western_name(key: str, semi: int) -> str:
    """Western letter name of the note `semi` semitones above Sa in `key`."""
    return KEYS[(KEYS.index(key) + semi) % 12]


def chord_info(key: str, semis: list[int]) -> dict:
    """Name a 3-note chord given as semitones above Sa (may exceed 12).

    Tries every rotation so inversions such as Sa-Ga-Dha (C-E-A) are named
    as Am/C rather than an unnamed cluster.
    """
    pcs = [s % 12 for s in semis]
    bass = pcs[0]
    for i in range(len(pcs)):
        root = pcs[i]
        rest = sorted({(p - root) % 12 for p in pcs} - {0})
        if len(rest) == 2 and tuple(rest) in TRIADS:
            quality, suffix = TRIADS[tuple(rest)]
            symbol = western_name(key, root) + suffix
            if root != bass:
                symbol += "/" + western_name(key, bass)
            numeral = ROMAN[root]
            if quality in ("minor", "diminished"):
                numeral = numeral.lower()
            numeral += {"diminished": "°", "augmented": "+", "suspended 4th": "sus4",
                        "suspended 2nd": "sus2"}.get(quality, "")
            return {"symbol": symbol, "roman": numeral, "quality": quality,
                    "sargam": [SARGAM[p] for p in pcs],
                    "western": [western_name(key, p) for p in pcs]}
    uniq = sorted({(p - bass) % 12 for p in pcs} - {0})
    dyads = {4: ("major (no 5th)", "", ""), 3: ("minor (no 5th)", "m", ""),
             5: ("suspended 4th (no 5th)", "sus4", "sus4"), 2: ("suspended 2nd (no 5th)", "sus2", "sus2")}
    if len(uniq) == 1 and uniq[0] in dyads:
        quality, suffix, rsuffix = dyads[uniq[0]]
        numeral = ROMAN[bass].lower() if uniq[0] == 3 else ROMAN[bass]
        return {"symbol": western_name(key, bass) + suffix + "(no5)", "roman": numeral + rsuffix,
                "quality": quality, "sargam": [SARGAM[p] for p in pcs],
                "western": [western_name(key, p) for p in pcs]}
    return {"symbol": "/".join(western_name(key, p) for p in pcs), "roman": ROMAN[bass],
            "quality": "cluster", "sargam": [SARGAM[p] for p in pcs],
            "western": [western_name(key, p) for p in pcs]}
