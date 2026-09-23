import { useState } from "react";
import { LESSONS } from "../data/lessons";
import { sequence } from "../lib/audio";
import { KEYS, saMidi, tokenSemi } from "../lib/theory";
import { load, save } from "../lib/store";
import Piano from "./Piano";
import TalaCircle from "./TalaCircle";

function Quiz({ quiz, done, onPass }) {
  const [pick, setPick] = useState(null);
  const right = pick === quiz.answer;
  return (
    <div className="quiz">
      <strong>✅ Quick check: {quiz.q}</strong>
      <div className="row">
        {quiz.options.map((o, i) => (
          <button key={o}
                  className={`chip${pick === i ? (right ? " good" : " bad") : ""}${done && i === quiz.answer && pick == null ? " good" : ""}`}
                  onClick={() => { setPick(i); if (i === quiz.answer) onPass(); }}>
            {o}
          </button>
        ))}
      </div>
      {pick != null && <p className={right ? "ok" : "error"}>{right ? "Correct! " : "Not quite. "}{quiz.why}</p>}
    </div>
  );
}

function RagaExplorer({ opts, keyName }) {
  const [raga, setRaga] = useState("yaman");
  const r = opts.ragas[raga];
  const sa = saMidi(keyName);
  const play = (field) => sequence(r[field].map((t) => sa + tokenSemi(t)), field === "pakad" ? 0.36 : 0.42);
  return (
    <div className="widget">
      <div className="row">
        {Object.entries(opts.ragas).map(([k, v]) => (
          <button key={k} className={raga === k ? "chip small on" : "chip small"} onClick={() => setRaga(k)}>{v.name}</button>
        ))}
      </div>
      <div className="raga-facts">
        <div><em>Aroha ↑</em><code>{r.aroha.join(" ")}</code><button className="mini" onClick={() => play("aroha")}>▶</button></div>
        <div><em>Avaroha ↓</em><code>{r.avaroha.join(" ")}</code><button className="mini" onClick={() => play("avaroha")}>▶</button></div>
        <div><em>Pakad</em><code>{r.pakad.join(" ")}</code><button className="mini" onClick={() => play("pakad")}>▶</button></div>
        <div><em>Vadi / Samvadi</em><code>{r.vadi ? `${r.vadi} / ${r.samvadi}` : "not used for this scale"}</code></div>
        <div><em>Time · Mood</em><span>{r.time} · {r.feeling}</span></div>
      </div>
      <Piano keyName={keyName} notes={r.notes} />
    </div>
  );
}

export default function Learn({ opts, keyName, setKeyName }) {
  const [open, setOpen] = useState(LESSONS[0].id);
  const [done, setDone] = useState(() => load("lessons-done", []));
  const [tala, setTala] = useState("teentaal");
  const lesson = LESSONS.find((l) => l.id === open);
  const sa = saMidi(keyName);

  const pass = (id) => {
    if (done.includes(id)) return;
    const next = [...done, id];
    setDone(next);
    save("lessons-done", next);
  };

  return (
    <div className="learn">
      <aside className="lesson-list">
        <div className="progress" aria-label={`${done.length} of ${LESSONS.length} lessons complete`}>
          <div style={{ width: `${(done.length / LESSONS.length) * 100}%` }} />
        </div>
        <p className="help">{done.length} / {LESSONS.length} lessons complete</p>
        {LESSONS.map((l, i) => (
          <button key={l.id} className={open === l.id ? "lesson-item on" : "lesson-item"} onClick={() => setOpen(l.id)}>
            <span>{done.includes(l.id) ? "✅" : l.icon}</span>
            <span><small>{i + 1}. {l.level}</small>{l.title}</span>
          </button>
        ))}
      </aside>
      <article className="lesson">
        <div className="lesson-head">
          <h3>{lesson.icon} {lesson.title}</h3>
          <label className="keypick">Sa =
            <select value={keyName} onChange={(e) => setKeyName(e.target.value)}>
              {KEYS.map((k) => <option key={k}>{k}</option>)}
            </select>
          </label>
        </div>
        {lesson.body.map((p) => <p key={p}>{p}</p>)}
        {lesson.tries.length > 0 && (
          <div className="tries">
            <strong>🎧 Try it</strong>
            <div className="row">
              {lesson.tries.map((t) => (
                <button key={t.label} className="chip" onClick={() => t.play(sa)}>▶ {t.label}</button>
              ))}
            </div>
          </div>
        )}
        {lesson.widget === "piano" && (
          <div className="widget">
            <p className="help">Play the keys yourself. Typing keys A W S E D F T G Y H U J K also play from Sa.</p>
            <Piano keyName={keyName} notes={["Sa", "Re", "Ga", "Ma", "Pa", "Dha", "Ni"]} typing />
          </div>
        )}
        {lesson.widget === "ragas" && <RagaExplorer opts={opts} keyName={keyName} />}
        {lesson.widget === "tala" && (
          <div className="widget">
            <div className="row">
              {Object.entries(opts.talas).map(([k, t]) => (
                <button key={k} className={tala === k ? "chip small on" : "chip small"} onClick={() => setTala(k)}>
                  {t.name} ({t.matras})
                </button>
              ))}
            </div>
            <p className="help">{opts.clap_help}</p>
            <TalaCircle key={tala} tala={opts.talas[tala]} bpm={100} keyName={keyName} />
          </div>
        )}
        <Quiz key={lesson.id} quiz={lesson.quiz} done={done.includes(lesson.id)} onPass={() => pass(lesson.id)} />
        <div className="row nav">
          {LESSONS.indexOf(lesson) > 0 && (
            <button className="chip" onClick={() => setOpen(LESSONS[LESSONS.indexOf(lesson) - 1].id)}>← Previous</button>
          )}
          {LESSONS.indexOf(lesson) < LESSONS.length - 1 && (
            <button className="chip on" onClick={() => setOpen(LESSONS[LESSONS.indexOf(lesson) + 1].id)}>Next lesson →</button>
          )}
        </div>
      </article>
    </div>
  );
}
