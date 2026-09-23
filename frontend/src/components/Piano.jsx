import { useEffect, useState } from "react";
import { pluck } from "../lib/audio";
import { SARGAM, isBlack, noteName, saMidi } from "../lib/theory";

// Computer keys that play the notes from Sa upward, like a DAW's typing keyboard.
const TYPING = ["a", "w", "s", "e", "d", "f", "t", "g", "y", "h", "u", "j", "k", "o", "l", "p", ";"];

/**
 * A playable 2-octave keyboard starting at Sa of the chosen key.
 * Raga notes glow; every key shows its sargam and Western name.
 */
export default function Piano({ keyName = "C", notes = [], typing = false, onPlay }) {
  const sa = saMidi(keyName);
  const start = isBlack(sa) ? sa - 1 : sa;
  const end = isBlack(sa + 24) ? sa + 25 : sa + 24;
  const midis = [];
  for (let m = start; m <= end; m++) midis.push(m);
  const whites = midis.filter((m) => !isBlack(m));
  const lit = new Set(notes.map((n) => SARGAM.indexOf(n)));
  const [down, setDown] = useState(null);

  const play = (m) => {
    pluck(m);
    setDown(m);
    setTimeout(() => setDown((d) => (d === m ? null : d)), 220);
    onPlay?.(m);
  };

  useEffect(() => {
    if (!typing) return undefined;
    const onKey = (e) => {
      if (e.repeat || e.ctrlKey || e.metaKey || /input|select|textarea/i.test(e.target.tagName)) return;
      const i = TYPING.indexOf(e.key.toLowerCase());
      if (i >= 0) play(sa + i);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const w = 100 / whites.length;
  const label = (m) => {
    const rel = m - sa;
    const pc = ((rel % 12) + 12) % 12;
    const name = SARGAM[pc];
    return rel < 0 ? "." + name : rel >= 12 ? name + "'" : name;
  };

  return (
    <div className="piano" role="group" aria-label={`Piano in ${keyName}`}>
      {whites.map((m) => {
        const pc = (((m - sa) % 12) + 12) % 12;
        const on = lit.has(pc);
        return (
          <button key={m} className={`wkey${on ? " lit" : ""}${pc === 0 ? " sa" : ""}${down === m ? " down" : ""}`}
                  onClick={() => play(m)} aria-label={`${noteName(m)} ${label(m)}`}>
            {on && <b>{label(m)}</b>}
            <small>{noteName(m).replace(/\d/, "")}</small>
          </button>
        );
      })}
      {midis.filter(isBlack).map((m) => {
        const pc = (((m - sa) % 12) + 12) % 12;
        const idx = whites.filter((x) => x < m).length;
        const on = lit.has(pc);
        return (
          <button key={m} className={`bkey${on ? " lit" : ""}${down === m ? " down" : ""}`}
                  style={{ left: `${idx * w - w * 0.3}%`, width: `${w * 0.6}%` }}
                  onClick={() => play(m)} aria-label={`${noteName(m)} ${label(m)}`}>
            {on && <b>{label(m)}</b>}
          </button>
        );
      })}
    </div>
  );
}
