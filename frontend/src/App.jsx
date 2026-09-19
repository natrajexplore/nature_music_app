import { useEffect, useRef, useState } from "react";
import "./App.css";

const API = "http://localhost:8001";
const ICONS = { bird: "🐦", droplet: "💧", cricket: "🦗", rain: "🌧️", fire: "🔥", thunder: "⚡", river: "🌊", wind: "🍃" };
// The real instrument each nature sound acts like in the music.
const LIKE = {
  bird: ["🎷", "saxophone lead"], droplet: ["🎹", "piano chords"], cricket: ["🔔", "bells"],
  rain: ["🥁", "hi-hat"], fire: ["🥁", "snare"], thunder: ["🥁", "bass drum"],
  river: ["🎻", "cello drone"], wind: ["🎺", "horn section"],
};
const BAND = [["🎹", "Piano"], ["🎷", "Saxophone"], ["🥁", "Drums"], ["🎺", "Trumpet"], ["🎸", "Guitar"],
  ["🎻", "Violin"], ["🪕", "Banjo"], ["🪗", "Accordion"], ["🎤", "Voice"], ["🎧", "Listen"]];
const FLOATERS = ["♪", "♫", "♬", "𝄞", "♩", "♪", "♫", "𝄞", "♬", "♩"];

// Semitone of each sargam note above Sa, used to light the piano keys.
const SEMI = { Sa: 0, re: 1, Re: 2, ga: 3, Ga: 4, Ma: 5, "Ma#": 6, Pa: 7, dha: 8, Dha: 9, ni: 10, Ni: 11 };
const WHITE = [0, 2, 4, 5, 7, 9, 11, 12];
const BLACK = [[1, 0], [3, 1], [6, 3], [8, 4], [10, 5]]; // [semitone, white key on its left]

function Logo() {
  return (
    <svg viewBox="0 0 64 64" width="56" height="56" role="img" aria-label="Nature Orchestra logo">
      <circle cx="32" cy="32" r="30" fill="#2e7d4f" />
      <ellipse cx="22" cy="44" rx="8" ry="6" transform="rotate(-20 22 44)" fill="#fff" />
      <rect x="28" y="14" width="4" height="30" rx="2" fill="#fff" />
      <path d="M32 14c9 2 13 8 10 17-2-6-5-9-10-10z" fill="#fff" />
      <path d="M38 52c11 0 18-6 18-17-11 0-18 6-18 17z" fill="#a6e3a1" />
    </svg>
  );
}

