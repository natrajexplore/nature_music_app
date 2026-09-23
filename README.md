# 🌿 Nature Orchestra

**Compose original music from the sounds of nature, and learn how music works while you do it.**

Birds sing the melody. Water drops pluck the chords. Rain plays the hi-hat. A river hums the home note. Nature Orchestra turns synthesized nature sounds into a tuned orchestra, then composes with Indian ragas and Western scales, in the layered, harmony-rich spirit of film-score orchestration.

Everything is generated in code: no recordings, no samples, no licences to worry about. Every track is unique, and any track can be reproduced from its seed.

---

## ✨ Features

### 🎼 Studio: a composer's workbench

- **9 nature instruments:** procedurally synthesized sounds, each tuned and given a musical role, including a 🪵 hollow log drum that plays real tabla patterns.
- **12 ragas + 2 Western scales,** each with its aroha (up), avaroha (down), pakad (catch phrase), vadi/samvadi (most important notes), time of day and feeling.
- **Raga-aware melody:** the composer obeys each raga's aroha and avaroha, leans on its vadi, and can quote its pakad.
- **5 talas (rhythm cycles):** Keherwa (8), Dadra (6), Rupak (7), Jhaptal (10) and Teentaal (16), with sam, khali and theka.
- **Any of 12 keys,** tempo from 40 to 160 bpm, and **5 chord progressions** (Home Journey, Gentle Wave, Folk Circle, Anthem, Drone).
- **7 composing methods:** Nature Freestyle, Call & Response, Theme & Variation, Alap Journey, Rising Story, Rhythm First and Raga Signature.
- **Song form:** every piece has an Intro → Theme (A) → Development (B) → Return (A') → Outro energy arc, and ends with a cadence on Sa.
- **Mixer:** per-instrument volume faders, reverb, humanize (natural timing and loudness) and swing.
- **14 real-life scenarios:** pick a moment (a morning walk, a rainy window, bedtime, daily riyaz) and get a matching raga, key, tala, tempo, instruments and method.
- **See the music:** a live piano roll with playhead and click-to-seek, and a bar-by-bar **score** with chord symbols, Roman numerals and the melody in sargam and Western notes.
- **Export:** stereo **WAV** and multi-track **MIDI** (one track per instrument, General MIDI programs, tempo and tala time signature) for GarageBand, FL Studio, Reaper, Ableton, Logic or MuseScore.
- **Reproducible:** lock the seed to keep the melody while you change the mix; recent compositions are remembered so you can reload or recompose them.

### 📚 Learn, 👂 Ear training and 📖 Glossary

- **10 interactive lessons**, beginner to advanced: pitch and octaves, the 12 notes (sargam, Western, solfège), ragas, rhythm and tala, intervals, chords and Roman numerals, melody writing, arrangement and form, mixing, and a composing workflow. Every lesson has *Try it* sound buttons, a playable piano or tala wheel, and a quick-check quiz. Progress is saved in the browser.
- **Playable piano:** click the keys or type `A W S E D F T G Y H U J K`. Keys are labelled in sargam and Western notes for whichever key you choose; the raga's notes glow.
- **Tala wheel:** hear the theka, watch each beat light up, and see where to clap (X, 2, 3) and wave (0).
- **5 ear-training games:** Higher or lower, Name the note, Name any of 12, Chord colour (major/minor/diminished/augmented) and Which raga?, with streak tracking.
- **Glossary** of 45+ terms (Indian, Western and production) with search and filters.
- A **What am I hearing?** panel explains the raga, tala, chords, song form, instruments and method of every track.

---

## 🎼 How it works

```
Scenario ─► Raga + Key + Tala ─► Composer ─► Note events ─► Mixer ─► Stereo WAV
(mood)      (aroha/avaroha,      (method,     per instrument  (pan, faders,  └► MIDI
             pakad, theka)        form)                        reverb)       └► Score + piano roll
```

1. **Sounds** (`sounds.py`): NumPy/SciPy synthesizers create each nature sound from noise, filters and FM synthesis.
2. **Composer** (`composer.py`): splits the piece into a song form, picks a chord progression built from the raga's own notes, then writes a melody (obeying aroha/avaroha, leaning on the vadi, quoting the pakad), arpeggios, and rhythm following the tala. The composing method decides when each instrument enters and how the melody behaves. The last bar always resolves to Sa.
3. **Mixer** (`mixer.py`): places every note in the stereo field with equal-power panning, applies each instrument's fader, adds continuous beds (river, rain) and a chord-following wind pad, applies reverb, fades out and normalizes. It also writes the score (chords named by `theory.py`) and piano-roll data.
4. **MIDI** (`midi.py`): writes a Standard MIDI File with one named track per instrument.
5. **Frontend** (`frontend/`): React UI. Lessons, ear training, the piano and the tala wheel use a small Web Audio synth (`src/lib/audio.js`) for instant sound.

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
| 🪵 Log drum | Plays the tala's theka (tabla bols) | 🪘 Tabla |

### Composing methods

| Method | Idea |
|---|---|
| **Nature Freestyle** | Everything plays together and wanders freely. |
| **Call & Response** | One phrase asks a question (ends unresolved), the next answers (lands on the home note). |
| **Theme & Variation** | A short melody repeats, shifted higher on bar 3 and reversed at the end of bar 4. |
| **Alap Journey** | The classical way: drone first, then slow melody, then water drops and rhythm. |
| **Rising Story** | Instruments join one at a time until the full orchestra plays. |
| **Rhythm First** | Rain and fire play the tala's accent pattern before the melody joins. |
| **Raga Signature** | Every 4 bars open with the raga's pakad, then improvise and return to Sa. |

### Talas (rhythm cycles)

One matra is played as an 8th note, so 8 matras last 4 beats at the chosen bpm.

| Tala | Beats | Groups | Western feel |
|---|---|---|---|
| Keherwa | 8 | 4 + 4 | 4/4 |
| Dadra | 6 | 3 + 3 | 6/8 |
| Rupak | 7 | 3 + 2 + 2 | 7/8 |
| Jhaptal | 10 | 2 + 3 + 2 + 3 | 10/8 |
| Teentaal | 16 | 4 + 4 + 4 + 4 | two bars of 4/4 |

### Chord progressions

Chords are built from the raga's own notes and are always rooted on their degree. Ragas without a 3rd or 5th get sus or open (no 5th) chords.

| Progression | Degrees | Idea |
|---|---|---|
| Home Journey | I – IV – V – I | Leave home, travel, come back |
| Gentle Wave | I – vi – IV – V | Dips into a softer chord |
| Folk Circle | I – iii – IV – I | Small steps, like a village song |
| Anthem | I – V – vi – IV | The famous pop/film loop |
| Drone (Raga Style) | I – I – I – I | Classical style: all colour from the melody |

### Ragas and scales

Capital letters are natural notes, lowercase are *komal* (a step lower), and `Ma#` is *tivra* (a step higher).

The table shows each raga's note set; `/api/options` also returns its aroha, avaroha, pakad, vadi and samvadi.

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
| 🧘 | Riverside Meditation | Bhairav | Raga Signature |
| 😴 | Bedtime Lullaby | Durga | Theme & Variation |
| 🎉 | Village Festival | Kafi | Rhythm First |
| 🥾 | Forest Adventure | Major | Rising Story |
| 💔 | Missing Someone | Bageshri | Call & Response |
| 📚 | Study & Focus | Bhupali | Raga Signature |
| 🌇 | Sunset by the Sea | Marwa | Alap Journey |
| 🪷 | Daily Riyaz (Practice) | Yaman | Raga Signature |

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

Open **http://localhost:5170**, pick a scenario, and press **Compose new music**. Visit the **Learn** tab to start the lessons.

To point the frontend at a different backend, set `VITE_API_URL` (for example `VITE_API_URL=http://192.168.1.5:8001 npm run dev`).

### Test

```bash
uv run pytest                    # backend: theory, composer rules, MIDI, API
cd frontend && npm run lint && npm run build
```

---

## 🔌 API

The backend is a FastAPI app. Interactive docs are at `http://localhost:8001/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/options` | Scenarios, ragas, talas, progressions, keys, methods and instrument roles |
| `POST` | `/api/compose` | Compose a track, returns metadata, audio and MIDI URLs, score, piano-roll notes and explanations |
| `GET` | `/api/audio/{id}.wav` | Download a composed track |
| `GET` | `/api/midi/{id}.mid` | Download the composed track as MIDI |
| `GET` | `/api/scale/{raga}.wav?instrument=droplet\|bird&phrase=scale\|aroha\|avaroha\|pakad&key=C` | Hear a raga phrase with a nature sound |

Compose a track from the command line:

```bash
curl -X POST http://localhost:8001/api/compose \
  -H "Content-Type: application/json" \
  -d '{"mood": "riverside", "scale": "bhairav", "template": "alap", "duration": 60, "seed": 42,
       "key": "D", "tala": "rupak", "progression": "drone", "volumes": {"bird": 1.2}}'
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `mood` | string | `dawn` | Scenario key, see `/api/options` |
| `scale` | string | mood's raga | Any raga key |
| `template` | string | `free` | Composing method key |
| `bpm` | int, 40-160 | mood's tempo | |
| `duration` | number, 10-120 | `45` | Seconds (the tail adds about 3 s of reverb) |
| `seed` | int | random | Same seed gives the same music |
| `layers` | string list | mood's instruments | Any of the nine nature instruments |
| `key` | string | mood's key | `C`, `C#`, ... `B`: the note used as Sa |
| `tala` | string | mood's tala | `keherwa`, `dadra`, `rupak`, `jhaptal`, `teentaal` |
| `progression` | string | random | `home_journey`, `gentle`, `folk`, `anthem`, `drone` |
| `volumes` | object | all `1.0` | Per-instrument level, 0 to 2 |
| `reverb` | number, 0-0.7 | `0.3` | Wet mix |
| `humanize` | number, 0-1 | `0.3` | Timing and loudness variation |
| `swing` | number, 0-1 | `0` | Delays every second matra |

Composed WAV and MIDI files are saved to `output/` (gitignored). Only the 40 most recent tracks are kept.

---

## 📁 Project structure

```
nature_music_app/
├── src/nature_music_app/
│   ├── sounds.py      # nature sound synthesizers
│   ├── ragas.py       # ragas: notes, aroha, avaroha, pakad, vadi, samvadi
│   ├── talas.py       # rhythm cycles: vibhags, claps, theka
│   ├── theory.py      # keys, note names, chord naming, Roman numerals
│   ├── templates.py   # composing methods and instrument roles
│   ├── composer.py    # scenarios, form, chords, raga-aware melody and rhythm
│   ├── mixer.py       # rendering: panning, faders, beds, reverb, WAV, score
│   ├── midi.py        # Standard MIDI File export
│   └── api.py         # FastAPI endpoints
├── tests/             # pytest suite
├── frontend/src/
│   ├── components/    # Studio, Learn, EarTraining, Glossary, Piano, TalaCircle, PianoRoll, Score
│   ├── data/          # lessons and glossary
│   └── lib/           # Web Audio synth, theory helpers, API URL, local storage
└── pyproject.toml
```

**Built with:** Python, NumPy, SciPy, FastAPI, Uvicorn, React, Vite.

---

## ⚠️ Honest limitations

- **Synthesized, not recorded.** The nature sounds are convincing textures, but they are generated, not real field recordings. There are no real saxophone, piano or drum samples: those labels describe each sound's musical role.
- **Simplified ragas.** Aroha, avaroha, pakad and vadi are modelled, but ornaments (*gamaka*), meend (slides) and subtle note-usage rules are not. Some ragas use common simplified note sets: Desh uses only komal ni (real Desh rises with shuddha Ni), and Bageshri and Hamsadhwani are simplified too.
- **Harmony on ragas is a fusion choice.** Indian classical music is traditionally drone-based; the chord progressions are a film-score style addition. Pick *Drone (Raga Style)* for a classical feel.
- **Rule-based composition.** The music comes from hand-written rules and randomness, not a trained model, so it is pleasant and consistent rather than deeply expressive.
- **Local only.** CORS allows only `http://localhost:5170`, and there is no authentication, so it is not ready to deploy as is.

## 🌱 Ideas for the future

Loading real nature recordings as instruments, MP3 export, gamaka (slides and ornaments), more ragas and talas, and lessons in Tamil and Hindi.

---

*Made with 🎶 and 🌿.*
