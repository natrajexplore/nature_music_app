import { useRef, useState } from "react";
import { API } from "../lib/api";
import { sequence, stopAll } from "../lib/audio";
import { KEYS, saMidi, tokenSemi } from "../lib/theory";
import { load, save } from "../lib/store";
import Piano from "./Piano";
import PianoRoll from "./PianoRoll";
import Score from "./Score";
import TalaCircle from "./TalaCircle";


const ICONS = { bird: "🐦", droplet: "💧", cricket: "🦗", rain: "🌧️", fire: "🔥", thunder: "⚡", river: "🌊", wind: "🍃", log: "🪵" };
// The real instrument each nature sound acts like in the music (and in the MIDI export).
const LIKE = {
  bird: ["🎷", "saxophone lead"], droplet: ["🎹", "piano chords"], cricket: ["🔔", "bells"],
  rain: ["🥁", "hi-hat"], fire: ["🥁", "snare"], thunder: ["🥁", "bass drum"],
  river: ["🎻", "cello drone"], wind: ["🎺", "horn section"], log: ["🪘", "tabla"],
};

function Step({ n, title, children }) {
  return <h2><span className="num">{n}</span> {title}{children}</h2>;
}

function Slider({ label, value, min, max, step = 1, onChange, fmt = (v) => v }) {
  return (
    <label className="slider">
      <span>{label} <b>{fmt(value)}</b></span>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </label>
  );
}

function fromMood(opts, key) {
  const m = opts.moods[key];
  return { mood: key, raga: m.scale, template: m.template, layers: m.layers, key: m.key, bpm: m.bpm, tala: m.tala };
}

