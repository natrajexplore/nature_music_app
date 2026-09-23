"""Ragas and scales with beginner-friendly info.

Sargam key: Capital = natural note, lowercase = komal (one step lower), Ma# = tivra (sharp) Ma.
"""

SARGAM_HELP = (
    "Sa Re Ga Ma Pa Dha Ni are the 7 Indian notes (like Do Re Mi Fa Sol La Ti). "
    "Sa is home. A lowercase name (re, ga, dha, ni) is one step lower and sounds darker; "
    "Ma# is one step higher and sounds dreamy."
)

# name -> semitones above Sa
SARGAM_SEMITONES = {
    "Sa": 0, "re": 1, "Re": 2, "ga": 3, "Ga": 4, "Ma": 5, "Ma#": 6,
    "Pa": 7, "dha": 8, "Dha": 9, "ni": 10, "Ni": 11,
}


def _r(name, notes, time, feeling, sound, aroha, avaroha, pakad, vadi=None, samvadi=None):
    """Build a raga entry.

    `aroha`, `avaroha` and `pakad` are space-separated phrases. A leading "."
    means the lower octave and a trailing "'" means the upper octave.
    """
    return {
        "name": name,
        "notes": notes,
        "semitones": [SARGAM_SEMITONES[n] for n in notes],
        "time": time,
        "feeling": feeling,
        "sound": sound,
        "aroha": aroha.split(),
        "avaroha": avaroha.split(),
        "pakad": pakad.split(),
        "vadi": vadi,
        "samvadi": samvadi,
    }


def phrase_semitones(phrase: list[str]) -> list[int]:
    """Convert a phrase such as [".Dha", "Sa", "Re'"] to semitones above middle Sa."""
    out = []
    for tok in phrase:
        octave = -12 if tok.startswith(".") else 12 if tok.endswith("'") else 0
        out.append(SARGAM_SEMITONES[tok.strip(".'")] + octave)
    return out


