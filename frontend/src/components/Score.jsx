import { useState } from "react";
import { sargamLabel } from "../lib/theory";

/** The composition written out bar by bar: chords, Roman numerals and melody notes. */
export default function Score({ track, currentBar }) {
  const [mode, setMode] = useState("both");
  return (
    <div>
      <div className="row">
        {[["both", "Sargam + Western"], ["sargam", "Sargam only"], ["western", "Western only"]].map(([k, l]) => (
          <button key={k} className={mode === k ? "chip small on" : "chip small"} onClick={() => setMode(k)}>{l}</button>
        ))}
      </div>
      <div className="score">
        {track.score.map((b) => (
          <div key={b.bar} className={b.bar - 1 === currentBar ? "bar cur" : "bar"}>
            <div className="bar-head">
              <span>Bar {b.bar}</span>
              <span className="sect">{b.section}</span>
            </div>
            <div className="chord-sym" title={`${b.chord.quality} chord`}>
              {b.chord.symbol} <span className="roman">{b.chord.roman}</span>
            </div>
            <div className="chord-notes">{b.chord.sargam.join(" ")}</div>
            <div className="mel">
              {b.melody.length === 0 && <span className="rest">rest</span>}
              {b.melody.map((n, i) => (
                <span key={i} className="mnote" title={`matra ${Math.floor(n.step) + 1}`}>
                  {mode !== "western" && <b>{sargamLabel(n.sargam, n.octave)}</b>}
                  {mode !== "sargam" && <small>{n.western}</small>}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
      <p className="help">
        A dot before a note (.Dha) means the lower octave, an apostrophe after it (Re') means the higher octave.
        Roman numerals: capital = major chord, small = minor, ° = diminished.
      </p>
    </div>
  );
}
