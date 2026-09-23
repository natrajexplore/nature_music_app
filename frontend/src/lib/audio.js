// A tiny Web Audio synth for instant feedback while learning (no server round-trip).

let ctx = null;
let bus = null;

function audio() {
  if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
  if (ctx.state === "suspended") ctx.resume();
  if (!bus) {
    const comp = ctx.createDynamicsCompressor();
    comp.connect(ctx.destination);
    bus = ctx.createGain();
    bus.gain.value = 0.8;
    bus.connect(comp);
  }
  return ctx;
}

export const mtof = (m) => 440 * 2 ** ((m - 69) / 12);

/** Silence everything scheduled so far by swapping the output bus. */
export function stopAll() {
  if (!bus) return;
  const old = bus;
  old.gain.setTargetAtTime(0, ctx.currentTime, 0.02);
  setTimeout(() => old.disconnect(), 200);
  bus = null;
}

/** A warm plucked note, like the water-drop piano. `when` is seconds from now. */
export function pluck(midi, when = 0, dur = 1.2, gain = 0.28) {
  const c = audio();
  const t = c.currentTime + when;
  const f = mtof(midi);
  const out = c.createGain();
  out.gain.setValueAtTime(0.0001, t);
  out.gain.exponentialRampToValueAtTime(gain, t + 0.006);
  out.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  const lp = c.createBiquadFilter();
  lp.type = "lowpass";
  lp.frequency.setValueAtTime(Math.min(9000, f * 10), t);
  lp.frequency.exponentialRampToValueAtTime(Math.max(300, f * 2), t + dur);
  out.connect(lp).connect(bus);
  for (const [h, type, a] of [[1, "triangle", 1], [2, "sine", 0.3], [3, "sine", 0.1]]) {
    const o = c.createOscillator();
    const g = c.createGain();
    o.type = type;
    o.frequency.value = f * h;
    g.gain.value = a;
    o.connect(g).connect(out);
    o.start(t);
    o.stop(t + dur + 0.05);
  }
}

/** Play MIDI notes one after another. Returns total length in seconds. */
export function sequence(midis, gap = 0.4, dur = 0.9) {
  midis.forEach((m, i) => m != null && pluck(m, i * gap, dur));
  return midis.length * gap + dur;
}

/** Play notes together (a chord), optionally rolled like a harp. */
export function chord(midis, when = 0, roll = 0.03, dur = 1.8) {
  midis.forEach((m, i) => pluck(m, when + i * roll, dur, 0.2));
}

function noise(c, dur) {
  const buf = c.createBuffer(1, Math.ceil(c.sampleRate * dur), c.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  const src = c.createBufferSource();
  src.buffer = buf;
  return src;
}

// Tabla bol -> [bass stroke, treble stroke], matching sounds.py on the backend.
const BOLS = {
  Dha: ["open", "ring"], Dhi: ["open", "ring"], Dhin: ["open", "long"], Ge: ["bend", null],
  Na: [null, "ring"], Ta: [null, "ring"], Tin: [null, "long"], Tu: [null, "long"],
  Ti: [null, "click"], Ka: ["click", null], Te: [null, "click"],
};

/** Play one tabla-like bol. `accent` makes it louder (used on sam). */
export function bol(name, saMidiNote = 60, accent = false, when = 0) {
  const c = audio();
  const t = c.currentTime + when;
  const [bass, treble] = BOLS[name] || ["open", "ring"];
  const level = accent ? 0.9 : 0.55;
  if (bass === "open" || bass === "bend") {
    const o = c.createOscillator();
    const g = c.createGain();
    o.frequency.setValueAtTime(130, t);
    o.frequency.exponentialRampToValueAtTime(bass === "bend" ? 115 : 80, t + 0.18);
    g.gain.setValueAtTime(level, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.45);
    o.connect(g).connect(bus);
    o.start(t);
    o.stop(t + 0.5);
  }
  if (treble === "ring" || treble === "long") {
    const f = mtof(saMidiNote + 12);
    const decay = treble === "long" ? 0.5 : 0.25;
    for (const [h, a] of [[1, 1], [2, 0.5], [3, 0.3]]) {
      const o = c.createOscillator();
      const g = c.createGain();
      o.frequency.value = f * h;
      g.gain.setValueAtTime(level * 0.35 * a, t);
      g.gain.exponentialRampToValueAtTime(0.0001, t + decay);
      o.connect(g).connect(bus);
      o.start(t);
      o.stop(t + decay + 0.05);
    }
  }
  if (treble === "click" || bass === "click") {
    const n = noise(c, 0.05);
    const bp = c.createBiquadFilter();
    const g = c.createGain();
    bp.type = "bandpass";
    bp.frequency.value = treble === "click" ? 3000 : 500;
    g.gain.setValueAtTime(level * 0.8, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.04);
    n.connect(bp).connect(g).connect(bus);
    n.start(t);
  }
}
