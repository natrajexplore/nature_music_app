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


def _r(name, notes, time, feeling, sound):
    return {
        "name": name,
        "notes": notes,
        "semitones": [SARGAM_SEMITONES[n] for n in notes],
        "time": time,
        "feeling": feeling,
        "sound": sound,
    }


RAGAS: dict[str, dict] = {
    "bhupali": _r("Bhupali", ["Sa", "Re", "Ga", "Pa", "Dha"], "Evening",
                  "Peaceful, joyful",
                  "Bright and open. Only 5 notes, so it is the easiest raga to hum along with."),
    "yaman": _r("Yaman", ["Sa", "Re", "Ga", "Ma#", "Pa", "Dha", "Ni"], "Early evening",
                "Romantic, calm",
                "Dreamy and glowing. The sharp Ma gives a floating feeling."),
    "bhairavi": _r("Bhairavi", ["Sa", "re", "ga", "Ma", "Pa", "dha", "ni"], "Morning",
                   "Devotional, tender",
                   "Soft and heartfelt. Every note leans a little sad and sweet."),
    "bhairav": _r("Bhairav", ["Sa", "re", "Ga", "Ma", "Pa", "dha", "Ni"], "Dawn",
                  "Serious, peaceful",
                  "Solemn like a temple morning, with a strong pull between low and bright notes."),
    "kafi": _r("Kafi", ["Sa", "Re", "ga", "Ma", "Pa", "Dha", "ni"], "Late night, spring",
               "Playful, folk-like",
               "Warm and relaxed, like a folk song or a Holi festival tune."),
    "desh": _r("Desh", ["Sa", "Re", "Ga", "Ma", "Pa", "Dha", "ni"], "Night, rainy season",
               "Longing, romantic",
               "The classic monsoon raga: hopeful, with a touch of ache."),
    "malkauns": _r("Malkauns", ["Sa", "ga", "Ma", "dha", "ni"], "Midnight",
                   "Deep, mysterious",
                   "Slow and heavy like a night sky. Five notes, with no Re and no Pa."),
    "durga": _r("Durga", ["Sa", "Re", "Ma", "Pa", "Dha"], "Late night",
                "Calm, strong",
                "Steady and confident. Like Bhupali without Ga, so it feels open and firm."),
    "todi": _r("Todi", ["Sa", "re", "ga", "Ma#", "Pa", "dha", "Ni"], "Late morning",
               "Intense, emotional",
               "Dramatic and aching. The most colourful raga in this list."),
    "marwa": _r("Marwa", ["Sa", "re", "Ga", "Ma#", "Dha", "Ni"], "Sunset",
                "Restless, yearning",
                "Unsettled. It leaves out Pa, the most stable note, so it never fully rests."),
    "bageshri": _r("Bageshri", ["Sa", "Re", "ga", "Ma", "Dha", "ni"], "Late night",
                   "Romantic, gentle longing",
                   "Slow, sweet and tender. Pa is used only lightly in tradition, so it is left out here."),
    "hamsadhwani": _r("Hamsadhwani", ["Sa", "Re", "Ga", "Pa", "Ni"], "Evening (Carnatic)",
                      "Joyful, auspicious",
                      "Light and celebratory. Five notes, no Ma or Dha. Often opens concerts in South India."),
    "major": _r("Major (Western)", ["Sa", "Re", "Ga", "Ma", "Pa", "Dha", "Ni"], "Any time",
                "Happy, bright",
                "The familiar 'Do Re Mi' scale, also called Bilawal in Indian music."),
    "minor": _r("Minor (Western)", ["Sa", "Re", "ga", "Ma", "Pa", "dha", "ni"], "Any time",
                "Sad, thoughtful",
                "The familiar sad-sounding scale, also called Asavari in Indian music."),
}

SCALES: dict[str, list[int]] = {k: v["semitones"] for k, v in RAGAS.items()}
