import { useEffect, useState } from "react";
import "./App.css";
import EarTraining from "./components/EarTraining";
import Glossary from "./components/Glossary";
import Learn from "./components/Learn";
import Studio from "./components/Studio";
import { API } from "./lib/api";
import { stopAll } from "./lib/audio";
import { load, save } from "./lib/store";

const BAND = [["🎹", "Piano"], ["🎷", "Saxophone"], ["🥁", "Drums"], ["🎺", "Trumpet"], ["🎸", "Guitar"],
  ["🎻", "Violin"], ["🪘", "Tabla"], ["🪗", "Accordion"], ["🎤", "Voice"], ["🎧", "Listen"]];
const FLOATERS = ["♪", "♫", "♬", "𝄞", "♩", "♪", "♫", "𝄞", "♬", "♩"];
const TABS = [
  ["studio", "🎼 Studio", "Compose"],
  ["learn", "📚 Learn", "10 lessons"],
  ["ear", "👂 Ear training", "5 games"],
  ["glossary", "📖 Glossary", "Terms A–Z"],
];

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

export default function App() {
  const [opts, setOpts] = useState(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState(() => load("tab", "studio"));
  const [keyName, setKeyName] = useState("A");

  useEffect(() => {
    fetch(`${API}/api/options`)
      .then((r) => r.json())
      .then(setOpts)
      .catch(() => setError("Backend not reachable. Start it with: uv run nature-music-app"));
  }, []);

  const go = (t) => { stopAll(); setTab(t); save("tab", t); };

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
          <p className="sub">Compose with ragas, talas and chords played by birds, rain, rivers and wind, and learn how music works while you do it.</p>
          <div className="band" aria-hidden="true">
            {BAND.map(([e, name], i) => (
              <span key={name} title={name} style={{ animationDelay: `${i * 0.2}s` }}>{e}</span>
            ))}
          </div>
        </header>

        <nav className="tabs" aria-label="Sections">
          {TABS.map(([k, label, sub]) => (
            <button key={k} className={tab === k ? "tab on" : "tab"} onClick={() => go(k)} aria-current={tab === k}>
              {label}<small>{sub}</small>
            </button>
          ))}
        </nav>

        {!opts && <p className={error ? "error" : "help"}>{error || "Loading…"}</p>}
        {opts && (
          <>
            <div hidden={tab !== "studio"}><Studio opts={opts} setKeyName={setKeyName} active={tab === "studio"} /></div>
            {tab === "learn" && <Learn opts={opts} keyName={keyName} setKeyName={setKeyName} />}
            {tab === "ear" && <EarTraining opts={opts} keyName={keyName} />}
            {tab === "glossary" && <Glossary />}
          </>
        )}
        <footer className="foot">
          All sounds are synthesized in code. Export MIDI to continue in GarageBand, FL Studio, Reaper, Ableton, Logic or MuseScore.
        </footer>
      </main>
    </>
  );
}
