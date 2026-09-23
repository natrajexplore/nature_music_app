import { useState } from "react";
import { chord, pluck, sequence } from "../lib/audio";
import { SARGAM, saMidi, shuffle, tokenSemi } from "../lib/theory";
import { load, save } from "../lib/store";

const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const SHUDDHA = ["Sa", "Re", "Ga", "Ma", "Pa", "Dha", "Ni"];
const CHORDS = { major: [0, 4, 7], minor: [0, 3, 7], diminished: [0, 3, 6], augmented: [0, 4, 8] };

const GAMES = {
  updown: {
    name: "Higher or lower?", icon: "↕️", level: "Starter",
    help: "Two notes play. Is the second one higher or lower than the first?",
    make: (sa) => {
      const a = sa + Math.floor(Math.random() * 12);
      let b = a;
      while (b === a) b = sa + Math.floor(Math.random() * 12);
      return { play: () => sequence([a, b], 0.7), options: ["Higher", "Lower"], answer: b > a ? "Higher" : "Lower" };
    },
  },
  note: {
    name: "Name the note", icon: "🎯", level: "Beginner",
    help: "Sa plays first, then a mystery note from the 7 shuddha notes. Which one is it? Sing Sa Re Ga… up to it in your head.",
    make: (sa) => {
      const n = pick(SHUDDHA.slice(1));
      const m = sa + SARGAM.indexOf(n);
      return { play: () => sequence([sa, null, m], 0.5, 1), options: SHUDDHA.slice(1), answer: n };
    },
  },
  chromatic: {
    name: "Name any of 12", icon: "🧠", level: "Advanced",
    help: "Like 'Name the note', but komal and tivra notes can appear too.",
    make: (sa) => {
      const n = pick(SARGAM.slice(1));
      return { play: () => sequence([sa, null, sa + SARGAM.indexOf(n)], 0.5, 1), options: SARGAM.slice(1), answer: n };
    },
  },
  chord: {
    name: "Chord colour", icon: "🎨", level: "Intermediate",
    help: "A chord plays. Is it major (bright), minor (soft/sad), diminished (tense) or augmented (dreamy, unresolved)?",
    make: (sa) => {
      const q = pick(Object.keys(CHORDS));
      const root = sa + Math.floor(Math.random() * 7);
      return { play: () => chord(CHORDS[q].map((s) => root + s), 0, 0.05), options: Object.keys(CHORDS), answer: q };
    },
  },
  raga: {
    name: "Which raga?", icon: "🎼", level: "Intermediate",
    help: "A raga's aroha and avaroha play. Pick the right one. Tip: listen for komal (dark) notes and which notes are missing.",
    make: (sa, opts) => {
      const keys = shuffle(Object.keys(opts.ragas)).slice(0, 3);
      const k = pick(keys);
      const r = opts.ragas[k];
      const seq = [...r.aroha, ...r.avaroha.slice(1)].map((t) => sa + tokenSemi(t));
      return { play: () => sequence(seq, 0.32, 0.8), options: keys.map((x) => opts.ragas[x].name), answer: r.name };
    },
  },
};

export default function EarTraining({ opts, keyName }) {
  const [game, setGame] = useState("updown");
  const [q, setQ] = useState(null);
  const [guess, setGuess] = useState(null);
  const [score, setScore] = useState({ right: 0, total: 0, streak: 0 });
  const [best, setBest] = useState(() => load("ear-best", {}));
  const sa = saMidi(keyName);
  const g = GAMES[game];

  const next = () => {
    const nq = g.make(sa, opts);
    setQ(nq);
    setGuess(null);
    nq.play();
  };

  const answer = (o) => {
    if (guess != null) return;
    setGuess(o);
    const ok = o === q.answer;
    const s = { right: score.right + ok, total: score.total + 1, streak: ok ? score.streak + 1 : 0 };
    setScore(s);
    if (s.streak > (best[game] || 0)) {
      const nb = { ...best, [game]: s.streak };
      setBest(nb);
      save("ear-best", nb);
    }
  };

  const choose = (k) => {
    setGame(k);
    setQ(null);
    setGuess(null);
    setScore({ right: 0, total: 0, streak: 0 });
  };

  return (
    <div className="ear">
      <div className="cards games">
        {Object.entries(GAMES).map(([k, v]) => (
          <button key={k} className={game === k ? "card on" : "card"} onClick={() => choose(k)}>
            <span className="icon">{v.icon}</span>
            <strong>{v.name}</strong>
            <span className="meta">{v.level} · best streak {best[k] || 0}</span>
          </button>
        ))}
      </div>
      <div className="panel">
        <p>{g.help}</p>
        <div className="row">
          <button className="chip" onClick={() => pluck(sa, 0, 1.4)}>🔈 Reference Sa ({keyName})</button>
          {!q && <button className="chip on" onClick={next}>▶ Start</button>}
          {q && <button className="chip" onClick={q.play}>🔁 Play again</button>}
          {q && guess != null && <button className="chip on" onClick={next}>Next →</button>}
        </div>
        {q && (
          <div className="row answers">
            {q.options.map((o) => (
              <button key={o} onClick={() => answer(o)}
                      className={`chip big${guess != null && o === q.answer ? " good" : ""}${guess === o && o !== q.answer ? " bad" : ""}`}>
                {o}
              </button>
            ))}
          </div>
        )}
        {guess != null && (
          <p className={guess === q.answer ? "ok" : "error"}>
            {guess === q.answer ? "🎉 Correct!" : `The answer was ${q.answer}.`}
          </p>
        )}
        <p className="help">Score {score.right} / {score.total} · Streak {score.streak} 🔥</p>
      </div>
    </div>
  );
}
