"""Talas (rhythm cycles), written for beginners.

One matra (beat of the cycle) is played as an 8th note, so 8 matras last
4 quarter-note beats at the chosen bpm.
"""

TALAS: dict[str, dict] = {
    "keherwa": {
        "name": "Keherwa",
        "matras": 8,
        "vibhags": [4, 4],
        "claps": ["X", "0"],
        "theka": ["Dha", "Ge", "Na", "Ti", "Na", "Ka", "Dhi", "Na"],
        "groove": [0, 3, 6],
        "western": "4/4, the most common beat in pop and film songs",
        "about": "An easy-going 8-beat cycle used in folk, bhajans and film songs. Counts as 1 2 3 4 | 5 6 7 8.",
    },
    "dadra": {
        "name": "Dadra",
        "matras": 6,
        "vibhags": [3, 3],
        "claps": ["X", "0"],
        "theka": ["Dha", "Dhi", "Na", "Dha", "Tu", "Na"],
        "groove": [0, 3],
        "western": "6/8, a gentle swaying lilt like a lullaby or waltz",
        "about": "A light 6-beat cycle that sways: ONE two three FOUR five six.",
    },
    "rupak": {
        "name": "Rupak",
        "matras": 7,
        "vibhags": [3, 2, 2],
        "claps": ["0", "1", "2"],
        "theka": ["Tin", "Tin", "Na", "Dhi", "Na", "Dhi", "Na"],
        "groove": [0, 3, 5],
        "western": "7/8, an odd meter felt as 3 + 2 + 2",
        "about": "A 7-beat cycle that famously starts on an open, unstressed wave (khali) instead of a clap.",
    },
    "jhaptal": {
        "name": "Jhaptal",
        "matras": 10,
        "vibhags": [2, 3, 2, 3],
        "claps": ["X", "2", "0", "3"],
        "theka": ["Dhi", "Na", "Dhi", "Dhi", "Na", "Ti", "Na", "Dhi", "Dhi", "Na"],
        "groove": [0, 2, 5, 7],
        "western": "10/8, felt as 2 + 3 + 2 + 3",
        "about": "A limping 10-beat cycle loved in classical music. The uneven 2 + 3 groups give it a rolling feel.",
    },
    "teentaal": {
        "name": "Teentaal",
        "matras": 16,
        "vibhags": [4, 4, 4, 4],
        "claps": ["X", "2", "0", "3"],
        "theka": ["Dha", "Dhin", "Dhin", "Dha", "Dha", "Dhin", "Dhin", "Dha",
                  "Dha", "Tin", "Tin", "Ta", "Ta", "Dhin", "Dhin", "Dha"],
        "groove": [0, 3, 6, 8, 11, 14],
        "western": "16 beats, like two bars of 4/4 joined into one long cycle",
        "about": "The king of talas: 16 beats in four groups of four. Beat 9 is khali (a wave), where the bass drops out.",
    },
}

CLAP_HELP = (
    "X = sam, the first and strongest beat, where the cycle lands. "
    "0 = khali, an open wave of the hand where the bass drum goes quiet. "
    "Numbers are the other claps (tali)."
)


def vibhag_starts(tala: dict) -> list[int]:
    starts, pos = [], 0
    for v in tala["vibhags"]:
        starts.append(pos)
        pos += v
    return starts


def khali_steps(tala: dict) -> set[int]:
    return {s for s, c in zip(vibhag_starts(tala), tala["claps"]) if c == "0"}


for _k, _t in TALAS.items():
    assert sum(_t["vibhags"]) == _t["matras"] == len(_t["theka"]), _k
    assert len(_t["claps"]) == len(_t["vibhags"]), _k
