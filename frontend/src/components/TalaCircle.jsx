import { useEffect, useRef, useState } from "react";
import { bol, stopAll } from "../lib/audio";
import { saMidi } from "../lib/theory";

function starts(vibhags) {
  const out = [];
  vibhags.reduce((pos, v) => { out.push(pos); return pos + v; }, 0);
  return out;
}

/** An interactive tala wheel: hear the theka, see sam (X), khali (0) and claps.
 *  Remount it (change its key) to reset the tempo from `bpm`. */
export default function TalaCircle({ tala, bpm = 90, keyName = "C" }) {
  const [running, setRunning] = useState(false);
  const [beat, setBeat] = useState(-1);
  const [tempo, setTempo] = useState(bpm);
  const timer = useRef(null);
  const n = tala.matras;
  const vib = starts(tala.vibhags);
  const clapAt = Object.fromEntries(vib.map((s, i) => [s, tala.claps[i]]));

  useEffect(() => {
    if (!running) return undefined;
    const stepMs = 60000 / tempo / 2; // one matra = an 8th note
    let i = 0;
    let next = performance.now();
    const tick = () => {
      const s = i % n;
      bol(tala.theka[s], saMidi(keyName), s === 0);
      setBeat(s);
      i += 1;
      next += stepMs;
      timer.current = setTimeout(tick, Math.max(0, next - performance.now()));
    };
    tick();
    return () => { clearTimeout(timer.current); setBeat(-1); };
  }, [running, tempo, tala, n, keyName]);

  useEffect(() => () => stopAll(), []);

  const R = 110;
  return (
    <div className="tala">
      <svg viewBox="-150 -150 300 300" className="tala-wheel" role="img"
           aria-label={`${tala.name}: ${n} beats in groups of ${tala.vibhags.join(", ")}`}>
        <circle r={R} className="tala-ring" />
        {tala.theka.map((b, s) => {
          const a = (s / n) * 2 * Math.PI - Math.PI / 2;
          const x = R * Math.cos(a);
          const y = R * Math.sin(a);
          const clap = clapAt[s];
          const cls = ["tala-dot", s === beat && "now", clap === "X" && "sam", clap === "0" && "khali"]
            .filter(Boolean).join(" ");
          return (
            <g key={s}>
              <circle cx={x} cy={y} r={s === beat ? 17 : 14} className={cls} />
              <text x={x} y={y + 4} className="tala-bol">{b}</text>
              {clap && (
                <text x={(R + 30) * Math.cos(a)} y={(R + 30) * Math.sin(a) + 5} className="tala-clap">{clap}</text>
              )}
            </g>
          );
        })}
        <text y="-6" className="tala-name">{tala.name}</text>
        <text y="16" className="tala-count">{beat >= 0 ? `beat ${beat + 1} / ${n}` : `${n} beats`}</text>
      </svg>
      <div className="tala-side">
        <div className="theka">
          {vib.map((s, gi) => (
            <span key={s} className="vibhag">
              <em>{tala.claps[gi]}</em>
              {tala.theka.slice(s, s + tala.vibhags[gi]).map((b, j) => (
                <i key={j} className={s + j === beat ? "now" : ""}>{b}</i>
              ))}
            </span>
          ))}
        </div>
        <p className="help">{tala.about}</p>
        <p className="help"><strong>Western:</strong> {tala.western}</p>
        <label className="slider">
          <span>Tempo {tempo} bpm</span>
          <input type="range" min="40" max="200" value={tempo} onChange={(e) => setTempo(+e.target.value)} />
        </label>
        <button className={running ? "chip on" : "chip"} onClick={() => setRunning((r) => !r)}>
          {running ? "⏸ Stop the cycle" : "▶ Play the cycle"}
        </button>
        <p className="help">Clap on X and the numbers, wave your hand on 0. Count the beats out loud.</p>
      </div>
    </div>
  );
}
