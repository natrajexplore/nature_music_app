"""Export a composed piece as a Standard MIDI File, ready for any DAW or notation app.

Each nature instrument gets its own track, named after the real instrument it
acts like, so a composer can swap in real sounds.
"""

import struct

from .composer import Piece
from .sounds import BOLS
from .theory import freq_to_midi

PPQ = 480
DRUM_CH = 9
# layer -> (track name, channel, General MIDI program)
TONAL = {
    "bird": ("Bird - Lead (Alto Sax)", 0, 65),
    "droplet": ("Droplet - Chords (Piano)", 1, 0),
    "cricket": ("Cricket - Bells (Glockenspiel)", 2, 9),
    "wind": ("Wind - Pad (French Horns)", 3, 60),
    "river": ("River - Drone (Cello)", 4, 42),
}
DRUMS = {"rain": 42, "fire": 38, "thunder": 36}  # closed hi-hat, snare, bass drum
LOG_NOTES = {"open": 61, "bend": 61, "click": 62}  # low bongo, low bongo, mute hi conga
LOG_TREBLE = 60  # hi bongo


def _vlq(n: int) -> bytes:
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append(0x80 | (n & 0x7F))
        n >>= 7
    return bytes(reversed(out))


def _track(events: list[tuple[int, int, bytes]], name: str) -> bytes:
    """events: (tick, order, message). Lower order sorts first at the same tick."""
    data = b"\x00\xff\x03" + _vlq(len(name.encode())) + name.encode()
    last = 0
    for tick, _, msg in sorted(events, key=lambda e: (e[0], e[1])):
        data += _vlq(tick - last) + msg
        last = tick
    data += b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data


def _note(ch: int, pitch: int, vel: int, start: int, end: int) -> list[tuple[int, int, bytes]]:
    pitch = max(0, min(127, pitch))
    vel = max(1, min(127, vel))
    return [(start, 1, bytes([0x90 | ch, pitch, vel])),
            (max(end, start + 1), 0, bytes([0x80 | ch, pitch, 0]))]


def to_midi(piece: Piece, bpm: int, layers: list[str], matras: int, title: str) -> bytes:
    def tick(sec: float) -> int:
        return round(sec / (60 / bpm) * PPQ)

    tempo = round(60_000_000 / bpm)
    meta = [(0, 0, b"\xff\x51\x03" + tempo.to_bytes(3, "big")),
            (0, 0, bytes([0xFF, 0x58, 0x04, matras, 3, 24, 8])),  # matras/8 time signature
            (0, 0, b"\xff\x01" + _vlq(len(title.encode())) + title.encode())]
    tracks = [_track(meta, title)]

    per: dict[str, list] = {k: [] for k in (*TONAL, "drums")}
    for e in piece.events:
        start, end = tick(e.t), tick(e.t + e.dur)
        vel = round(40 + 80 * min(e.gain, 1))
        if e.inst in TONAL:
            ch = TONAL[e.inst][1]
            per[e.inst] += _note(ch, round(freq_to_midi(e.freq)), vel, start, end)
        elif e.inst in DRUMS:
            per["drums"] += _note(DRUM_CH, DRUMS[e.inst], vel, start, start + PPQ // 8)
        elif e.inst == "log":
            bass, treble = BOLS.get(e.kind, ("open", "ring"))
            if bass:
                per["drums"] += _note(DRUM_CH, LOG_NOTES[bass], vel, start, start + PPQ // 8)
            if treble:
                note = LOG_NOTES["click"] if treble == "click" else LOG_TREBLE
                per["drums"] += _note(DRUM_CH, note, vel, start, start + PPQ // 8)

    for b, chord in enumerate(piece.chords):
        t0, t1 = tick(b * piece.bar), tick((b + 1) * piece.bar)
        if "wind" in layers and b * piece.bar >= piece.entry["wind"]:
            for f in chord:
                per["wind"] += _note(3, round(freq_to_midi(f)), 60, t0, t1)
        if "river" in layers and b * piece.bar >= piece.entry["river"]:
            per["river"] += _note(4, round(freq_to_midi(piece.tonic / 2)), 70, t0, t1)

    for inst, (name, ch, program) in TONAL.items():
        if per[inst]:
            tracks.append(_track([(0, 0, bytes([0xC0 | ch, program]))] + per[inst], name))
    if per["drums"]:
        tracks.append(_track(per["drums"], "Rain / Fire / Thunder / Log drum"))

    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), PPQ)
    return header + b"".join(tracks)
