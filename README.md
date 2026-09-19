# 🌿 Nature Orchestra

**Compose original music from the sounds of nature, and learn how music works while you do it.**

Birds sing the melody. Water drops pluck the chords. Rain plays the hi-hat. A river hums the home note. Nature Orchestra turns synthesized nature sounds into a tuned orchestra, then composes with Indian ragas and Western scales, in the layered, harmony-rich spirit of film-score orchestration.

Everything is generated in code: no recordings, no samples, no licences to worry about. Every track is unique, and any track can be reproduced from its seed.

---

## ✨ Features

- **Nature instruments:** eight procedurally synthesized sounds, each tuned and given a musical role.
- **12 ragas + 2 Western scales:** each with its notes in Sa Re Ga notation, time of day, feeling, and a plain-English description.
- **6 composing methods:** named recipes (Call & Response, Alap Journey, ...) that change how the music is built.
- **13 real-life scenarios:** pick a moment (a morning walk, a rainy window, bedtime) and get a matching raga, tempo, instruments and method.
- **Learn while you listen:**
  - *Hear scale* buttons play any raga up and down.
  - A piano lights up the keys of the selected raga.
  - Each nature sound is labelled with the real instrument it acts like (🎷 🎹 🥁 🎺 🎻).
  - A *What am I hearing?* panel explains the raga, tempo, chords, instruments and method of every track.
- **Download** any track as a stereo WAV.
- **Reproducible:** the same seed gives the same music.

---

## 🎼 How it works

```
Scenario ─► Raga + Tempo ─► Composer ─► Note events ─► Mixer ─► Stereo WAV
(mood)      (scale rules)   (template)   per instrument  (pan + reverb)
```

1. **Sounds** (`sounds.py`): NumPy/SciPy synthesizers create each nature sound from noise, filters and FM synthesis.
2. **Composer** (`composer.py`): picks a chord progression, then writes a melody, arpeggios and rhythm on the notes of the chosen raga. The composing method decides when each instrument enters and how the melody behaves.
3. **Mixer** (`mixer.py`): places every note in the stereo field with equal-power panning, adds continuous beds (river, rain) and a chord-following wind pad, applies reverb, and normalizes.

### The nature instruments

| Sound | Musical role | Acts like |
|---|---|---|
| 🐦 Bird | Melody, chirps tuned to the raga's notes | 🎷 Saxophone lead |
| 💧 Droplet | Harmony, plucked chord arpeggios | 🎹 Piano |
| 🍃 Wind | Pad, resonates on the chord tones | 🎺 Horn section |
| 🌊 River | Drone on the home note (Sa) | 🎻 Cello |
| 🌧️ Rain | Rhythm, short bright bursts | 🥁 Hi-hat |
| 🔥 Fire | Accents, random crackles | 🥁 Snare |
| ⚡ Thunder | Bass, low rumble marking sections | 🥁 Bass drum |
| 🦗 Cricket | Night texture | 🔔 Bells |

### Composing methods

| Method | Idea |
|---|---|
| **Nature Freestyle** | Everything plays together and wanders freely. |
| **Call & Response** | One phrase asks a question (ends unresolved), the next answers (lands on the home note). |
| **Theme & Variation** | A short melody repeats, shifted higher on bar 3 and reversed at the end of bar 4. |
| **Alap Journey** | The classical way: drone first, then slow melody, then water drops and rhythm. |
| **Rising Story** | Instruments join one at a time until the full orchestra plays. |
| **Rhythm First** | Rain and fire play a 3 + 3 + 2 beat before the melody joins. |

### Ragas and scales

Capital letters are natural notes, lowercase are *komal* (a step lower), and `Ma#` is *tivra* (a step higher).

| Raga | Notes | Time | Feeling |
|---|---|---|---|
| Bhupali | Sa Re Ga Pa Dha | Evening | Peaceful, joyful |
| Yaman | Sa Re Ga Ma# Pa Dha Ni | Early evening | Romantic, calm |
| Bhairavi | Sa re ga Ma Pa dha ni | Morning | Devotional, tender |
| Bhairav | Sa re Ga Ma Pa dha Ni | Dawn | Serious, peaceful |
| Kafi | Sa Re ga Ma Pa Dha ni | Late night, spring | Playful, folk-like |
| Desh | Sa Re Ga Ma Pa Dha ni | Night, rainy season | Longing, romantic |
| Malkauns | Sa ga Ma dha ni | Midnight | Deep, mysterious |
| Durga | Sa Re Ma Pa Dha | Late night | Calm, strong |
| Todi | Sa re ga Ma# Pa dha Ni | Late morning | Intense, emotional |
| Marwa | Sa re Ga Ma# Dha Ni | Sunset | Restless, yearning |
| Bageshri | Sa Re ga Ma Dha ni | Late night | Romantic, gentle longing |
| Hamsadhwani | Sa Re Ga Pa Ni | Evening (Carnatic) | Joyful, auspicious |
| Major (Western) | Sa Re Ga Ma Pa Dha Ni | Any time | Happy, bright |
| Minor (Western) | Sa Re ga Ma Pa dha ni | Any time | Sad, thoughtful |