function Piano({ notes }) {
  const lit = { 12: "Sa" };
  notes.forEach((n) => { lit[SEMI[n]] = n; });
  return (
    <div className="piano" role="img" aria-label={`Piano keys for ${notes.join(" ")}`}>
      {WHITE.map((s) => (
        <div key={s} className={lit[s] ? "wkey lit" : "wkey"}>{lit[s]}</div>
      ))}
      {BLACK.map(([s, i]) => (
        <div key={s} className={lit[s] ? "bkey lit" : "bkey"} style={{ left: `${(i + 1) * 12.5 - 2.6}%` }}>
          {lit[s]}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [opts, setOpts] = useState(null);
  const [mood, setMood] = useState("dawn");
  const [raga, setRaga] = useState("bhupali");
  const [template, setTemplate] = useState("free");
  const [duration, setDuration] = useState(45);
  const [layers, setLayers] = useState([]);
  const [track, setTrack] = useState(null);
  const [busy, setBusy] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState("");
  const audioRef = useRef(null);
  const previewRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/api/options`)
      .then((r) => r.json())
      .then((o) => { setOpts(o); setLayers(o.moods.dawn.layers); })
      .catch(() => setError("Backend not reachable. Run: uv run nature-music-app"));
  }, []);

  const pickMood = (key) => {
    setMood(key);
    setRaga(opts.moods[key].scale);
    setLayers(opts.moods[key].layers);
    setTemplate(opts.moods[key].template);
  };

  const toggle = (l) =>
    setLayers((cur) => (cur.includes(l) ? cur.filter((x) => x !== l) : [...cur, l]));

  const hear = (key, instrument) => {
    previewRef.current?.pause();
    previewRef.current = new Audio(`${API}/api/scale/${key}.wav?instrument=${instrument}`);
    previewRef.current.play();
  };

  const stop = () => {
    const a = audioRef.current;
    if (a) {
      a.pause();
      a.currentTime = 0;
    }
  };

  const compose = async () => {
    previewRef.current?.pause();
    setBusy(true);
    setError("");
    try {
      const res = await fetch(`${API}/api/compose`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mood, scale: raga, template, duration, layers }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Compose failed");
      setTrack(await res.json());
      setTimeout(() => audioRef.current?.play(), 100);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (!opts) return <main><p className="error">{error || "Loading…"}</p></main>;

  const tpl = opts.templates[template];

  return (
    <>
      <div className="notes-bg" aria-hidden="true">
        {FLOATERS.map((n, i) => (
          <span key={i} style={{ left: `${5 + i * 10}%`, fontSize: `${28 + (i % 4) * 14}px`,
            animationDuration: `${16 + (i % 5) * 4}s`, animationDelay: `${-i * 3}s` }}>{n}</span>
        ))}
      </div>
      <main>
        <header className="hero">
          <div className="brand">
            <Logo />
            <h1>Nature Orchestra</h1>
          </div>
          <p className="sub">Compose music from birds, rain, fire, river and wind, and learn how it works.</p>
          <div className="band" aria-hidden="true">
            {BAND.map(([e, name], i) => (
              <span key={name} title={name} style={{ animationDelay: `${i * 0.2}s` }}>{e}</span>
            ))}
          </div>
        </header>

        <h2><span className="num">1</span> Pick a real-life scenario</h2>
        <p className="help">Choose the moment you want music for. It sets a matching raga, tempo, instruments and method, which you can change below.</p>
        <div className="cards scenarios">
          {Object.entries(opts.moods).map(([k, m]) => (
            <button key={k} className={mood === k ? "card scenario on" : "card scenario"} onClick={() => pickMood(k)}>
              <span className="icon">{m.icon}</span>
              <strong>{m.label}</strong>
              <span className="desc">{m.story}</span>
              <span className="meta">{opts.ragas[m.scale].name} · {m.bpm} bpm</span>
            </button>
          ))}
        </div>

        <h2><span className="num">2</span> Pick a raga (the notes you can use)</h2>
        <p className="help">{opts.sargam_help}</p>
        <div className="cards">
          {Object.entries(opts.ragas).map(([k, r]) => (
            <div key={k} className={raga === k ? "card on" : "card"} onClick={() => setRaga(k)}>
              <strong>🎼 {r.name}</strong>
              <div className="notes">{r.notes.join(" ")}</div>
              <div className="meta">{r.time} · {r.feeling}</div>
              <div className="desc">{r.sound}</div>
              <div className="row">
                <button className="mini" onClick={(e) => { e.stopPropagation(); hear(k, "droplet"); }}>
                  🎹 Hear scale
                </button>
                <button className="mini" onClick={(e) => { e.stopPropagation(); hear(k, "bird"); }}>
                  🎷 Hear scale
                </button>
              </div>
            </div>
          ))}
        </div>
        <div className="piano-wrap">
          <strong>🎹 {opts.ragas[raga].name} on a piano</strong>
          <p className="help">Green keys are the notes of this raga. Sa is the home note (C).</p>
          <Piano notes={opts.ragas[raga].notes} />
        </div>

        <h2><span className="num">3</span> Pick a composing method</h2>
        <div className="row">
          {Object.entries(opts.templates).map(([k, t]) => (
            <button key={k} className={template === k ? "chip on" : "chip"} onClick={() => setTemplate(k)}>
              {t.name}
            </button>
          ))}
        </div>
        <div className="callout">
          <strong>🎶 {tpl.idea}</strong>
          <ol>{tpl.steps.map((s) => <li key={s}>{s}</li>)}</ol>
        </div>

        <h2><span className="num">4</span> Choose nature instruments</h2>
        <div className="row">
          {Object.keys(opts.layers).map((l) => (
            <button key={l} className={layers.includes(l) ? "chip tall on" : "chip tall"}
                    title={opts.layers[l]} onClick={() => toggle(l)}>
              <span>{ICONS[l]} {l}</span>
              <small>acts like {LIKE[l][0]} {LIKE[l][1]}</small>
            </button>
          ))}
        </div>
        <p className="help">Tap an instrument to turn it on or off.</p>

        <h2>⏱️ Length: {duration}s</h2>
        <input type="range" min="15" max="120" step="5" value={duration}
               onChange={(e) => setDuration(+e.target.value)} />

        <button className="go" onClick={compose} disabled={busy || layers.length === 0}>
          {busy ? "🎼 Composing…" : "🎵 Compose new music"}
        </button>
        {error && <p className="error">{error}</p>}

        {track && (
          <section className="player">
            <div className="now">
              <div className={playing ? "eq on" : "eq"} aria-hidden="true"><i /><i /><i /><i /><i /></div>
              <p>
                {opts.moods[track.mood].label} · {opts.ragas[track.scale].name} ·{" "}
                {opts.templates[track.template].name} · {track.bpm} bpm · seed {track.seed}
              </p>
            </div>
            <div className="controls">
              <audio ref={audioRef} controls src={`${API}${track.url}`}
                     onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)}
                     onEnded={() => setPlaying(false)} />
              <button className="stop" onClick={stop} title="Stop and rewind to the start">⏹ Stop</button>
            </div>
            <a href={`${API}${track.url}`} download>⬇️ Download WAV</a>
            <h3>🎧 What am I hearing?</h3>
            {track.explain.map((x) => (
              <div key={x.title} className="explain">
                <strong>{x.title}</strong>
                <p>{x.text}</p>
              </div>
            ))}
          </section>
        )}
      </main>
    </>
  );
}