export default function Studio({ opts, setKeyName, active = true }) {
  const [s, setS] = useState(() => ({
    ...fromMood(opts, "dawn"), duration: 60, progression: "auto", reverb: 0.3, humanize: 0.3,
    swing: 0, volumes: {}, seed: "", lockSeed: false,
  }));
  const [track, setTrack] = useState(null);
  const [busy, setBusy] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [view, setView] = useState("roll");
  const [error, setError] = useState("");
  const [showTala, setShowTala] = useState(false);
  const [history, setHistory] = useState(() => load("history", []));
  const audioRef = useRef(null);
  const previewRef = useRef(null);

  const set = (patch) => setS((cur) => ({ ...cur, ...patch }));
  const pickMood = (k) => { set(fromMood(opts, k)); setKeyName(opts.moods[k].key); };
  const setKey = (k) => { set({ key: k }); setKeyName(k); };
  const toggle = (l) => set({ layers: s.layers.includes(l) ? s.layers.filter((x) => x !== l) : [...s.layers, l] });
  const vol = (l) => s.volumes[l] ?? 1;

  const hearBird = (raga) => {
    stopAll();
    previewRef.current?.pause();
    previewRef.current = new Audio(`${API}/api/scale/${raga}.wav?instrument=bird&key=${encodeURIComponent(s.key)}`);
    previewRef.current.play();
  };
  const hearPhrase = (raga, field) => {
    previewRef.current?.pause();
    stopAll();
    const sa = saMidi(s.key);
    sequence(opts.ragas[raga][field].map((t) => sa + tokenSemi(t)), field === "pakad" ? 0.36 : 0.42);
  };

  const stop = () => {
    const a = audioRef.current;
    if (a) { a.pause(); a.currentTime = 0; }
  };

  const surprise = () => {
    const pickOne = (o) => { const ks = Object.keys(o); return ks[Math.floor(Math.random() * ks.length)]; };
    const mood = pickOne(opts.moods);
    const base = fromMood(opts, mood);
    set({ ...base, raga: pickOne(opts.ragas), template: pickOne(opts.templates), tala: pickOne(opts.talas),
      key: KEYS[Math.floor(Math.random() * 12)], progression: "auto", lockSeed: false });
  };

  const compose = async (settings = s) => {
    previewRef.current?.pause();
    stopAll();
    setBusy(true);
    setError("");
    try {
      const volumes = Object.fromEntries(settings.layers.map((l) => [l, settings.volumes[l] ?? 1]));
      const body = {
        mood: settings.mood, scale: settings.raga, template: settings.template, duration: settings.duration,
        layers: settings.layers, key: settings.key, bpm: settings.bpm, tala: settings.tala,
        progression: settings.progression === "auto" ? null : settings.progression,
        reverb: settings.reverb, humanize: settings.humanize, swing: settings.swing, volumes,
        seed: settings.lockSeed && settings.seed !== "" ? Number(settings.seed) : null,
      };
      const res = await fetch(`${API}/api/compose`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
      });
      if (!res.ok) {
        const d = (await res.json()).detail;
        throw new Error(typeof d === "string" ? d : "Compose failed: check the settings");
      }
      const t = await res.json();
      setTrack(t);
      set({ seed: String(t.seed) });
      const entry = { ...settings, seed: String(t.seed), lockSeed: true, at: Date.now(),
        label: `${opts.moods[t.mood].icon} ${opts.ragas[t.scale].name} · ${opts.talas[t.tala].name} · ${t.key}` };
      const h = [entry, ...history].slice(0, 12);
      setHistory(h);
      save("history", h);
      setTimeout(() => audioRef.current?.play(), 100);
    } catch (e) {
      setError(e.message === "Failed to fetch" ? "Backend not reachable. Run: uv run nature-music-app" : e.message);
    } finally {
      setBusy(false);
    }
  };

  const tpl = opts.templates[s.template];
  const tala = opts.talas[s.tala];
  const raga = opts.ragas[s.raga];
  const currentBar = track ? Math.floor(time / track.bar_seconds) : -1;

  return (
    <>
      <Step n="1" title="Pick a real-life scenario">
        <button className="mini push" onClick={surprise} title="Random raga, tala, method and key">🎲 Surprise me</button>
      </Step>
      <p className="help">Choose the moment you want music for. It sets a matching raga, key, tempo, tala, instruments and method, which you can change below.</p>
      <div className="cards scenarios">
        {Object.entries(opts.moods).map(([k, m]) => (
          <button key={k} className={s.mood === k ? "card scenario on" : "card scenario"} onClick={() => pickMood(k)}>
            <span className="icon">{m.icon}</span>
            <strong>{m.label}</strong>
            <span className="desc">{m.story}</span>
            <span className="meta">{opts.ragas[m.scale].name} · {opts.talas[m.tala].name} · {m.bpm} bpm</span>
          </button>
        ))}
      </div>

      <Step n="2" title="Pick a raga (the notes you can use)" />
      <p className="help">{opts.sargam_help}</p>
      <div className="cards">
        {Object.entries(opts.ragas).map(([k, r]) => (
          <div key={k} role="button" tabIndex={0} className={s.raga === k ? "card on" : "card"}
               onClick={() => set({ raga: k })} onKeyDown={(e) => e.key === "Enter" && set({ raga: k })}>
            <strong>🎼 {r.name}</strong>
            <div className="notes">{r.notes.join(" ")}</div>
            <div className="meta">{r.time} · {r.feeling}</div>
            <div className="desc">{r.sound}</div>
            <div className="row">
              <button className="mini" onClick={(e) => { e.stopPropagation(); hearPhrase(k, "aroha"); }}>↑ Aroha</button>
              <button className="mini" onClick={(e) => { e.stopPropagation(); hearPhrase(k, "avaroha"); }}>↓ Avaroha</button>
              <button className="mini" onClick={(e) => { e.stopPropagation(); hearPhrase(k, "pakad"); }}>✨ Pakad</button>
              <button className="mini" onClick={(e) => { e.stopPropagation(); hearBird(k); }}>🐦 Bird</button>
            </div>
          </div>
        ))}
      </div>
      <div className="panel">
        <div className="lesson-head">
          <strong>🎹 {raga.name} in {s.key}: play it yourself</strong>
          <label className="keypick">Key (Sa =)
            <select value={s.key} onChange={(e) => setKey(e.target.value)}>
              {KEYS.map((k) => <option key={k}>{k}</option>)}
            </select>
          </label>
        </div>
        <div className="raga-facts">
          <div><em>Aroha ↑</em><code>{raga.aroha.join(" ")}</code></div>
          <div><em>Avaroha ↓</em><code>{raga.avaroha.join(" ")}</code></div>
          <div><em>Pakad</em><code>{raga.pakad.join(" ")}</code></div>
          <div><em>Vadi / Samvadi</em><code>{raga.vadi ? `${raga.vadi} / ${raga.samvadi}` : "—"}</code></div>
        </div>
        <Piano keyName={s.key} notes={raga.notes} typing={active} />
        <p className="help">Glowing keys belong to the raga. Click them, or type A W S E D F T G Y H U J K to play from Sa.</p>
      </div>

      <Step n="3" title="Pick a rhythm cycle (tala) and tempo" />
      <div className="row">
        {Object.entries(opts.talas).map(([k, t]) => (
          <button key={k} className={s.tala === k ? "chip tall on" : "chip tall"} onClick={() => set({ tala: k })}>
            <span>{t.name} · {t.matras} beats</span>
            <small>{t.vibhags.join(" + ")} · {t.western.split(",")[0]}</small>
          </button>
        ))}
      </div>
      <div className="grid2">
        <Slider label="Tempo" value={s.bpm} min={40} max={160} onChange={(v) => set({ bpm: v })} fmt={(v) => `${v} bpm`} />
        <button className="chip" onClick={() => setShowTala((x) => !x)}>
          {showTala ? "Hide" : "Show"} the {tala.name} wheel 🥁
        </button>
      </div>
      {showTala && active && <div className="panel"><TalaCircle key={`${s.tala}-${s.bpm}`} tala={tala} bpm={s.bpm} keyName={s.key} /></div>}

      <Step n="4" title="Pick a composing method and chords" />
      <div className="row">
        {Object.entries(opts.templates).map(([k, t]) => (
          <button key={k} className={s.template === k ? "chip on" : "chip"} onClick={() => set({ template: k })}>{t.name}</button>
        ))}
      </div>
      <div className="callout">
        <strong>🎶 {tpl.idea}</strong>
        <ol>{tpl.steps.map((x) => <li key={x}>{x}</li>)}</ol>
      </div>
      <div className="row" style={{ marginTop: 12 }}>
        <button className={s.progression === "auto" ? "chip small on" : "chip small"} onClick={() => set({ progression: "auto" })}>🎲 Surprise</button>
        {Object.entries(opts.progressions).map(([k, p]) => (
          <button key={k} className={s.progression === k ? "chip small on" : "chip small"} title={p.idea}
                  onClick={() => set({ progression: k })}>{p.name}</button>
        ))}
      </div>
      <p className="help">{s.progression === "auto" ? "A progression is picked for you. The chords are named in the score after composing." : opts.progressions[s.progression].idea}</p>

      <Step n="5" title="Choose nature instruments and mix them" />
      <div className="mixer">
        {Object.keys(opts.layers).map((l) => {
          const on = s.layers.includes(l);
          return (
            <div key={l} className={on ? "strip on" : "strip"}>
              <button className="strip-btn" title={opts.layers[l]} onClick={() => toggle(l)} aria-pressed={on}>
                <span className="icon">{ICONS[l]}</span>
                <span>{l}</span>
                <small>{LIKE[l][0]} {LIKE[l][1]}</small>
              </button>
              <input type="range" min="0" max="2" step="0.05" value={vol(l)} disabled={!on}
                     aria-label={`${l} volume`}
                     onChange={(e) => set({ volumes: { ...s.volumes, [l]: +e.target.value } })} />
              <span className="vol">{on ? `${Math.round(vol(l) * 100)}%` : "off"}</span>
            </div>
          );
        })}
      </div>
      <p className="help">Tap an instrument to turn it on or off; drag its fader to balance the mix. Hover for its musical role.</p>

      <Step n="6" title="Studio settings" />
      <div className="grid3">
        <Slider label="Length" value={s.duration} min={15} max={120} step={5} onChange={(v) => set({ duration: v })} fmt={(v) => `${v}s`} />
        <Slider label="Reverb (space)" value={s.reverb} min={0} max={0.7} step={0.05} onChange={(v) => set({ reverb: v })} fmt={(v) => `${Math.round(v * 100)}%`} />
        <Slider label="Humanize" value={s.humanize} min={0} max={1} step={0.05} onChange={(v) => set({ humanize: v })} fmt={(v) => `${Math.round(v * 100)}%`} />
        <Slider label="Swing" value={s.swing} min={0} max={1} step={0.05} onChange={(v) => set({ swing: v })} fmt={(v) => `${Math.round(v * 100)}%`} />
        <label className="slider">
          <span>Seed {s.lockSeed ? "🔒 locked" : "🎲 new each time"}</span>
          <span className="row">
            <input className="seed" inputMode="numeric" value={s.seed} placeholder="random"
                   onChange={(e) => set({ seed: e.target.value.replace(/\D/g, "").slice(0, 10), lockSeed: true })} />
            <button className={s.lockSeed ? "mini on" : "mini"} onClick={() => set({ lockSeed: !s.lockSeed })}>
              {s.lockSeed ? "Unlock" : "Lock"}
            </button>
          </span>
        </label>
      </div>
      <p className="help">Lock the seed to keep the same melody while you change the mix, reverb or instruments.</p>

      <button className="go" onClick={() => compose()} disabled={busy || s.layers.length === 0}>
        {busy ? "🎼 Composing…" : "🎵 Compose new music"}
      </button>
      {error && <p className="error">{error}</p>}

      {track && (
        <section className="player">
          <div className="now-playing">
            <div className={playing ? "eq on" : "eq"} aria-hidden="true"><i /><i /><i /><i /><i /></div>
            <p>
              <strong>{opts.moods[track.mood].label}</strong> · {opts.ragas[track.scale].name} in {track.key} ·{" "}
              {opts.talas[track.tala].name} · {opts.templates[track.template].name} · {track.bpm} bpm · seed {track.seed}
            </p>
          </div>
          <div className="controls">
            <audio ref={audioRef} controls src={`${API}${track.url}`}
                   onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)}
                   onEnded={() => setPlaying(false)} onTimeUpdate={(e) => setTime(e.currentTarget.currentTime)} />
            <button className="stop" onClick={stop} title="Stop and rewind to the start">⏹ Stop</button>
          </div>
          <div className="row downloads">
            <a className="chip" href={`${API}${track.url}`} download>⬇️ Audio (WAV)</a>
            <a className="chip" href={`${API}${track.midi_url}`} download>🎹 MIDI for your DAW</a>
          </div>
          <div className="tabs small">
            {[["roll", "🎹 Piano roll"], ["score", "📜 Score"], ["explain", "🎧 What am I hearing?"]].map(([k, l]) => (
              <button key={k} className={view === k ? "tab on" : "tab"} onClick={() => setView(k)}>{l}</button>
            ))}
          </div>
          {view === "roll" && <PianoRoll track={track} audioRef={audioRef} />}
          {view === "score" && <Score track={track} currentBar={currentBar} />}
          {view === "explain" && track.explain.map((x) => (
            <div key={x.title} className="explain">
              <strong>{x.title}</strong>
              <p>{x.text}</p>
            </div>
          ))}
        </section>
      )}

      {history.length > 0 && (
        <section className="history">
          <h3>🕘 Recent compositions</h3>
          <p className="help">Load one to get the exact same music back (same settings and seed), then tweak it.</p>
          <ul>
            {history.map((h) => (
              <li key={h.at}>
                <span>{h.label} · {h.duration}s · seed {h.seed}</span>
                <span className="row">
                  <button className="mini" onClick={() => { setS(h); setKeyName(h.key); }}>Load</button>
                  <button className="mini" onClick={() => { setS(h); setKeyName(h.key); compose(h); }}>▶ Recompose</button>
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