### Real-life scenarios

| | Scenario | Raga | Method |
|---|---|---|---|
| 🌅 | Dawn Chorus | Bhupali | Rising Story |
| ⛈️ | Monsoon Storm | Bhairavi | Rhythm First |
| 🌙 | Calm Night | Yaman | Alap Journey |
| 🔥 | Campfire | Minor | Nature Freestyle |
| 🚶 | Morning Walk | Hamsadhwani | Call & Response |
| 🌧️ | Rainy Day Indoors | Desh | Alap Journey |
| 🧘 | Riverside Meditation | Bhairav | Alap Journey |
| 😴 | Bedtime Lullaby | Durga | Theme & Variation |
| 🎉 | Village Festival | Kafi | Rhythm First |
| 🥾 | Forest Adventure | Major | Rising Story |
| 💔 | Missing Someone | Bageshri | Call & Response |
| 📚 | Study & Focus | Bhupali | Theme & Variation |
| 🌇 | Sunset by the Sea | Marwa | Alap Journey |

---

## 🚀 Getting started

### Requirements

- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- Node.js 20.19+ (or 22.12+) and npm

### Install

```bash
git clone https://github.com/natrajexplore/nature_music_app.git
cd nature_music_app

uv sync                          # Python dependencies
cd frontend && npm install       # frontend dependencies
```

### Run

Start both servers (two terminals):

```bash
uv run nature-music-app          # backend  -> http://localhost:8001
cd frontend && npm run dev       # frontend -> http://localhost:5170
```

Open **http://localhost:5170**, pick a scenario, and press **Compose new music**.

---

## 🔌 API

The backend is a FastAPI app. Interactive docs are at `http://localhost:8001/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/options` | Scenarios, ragas, methods and instrument roles |
| `POST` | `/api/compose` | Compose a track, returns metadata, an audio URL and explanations |
| `GET` | `/api/audio/{id}.wav` | Download a composed track |
| `GET` | `/api/scale/{raga}.wav?instrument=droplet\|bird` | Hear a raga's scale, up and down |

Compose a track from the command line:

```bash
curl -X POST http://localhost:8001/api/compose \
  -H "Content-Type: application/json" \
  -d '{"mood": "riverside", "scale": "bhairav", "template": "alap", "duration": 60, "seed": 42}'
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `mood` | string | `dawn` | Scenario key, see `/api/options` |
| `scale` | string | mood's raga | Any raga key |
| `template` | string | `free` | Composing method key |
| `bpm` | int, 40-160 | mood's tempo | |
| `duration` | number, 10-120 | `45` | Seconds (the tail adds about 3 s of reverb) |
| `seed` | int | random | Same seed gives the same music |
| `layers` | string list | mood's instruments | Any of the eight nature instruments |

Composed tracks are saved to `output/` (gitignored). They are not cleaned up automatically.

---

## 📁 Project structure

```
nature_music_app/
├── src/nature_music_app/
│   ├── sounds.py      # nature sound synthesizers
│   ├── ragas.py       # ragas and scales, with beginner info
│   ├── templates.py   # composing methods and instrument roles
│   ├── composer.py    # scenarios, chord progressions, melody and rhythm rules
│   ├── mixer.py       # rendering: panning, beds, reverb, WAV
│   └── api.py         # FastAPI endpoints
├── frontend/          # React + Vite UI
└── pyproject.toml
```

**Built with:** Python, NumPy, SciPy, FastAPI, Uvicorn, React, Vite.

---

## ⚠️ Honest limitations

- **Synthesized, not recorded.** The nature sounds are convincing textures, but they are generated, not real field recordings. There are no real saxophone, piano or drum samples: those labels describe each sound's musical role.
- **Simplified ragas.** Each raga is reduced to its note set. Real ragas also depend on ascending and descending rules, characteristic phrases and ornaments (*gamaka*), which are not modelled. Bageshri and Hamsadhwani use common simplified note sets.
- **Rule-based composition.** The music comes from hand-written rules and randomness, not a trained model, so it is pleasant and consistent rather than deeply expressive.
- **Local only.** CORS allows only `http://localhost:5170`, and there is no authentication or output cleanup, so it is not ready to deploy as is.
- **No automated tests yet.**

## 🌱 Ideas for the future

Loading real nature recordings as instruments, MP3 and MIDI export, ascending and descending raga rules, more ragas, and explanations in Tamil and Hindi.

---

*Made with 🎶 and 🌿.*
