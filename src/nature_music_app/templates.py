"""Composing templates (methods) and layer roles, written for beginners."""

TEMPLATES: dict[str, dict] = {
    "free": {
        "name": "Nature Freestyle",
        "idea": "Everything plays together and wanders freely.",
        "steps": [
            "All chosen nature sounds start at the same time.",
            "The bird melody moves step by step through the raga.",
            "Good for hearing what the raga sounds like on its own.",
        ],
    },
    "call_response": {
        "name": "Call & Response",
        "idea": "One phrase asks a question and the next one answers, like two birds talking.",
        "steps": [
            "Odd bars are the CALL: the melody stops on a note that feels unfinished.",
            "Even bars are the RESPONSE: the melody replies and lands on the chord's home note.",
            "Listen for the tension in the call and the relief in the answer.",
        ],
    },
    "theme_var": {
        "name": "Theme & Variation",
        "idea": "One short melody repeats, changing a little each time.",
        "steps": [
            "A short 1-bar theme is created once.",
            "It repeats every bar so your ear learns it.",
            "Every 3rd bar it is shifted higher, every 4th bar it is played backwards at the end.",
        ],
    },
    "alap": {
        "name": "Alap Journey",
        "idea": "The classical Indian way: start slow and calm, then wake up the rhythm.",
        "steps": [
            "It starts with only the river drone and wind, setting the home note.",
            "Long, slow bird notes explore the raga.",
            "Water drops and rhythm join later as the energy builds.",
        ],
    },
    "rising_story": {
        "name": "Rising Story",
        "idea": "Sounds join one at a time, so the music grows like a story.",
        "steps": [
            "It begins with a single nature sound.",
            "A new instrument enters at regular intervals.",
            "By the end the full orchestra plays together.",
        ],
    },
    "rhythm_first": {
        "name": "Rhythm First",
        "idea": "Build the beat first, then add the melody on top.",
        "steps": [
            "Rain and fire play the tala's accent pattern (in Keherwa, a 3 + 3 + 2 groove).",
            "Melody and water drops join after the beat feels steady.",
            "River and wind arrive last to fill out the sound.",
        ],
    },
    "raga_phrase": {
        "name": "Raga Signature",
        "idea": "The melody keeps coming back to the raga's catch phrase (pakad), like a classical singer does.",
        "steps": [
            "Every 4 bars start with the pakad, the short phrase that identifies the raga.",
            "The next bars improvise freely, obeying the raga's up (aroha) and down (avaroha) rules.",
            "Each improvisation ends on Sa, so you always feel the way home.",
        ],
    },
}

LAYER_ROLES: dict[str, str] = {
    "bird": "Melody: bird chirps tuned to the raga's notes",
    "droplet": "Harmony: water drops pluck the notes of each chord",
    "cricket": "Texture: soft night rhythm",
    "rain": "Rhythm: raindrops act like a hi-hat",
    "fire": "Accents: crackles add random sparks of rhythm",
    "thunder": "Bass: low rumble marks the start of a section",
    "river": "Drone: the flowing river hums the home note (Sa)",
    "wind": "Pad: wind sings the chord notes as a warm cloud",
    "log": "Tala: a hollow log drum plays the tabla pattern (theka) of the rhythm cycle",
}