RAGAS: dict[str, dict] = {
    "bhupali": _r("Bhupali", ["Sa", "Re", "Ga", "Pa", "Dha"], "Evening",
                  "Peaceful, joyful",
                  "Bright and open. Only 5 notes, so it is the easiest raga to hum along with.",
                  "Sa Re Ga Pa Dha Sa'", "Sa' Dha Pa Ga Re Sa",
                  "Ga Re Sa .Dha Sa Re Ga Pa Ga Dha Pa Ga Re Sa", "Ga", "Dha"),
    "yaman": _r("Yaman", ["Sa", "Re", "Ga", "Ma#", "Pa", "Dha", "Ni"], "Early evening",
                "Romantic, calm",
                "Dreamy and glowing. The sharp Ma gives a floating feeling.",
                ".Ni Re Ga Ma# Dha Ni Sa'", "Sa' Ni Dha Pa Ma# Ga Re Sa",
                ".Ni Re Ga Re Sa Pa Ma# Ga Re .Ni Re Sa", "Ga", "Ni"),
    "bhairavi": _r("Bhairavi", ["Sa", "re", "ga", "Ma", "Pa", "dha", "ni"], "Morning",
                   "Devotional, tender",
                   "Soft and heartfelt. Every note leans a little sad and sweet.",
                   "Sa re ga Ma Pa dha ni Sa'", "Sa' ni dha Pa Ma ga re Sa",
                   "Ma ga Sa re Sa .dha .ni Sa", "Ma", "Sa"),
    "bhairav": _r("Bhairav", ["Sa", "re", "Ga", "Ma", "Pa", "dha", "Ni"], "Dawn",
                  "Serious, peaceful",
                  "Solemn like a temple morning, with a strong pull between low and bright notes.",
                  "Sa re Ga Ma Pa dha Ni Sa'", "Sa' Ni dha Pa Ma Ga re Sa",
                  "Sa Ga Ma dha Pa Ga Ma re Sa", "dha", "re"),
    "kafi": _r("Kafi", ["Sa", "Re", "ga", "Ma", "Pa", "Dha", "ni"], "Late night, spring",
               "Playful, folk-like",
               "Warm and relaxed, like a folk song or a Holi festival tune.",
               "Sa Re ga Ma Pa Dha ni Sa'", "Sa' ni Dha Pa Ma ga Re Sa",
               "Sa Re ga Ma Pa Ma ga Re Sa", "Pa", "Sa"),
    "desh": _r("Desh", ["Sa", "Re", "Ga", "Ma", "Pa", "Dha", "ni"], "Night, rainy season",
               "Longing, romantic",
               "The classic monsoon raga: hopeful, with a touch of ache.",
               "Sa Re Ma Pa ni Sa'", "Sa' ni Dha Pa Ma Ga Re Sa",
               "Re Ma Pa ni Sa' ni Dha Pa Ma Ga Re Ga Sa", "Re", "Pa"),
    "malkauns": _r("Malkauns", ["Sa", "ga", "Ma", "dha", "ni"], "Midnight",
                   "Deep, mysterious",
                   "Slow and heavy like a night sky. Five notes, with no Re and no Pa.",
                   "Sa ga Ma dha ni Sa'", "Sa' ni dha Ma ga Sa",
                   "Ma ga Ma dha ni dha Ma ga Sa", "Ma", "Sa"),
    "durga": _r("Durga", ["Sa", "Re", "Ma", "Pa", "Dha"], "Late night",
                "Calm, strong",
                "Steady and confident. Like Bhupali without Ga, so it feels open and firm.",
                "Sa Re Ma Pa Dha Sa'", "Sa' Dha Pa Ma Re Sa",
                "Re Ma Pa Dha Ma Re Sa .Dha Sa", "Ma", "Sa"),
    "todi": _r("Todi", ["Sa", "re", "ga", "Ma#", "Pa", "dha", "Ni"], "Late morning",
               "Intense, emotional",
               "Dramatic and aching. The most colourful raga in this list.",
               "Sa re ga Ma# dha Ni Sa'", "Sa' Ni dha Pa Ma# ga re Sa",
               ".dha .Ni Sa re ga re ga re Sa", "dha", "ga"),
    "marwa": _r("Marwa", ["Sa", "re", "Ga", "Ma#", "Dha", "Ni"], "Sunset",
                "Restless, yearning",
                "Unsettled. It leaves out Pa, the most stable note, so it never fully rests.",
                "Sa re Ga Ma# Dha Ni Sa'", "Sa' Ni Dha Ma# Ga re Sa",
                ".Dha .Ni re Ga Ma# Dha Ma# Ga re Sa", "re", "Dha"),
    "bageshri": _r("Bageshri", ["Sa", "Re", "ga", "Ma", "Dha", "ni"], "Late night",
                   "Romantic, gentle longing",
                   "Slow, sweet and tender. Pa is used only lightly in tradition, so it is left out here.",
                   "Sa ga Ma Dha ni Sa'", "Sa' ni Dha Ma ga Re Sa",
                   "Sa .ni .Dha Sa Ma ga Ma Dha ni Dha Ma ga Re Sa", "Ma", "Sa"),
    "hamsadhwani": _r("Hamsadhwani", ["Sa", "Re", "Ga", "Pa", "Ni"], "Evening (Carnatic)",
                      "Joyful, auspicious",
                      "Light and celebratory. Five notes, no Ma or Dha. Often opens concerts in South India.",
                      "Sa Re Ga Pa Ni Sa'", "Sa' Ni Pa Ga Re Sa",
                      "Ga Pa Ni Sa' Ni Pa Ga Re Sa"),
    "major": _r("Major (Western)", ["Sa", "Re", "Ga", "Ma", "Pa", "Dha", "Ni"], "Any time",
                "Happy, bright",
                "The familiar 'Do Re Mi' scale, also called Bilawal in Indian music.",
                "Sa Re Ga Ma Pa Dha Ni Sa'", "Sa' Ni Dha Pa Ma Ga Re Sa",
                "Sa Ga Pa Sa' Pa Ga Ma Re Sa"),
    "minor": _r("Minor (Western)", ["Sa", "Re", "ga", "Ma", "Pa", "dha", "ni"], "Any time",
                "Sad, thoughtful",
                "The familiar sad-sounding scale, also called Asavari in Indian music.",
                "Sa Re ga Ma Pa dha ni Sa'", "Sa' ni dha Pa Ma ga Re Sa",
                "Sa ga Pa dha Pa ga Ma Re Sa"),
}

SCALES: dict[str, list[int]] = {k: v["semitones"] for k, v in RAGAS.items()}

# Sanity check: every phrase only uses notes that belong to its raga.
for _k, _v in RAGAS.items():
    for _field in ("aroha", "avaroha", "pakad"):
        assert {t.strip(".'") for t in _v[_field]} <= set(_v["notes"]), (_k, _field)
    for _field in ("vadi", "samvadi"):
        assert _v[_field] is None or _v[_field] in _v["notes"], (_k, _field)
