import struct

import numpy as np
import pytest
from fastapi.testclient import TestClient

from nature_music_app import api
from nature_music_app.composer import (MOODS, PROGRESSIONS, Melody, chord_degrees, compose,
                                       degree_semi, form)
from nature_music_app.midi import to_midi
from nature_music_app.mixer import render
from nature_music_app.ragas import RAGAS, phrase_semitones
from nature_music_app.talas import TALAS
from nature_music_app.theory import chord_info, key_to_freq


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "OUTPUT_DIR", tmp_path)
    return TestClient(api.app)


def test_chord_names_and_inversions():
    assert chord_info("C", [0, 4, 7])["symbol"] == "C"
    assert chord_info("A", [0, 3, 7])["symbol"] == "Am"
    inv = chord_info("C", [0, 4, 9])  # Sa Ga Dha = C E A
    assert inv["symbol"] == "Am/C" and inv["roman"] == "vi"
    assert chord_info("C", [11, 14, 17])["roman"] == "vii°"


@pytest.mark.parametrize("raga", list(RAGAS))
def test_home_chord_is_rooted_on_sa(raga):
    scale = RAGAS[raga]["semitones"]
    idx = chord_degrees(scale, 0)
    info = chord_info("C", [degree_semi(scale, i) for i in idx])
    assert info["roman"].upper().startswith("I") and "/" not in info["symbol"], (raga, info)


def test_keys_are_tuned():
    assert key_to_freq("A") == pytest.approx(220.0)
    assert key_to_freq("C") == pytest.approx(261.63, abs=0.01)


def test_phrase_octaves():
    assert phrase_semitones([".Dha", "Sa", "Ga", "Sa'"]) == [-3, 0, 4, 12]


@pytest.mark.parametrize("raga", ["yaman", "todi", "desh", "bageshri"])
def test_melody_obeys_aroha_and_avaroha(raga):
    rng = np.random.default_rng(3)
    mel = Melody(raga, rng)
    for _ in range(400):
        before = mel.idx
        after = mel.walk([0, 2, 4], bool(rng.random() < 0.5))
        if after in (mel.lo, mel.hi) or after == before:
            continue
        semi = mel.scale[after % mel.n]
        assert semi in (mel.up if after > before else mel.down)


def test_form_covers_every_bar():
    for n in range(1, 40):
        sections = form(n)
        assert sections[0]["start"] == 0 and sections[-1]["end"] == n
        for a, b in zip(sections, sections[1:]):
            assert a["end"] == b["start"]


@pytest.mark.parametrize("tala", list(TALAS))
def test_bar_length_follows_tala(tala):
    mood = MOODS["festival"]
    piece = compose(mood, "kafi", 120, 30, np.random.default_rng(1), "rhythm_first", tala)
    assert piece.bar == pytest.approx(TALAS[tala]["matras"] * 0.25)
    assert piece.prog[-1] == 0  # ends at home


def test_same_seed_same_music():
    a, meta_a, _ = render("dawn", None, None, 20, 7)
    b, meta_b, _ = render("dawn", None, None, 20, 7)
    assert np.array_equal(a, b) and meta_a["score"] == meta_b["score"]
    assert np.max(np.abs(a)) <= 0.9 + 1e-6


def test_midi_file_structure():
    _, meta, piece = render("festival", None, None, 20, 1, progression="home_journey")
    data = to_midi(piece, meta["bpm"], meta["layers"], 8, "test")
    assert data[:4] == b"MThd"
    _, fmt, ntracks, ppq = struct.unpack(">IHHH", data[4:14])
    assert fmt == 1 and ppq == 480
    pos, found = 14, 0
    while pos < len(data):
        assert data[pos:pos + 4] == b"MTrk"
        (length,) = struct.unpack(">I", data[pos + 4:pos + 8])
        assert data[pos + 8 + length - 3:pos + 8 + length] == b"\xff\x2f\x00"
        pos += 8 + length
        found += 1
    assert found == ntracks >= 3


def test_options_lists_everything(client):
    o = client.get("/api/options").json()
    assert set(o["ragas"]) == set(RAGAS) and set(o["talas"]) == set(TALAS)
    assert set(o["progressions"]) == set(PROGRESSIONS)
    assert "pakad" in o["ragas"]["yaman"]


def test_compose_downloads(client):
    r = client.post("/api/compose", json={
        "mood": "riyaz", "duration": 20, "seed": 5, "key": "D", "tala": "dadra",
        "progression": "drone", "volumes": {"log": 1.5}, "swing": 0.5})
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["key"] == "D" and j["tala"] == "dadra"
    assert all(bar["chord"]["roman"] == "I" for bar in j["score"])
    assert client.get(j["url"]).headers["content-type"] == "audio/wav"
    assert client.get(j["midi_url"]).content[:4] == b"MThd"


@pytest.mark.parametrize("body", [
    {"key": "H"}, {"tala": "nope"}, {"progression": "x"}, {"layers": []},
    {"volumes": {"bird": 5}}, {"volumes": {"piano": 1}}, {"reverb": 2},
])
def test_compose_rejects_bad_input(client, body):
    assert client.post("/api/compose", json={"duration": 10, **body}).status_code == 422


def test_phrase_preview(client):
    for phrase in ("scale", "aroha", "avaroha", "pakad"):
        r = client.get(f"/api/scale/bhupali.wav?phrase={phrase}&key=G")
        assert r.status_code == 200 and r.content[:4] == b"RIFF"
    assert client.get("/api/scale/bhupali.wav?phrase=nope").status_code == 422
