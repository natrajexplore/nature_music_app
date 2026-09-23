import { useState } from "react";
import { GLOSSARY } from "../data/glossary";

export default function Glossary() {
  const [q, setQ] = useState("");
  const [kind, setKind] = useState("All");
  const kinds = ["All", ...new Set(GLOSSARY.map((g) => g[1]))];
  const s = q.trim().toLowerCase();
  const rows = GLOSSARY.filter(([term, k, text]) =>
    (kind === "All" || k === kind) && (!s || term.toLowerCase().includes(s) || text.toLowerCase().includes(s)));
  return (
    <div>
      <input className="search" type="search" placeholder="Search terms, e.g. tala, cadence, pan…"
             value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search the glossary" />
      <div className="row">
        {kinds.map((k) => (
          <button key={k} className={kind === k ? "chip small on" : "chip small"} onClick={() => setKind(k)}>{k}</button>
        ))}
      </div>
      <dl className="glossary">
        {rows.map(([term, k, text]) => (
          <div key={term}>
            <dt>{term} <span className="tag">{k}</span></dt>
            <dd>{text}</dd>
          </div>
        ))}
        {rows.length === 0 && <p className="help">No matches.</p>}
      </dl>
    </div>
  );
}
