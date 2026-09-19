import { useEffect, useRef, useState } from "react";
import "./App.css";

const API = "http://localhost:8001";
const ICONS = { bird: "🐦", droplet: "💧", cricket: "🦗", rain: "🌧️", fire: "🔥", thunder: "⚡", river: "🌊", wind: "🍃" };

export default function App() {
  const [opts, setOpts] = useState(null);
  const [mood, setMood] = useState("dawn");
  const [raga, setRaga] = useState("bhupali");
  const [template, setTemplate] = useState("free");
  const [duration, setDuration] = useState(45);
  const [layers, setLayers] = useState([]);
  const [track, setTrack] = useState(null);
  const [busy, setBusy] = useState(false);
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
  };

  const toggle = (l) =>
    setLayers((cur) => (cur.includes(l) ? cur.filter((x) => x !== l) : [...cur, l]));

  const hear = (key, instrument) => {
    previewRef.current?.pause();
    previewRef.current = new Audio(`${API}/api/scale/${key}.wav?instrument=${instrument}`);
    previewRef.current.play();
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
    <main>
      <h1>🌿 Nature Orchestra</h1>
      <p className="sub">Compose music from birds, rain, fire, river and wind, and learn how it works.</p>

      <h2><span className="num">1</span> Pick a feeling</h2>
      <div className="row">
        {Object.entries(opts.moods).map(([k, m]) => (
          <button key={k} className={mood === k ? "chip on" : "chip"} onClick={() => pickMood(k)}>
            {m.label}
          </button>
        ))}
      </div>

      <h2><span className="num">2</span> Pick a raga (the notes you can use)</h2>
      <p className="help">{opts.sargam_help}</p>
      <div className="cards">
        {Object.entries(opts.ragas).map(([k, r]) => (
          <div key={k} className={raga === k ? "card on" : "card"} onClick={() => setRaga(k)}>
            <strong>{r.name}</strong>
            <div className="notes">{r.notes.join(" ")}</div>
            <div className="meta">{r.time} · {r.feeling}</div>
            <div className="desc">{r.sound}</div>
            <div className="row">
              <button className="mini" onClick={(e) => { e.stopPropagation(); hear(k, "droplet"); }}>
                💧 Hear scale
              </button>
              <button className="mini" onClick={(e) => { e.stopPropagation(); hear(k, "bird"); }}>
                🐦 Hear scale
              </button>
            </div>
          </div>
        ))}
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
        <strong>{tpl.idea}</strong>
        <ol>{tpl.steps.map((s) => <li key={s}>{s}</li>)}</ol>
      </div>

      <h2><span className="num">4</span> Choose nature instruments</h2>
      <div className="row">
        {Object.keys(opts.layers).map((l) => (
          <button key={l} className={layers.includes(l) ? "chip on" : "chip"}
                  title={opts.layers[l]} onClick={() => toggle(l)}>
            {ICONS[l]} {l}
          </button>
        ))}
      </div>
      <p className="help">Tap an instrument to turn it on or off. Hover to see its musical role.</p>

      <h2>Length: {duration}s</h2>
      <input type="range" min="15" max="120" step="5" value={duration}
             onChange={(e) => setDuration(+e.target.value)} />

      <button className="go" onClick={compose} disabled={busy || layers.length === 0}>
        {busy ? "Composing…" : "Compose new music"}
      </button>
      {error && <p className="error">{error}</p>}

      {track && (
        <section className="player">
          <p>
            {opts.moods[track.mood].label} · {opts.ragas[track.scale].name} ·{" "}
            {opts.templates[track.template].name} · {track.bpm} bpm · seed {track.seed}
          </p>
          <audio ref={audioRef} controls src={`${API}${track.url}`} />
          <a href={`${API}${track.url}`} download>Download WAV</a>
          <h3>What am I hearing?</h3>
          {track.explain.map((x) => (
            <div key={x.title} className="explain">
              <strong>{x.title}</strong>
              <p>{x.text}</p>
            </div>
          ))}
        </section>
      )}
    </main>
  );
}
