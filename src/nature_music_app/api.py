import re
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from .composer import MOODS
from .mixer import preview_scale, render, save_wav
from .ragas import RAGAS, SARGAM_HELP
from .templates import LAYER_ROLES, TEMPLATES

OUTPUT_DIR = Path("output")
ALL_LAYERS = list(LAYER_ROLES)

app = FastAPI(title="Nature Orchestra")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5170"],
                   allow_methods=["*"], allow_headers=["*"])


class ComposeRequest(BaseModel):
    mood: str = "dawn"
    scale: str | None = None
    template: str = "free"
    bpm: int | None = Field(None, ge=40, le=160)
    duration: float = Field(45, ge=10, le=120)
    seed: int | None = None
    layers: list[str] | None = None


@app.get("/api/options")
def options():
    return {
        "moods": {k: {"label": m.label, "scale": m.scale, "bpm": m.bpm, "layers": m.layers,
                      "icon": m.icon, "story": m.story, "template": m.template}
                  for k, m in MOODS.items()},
        "ragas": {k: {kk: v[kk] for kk in ("name", "notes", "time", "feeling", "sound")}
                  for k, v in RAGAS.items()},
        "templates": TEMPLATES,
        "layers": LAYER_ROLES,
        "sargam_help": SARGAM_HELP,
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
    roots = " → ".join(notes[d % len(notes)] for d in meta["progression"])
    tpl = TEMPLATES[meta["template"]]
    return [
        {"title": f"Raga: {raga['name']}",
         "text": f"Notes: {' '.join(notes)}. {raga['sound']} Traditionally played at: "
                 f"{raga['time'].lower()}. Feeling: {raga['feeling'].lower()}."},
        {"title": f"Tempo: {meta['bpm']} bpm",
         "text": f"bpm means beats per minute, the heartbeat of the music. {meta['bpm']} is "
                 f"{_tempo_word(meta['bpm'])}."},
        {"title": "Chords",
         "text": f"Each bar (4 beats) sits on a chord, which is 3 notes played together. This "
                 f"piece's chord roots go {roots}, then repeat. Leaving Sa creates tension; "
                 f"coming back to Sa feels like coming home."},
        {"title": "Nature instruments",
         "text": " · ".join(LAYER_ROLES[l] for l in meta["layers"])},
        {"title": f"Method: {tpl['name']}",
         "text": f"{tpl['idea']} " + " ".join(tpl["steps"])},
    ]


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
    seed = req.seed if req.seed is not None else secrets.randbelow(2**31)
    buf, meta = render(req.mood, req.scale, req.bpm, req.duration, seed, req.layers, req.template)
    track_id = secrets.token_hex(8)
    save_wav(buf, OUTPUT_DIR / f"{track_id}.wav")
    return {**meta, "id": track_id, "url": f"/api/audio/{track_id}.wav",
            "explain": _explain(meta)}


@app.get("/api/scale/{key}.wav")
def scale_preview(key: str, instrument: str = "droplet"):
    if key not in RAGAS:
        raise HTTPException(404)
    if instrument not in ("droplet", "bird"):
        raise HTTPException(422, "instrument must be droplet or bird")
    return Response(preview_scale(key, instrument), media_type="audio/wav")


@app.get("/api/audio/{track_id}.wav")
def get_audio(track_id: str):
    if not re.fullmatch(r"[0-9a-f]{16}", track_id):
        raise HTTPException(404)
    path = OUTPUT_DIR / f"{track_id}.wav"
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="audio/wav", filename=f"nature-music-{track_id}.wav")
