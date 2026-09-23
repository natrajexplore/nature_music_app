import re
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from .composer import MOODS, PROGRESSIONS
from .midi import to_midi
from .mixer import preview_phrase, render, save_wav
from .ragas import RAGAS, SARGAM_HELP
from .talas import CLAP_HELP, TALAS
from .templates import LAYER_ROLES, TEMPLATES
from .theory import KEYS, freq_to_key

OUTPUT_DIR = Path("output")
KEEP_TRACKS = 40  # older renders are deleted so the output folder does not grow forever
ALL_LAYERS = list(LAYER_ROLES)
PHRASES = ("scale", "aroha", "avaroha", "pakad")

app = FastAPI(title="Nature Orchestra")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5170"],
                   allow_methods=["*"], allow_headers=["*"])


class ComposeRequest(BaseModel):
    mood: str = "dawn"
    scale: str | None = None
    template: str = "free"
    bpm: int | None = Field(None, ge=40, le=160)
    duration: float = Field(45, ge=10, le=120)
    seed: int | None = Field(None, ge=0, lt=2**31)
    layers: list[str] | None = None
    key: str | None = None
    tala: str | None = None
    progression: str | None = None
    volumes: dict[str, float] | None = None
    reverb: float = Field(0.3, ge=0, le=0.7)
    humanize: float = Field(0.3, ge=0, le=1)
    swing: float = Field(0.0, ge=0, le=1)


@app.get("/api/options")
def options():
    return {
        "moods": {k: {"label": m.label, "scale": m.scale, "bpm": m.bpm, "layers": m.layers,
                      "icon": m.icon, "story": m.story, "template": m.template,
                      "tala": m.tala, "key": freq_to_key(m.tonic)}
                  for k, m in MOODS.items()},
        "ragas": {k: {kk: v for kk, v in r.items() if kk != "semitones"}
                  for k, r in RAGAS.items()},
        "templates": TEMPLATES,
        "layers": LAYER_ROLES,
        "talas": TALAS,
        "progressions": PROGRESSIONS,
        "keys": KEYS,
        "sargam_help": SARGAM_HELP,
        "clap_help": CLAP_HELP,
    }


def _tempo_word(bpm: int) -> str:
    if bpm < 70:
        return "very slow and calm"
    if bpm < 90:
        return "slow, like a relaxed walk"
    if bpm < 120:
        return "medium, like a steady walk"
    return "fast and energetic"


def _explain(meta: dict) -> list[dict]:
    raga = RAGAS[meta["scale"]]
    notes = raga["notes"]
    tpl = TEMPLATES[meta["template"]]
    tala = TALAS[meta["tala"]]
    seen, chords = set(), []
    for bar in meta["score"]:
        c = bar["chord"]
        if c["symbol"] not in seen:
            seen.add(c["symbol"])
            chords.append(f"{c['symbol']} ({c['roman']}, {' '.join(c['sargam'])})")
    vadi = (f" Its most important note (vadi) is {raga['vadi']}, answered by {raga['samvadi']} "
            f"(samvadi)." if raga["vadi"] else "")
    form = " → ".join(f"{s['name']} (bar {s['start'] + 1})" for s in meta["sections"])
    return [
        {"title": f"Raga: {raga['name']} in the key of {meta['key']}",
         "text": f"Notes: {' '.join(notes)}. {raga['sound']} Going up (aroha): "
                 f"{' '.join(raga['aroha'])}. Coming down (avaroha): {' '.join(raga['avaroha'])}. "
                 f"Catch phrase (pakad): {' '.join(raga['pakad'])}.{vadi} Sa = {meta['key']} "
                 f"here. Traditionally played at: {raga['time'].lower()}. Feeling: "
                 f"{raga['feeling'].lower()}."},
        {"title": f"Tempo: {meta['bpm']} bpm",
         "text": f"bpm means beats per minute, the heartbeat of the music. {meta['bpm']} is "
                 f"{_tempo_word(meta['bpm'])}."},
        {"title": f"Tala: {tala['name']} ({tala['matras']} beats)",
         "text": f"{tala['about']} Groups: {' + '.join(map(str, tala['vibhags']))}. Tabla "
                 f"pattern (theka): {' '.join(tala['theka'])}. In Western terms: "
                 f"{tala['western']}."},
        {"title": "Chords",
         "text": f"Each cycle sits on one chord (3 notes together). Chords used: "
                 f"{'; '.join(chords)}. Roman numerals show the chord's distance from home: I is "
                 f"home, V pulls strongly back to I. The last bar always returns to Sa, which "
                 f"is called a cadence."},
        {"title": "Song form",
         "text": f"{form}. The intro and outro are quieter, the development (B) climbs higher "
                 f"and gets busier, and the return (A') brings back the calm of the theme."},
        {"title": "Nature instruments",
         "text": " · ".join(LAYER_ROLES[l] for l in meta["layers"])},
        {"title": f"Method: {tpl['name']}",
         "text": f"{tpl['idea']} " + " ".join(tpl["steps"])},
    ]


def _cleanup() -> None:
    wavs = sorted(OUTPUT_DIR.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in wavs[KEEP_TRACKS:]:
        old.unlink(missing_ok=True)
        old.with_suffix(".mid").unlink(missing_ok=True)


@app.post("/api/compose")
def compose_track(req: ComposeRequest):
    if req.mood not in MOODS:
        raise HTTPException(422, f"Unknown mood '{req.mood}'")
    if req.scale and req.scale not in RAGAS:
        raise HTTPException(422, f"Unknown scale '{req.scale}'")
    if req.template not in TEMPLATES:
        raise HTTPException(422, f"Unknown template '{req.template}'")
    if req.layers is not None and not set(req.layers) <= set(ALL_LAYERS):
        raise HTTPException(422, "Unknown layer")
    if req.layers is not None and not req.layers:
        raise HTTPException(422, "Choose at least one instrument")
    if req.key is not None and req.key not in KEYS:
        raise HTTPException(422, f"Unknown key '{req.key}'")
    if req.tala is not None and req.tala not in TALAS:
        raise HTTPException(422, f"Unknown tala '{req.tala}'")
    if req.progression is not None and req.progression not in PROGRESSIONS:
        raise HTTPException(422, f"Unknown progression '{req.progression}'")
    if req.volumes is not None and (not set(req.volumes) <= set(ALL_LAYERS)
                                    or not all(0 <= v <= 2 for v in req.volumes.values())):
        raise HTTPException(422, "Volumes must be known layers between 0 and 2")
    seed = req.seed if req.seed is not None else secrets.randbelow(2**31)
    buf, meta, piece = render(
        req.mood, req.scale, req.bpm, req.duration, seed, req.layers, req.template,
        key=req.key, tala=req.tala, progression=req.progression, volumes=req.volumes,
        reverb=req.reverb, humanize=req.humanize, swing=req.swing)
    track_id = secrets.token_hex(8)
    save_wav(buf, OUTPUT_DIR / f"{track_id}.wav")
    title = f"{MOODS[req.mood].label} - {RAGAS[meta['scale']]['name']} in {meta['key']}"
    (OUTPUT_DIR / f"{track_id}.mid").write_bytes(
        to_midi(piece, meta["bpm"], meta["layers"], TALAS[meta["tala"]]["matras"], title))
    _cleanup()
    return {**meta, "id": track_id, "url": f"/api/audio/{track_id}.wav",
            "midi_url": f"/api/midi/{track_id}.mid", "explain": _explain(meta)}


@app.get("/api/scale/{raga}.wav")
def scale_preview(raga: str, instrument: str = "droplet", phrase: str = "scale", key: str = "C"):
    if raga not in RAGAS:
        raise HTTPException(404)
    if instrument not in ("droplet", "bird"):
        raise HTTPException(422, "instrument must be droplet or bird")
    if phrase not in PHRASES:
        raise HTTPException(422, f"phrase must be one of {', '.join(PHRASES)}")
    if key not in KEYS:
        raise HTTPException(422, f"Unknown key '{key}'")
    return Response(preview_phrase(raga, instrument, phrase, key), media_type="audio/wav")


@app.get("/api/audio/{track_id}.wav")
def get_audio(track_id: str):
    if not re.fullmatch(r"[0-9a-f]{16}", track_id):
        raise HTTPException(404)
    path = OUTPUT_DIR / f"{track_id}.wav"
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="audio/wav", filename=f"nature-music-{track_id}.wav")


@app.get("/api/midi/{track_id}.mid")
def get_midi(track_id: str):
    if not re.fullmatch(r"[0-9a-f]{16}", track_id):
        raise HTTPException(404)
    path = OUTPUT_DIR / f"{track_id}.mid"
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="audio/midi", filename=f"nature-music-{track_id}.mid")
