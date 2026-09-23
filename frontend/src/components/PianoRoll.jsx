import { useEffect, useRef } from "react";
import { noteName } from "../lib/theory";

const COLORS = { bird: "#2e7d4f", droplet: "#3d7fc4" };

/** Piano-roll view of the composed melody and chords, with a live playhead. Click to seek. */
export default function PianoRoll({ track, audioRef }) {
  const canvas = useRef(null);

  useEffect(() => {
    const cv = canvas.current;
    if (!cv) return undefined;
    const notes = track.notes;
    const lo = Math.min(...notes.map((n) => n.m)) - 2;
    const hi = Math.max(...notes.map((n) => n.m)) + 2;
    const total = track.duration;
    let raf;

    const draw = () => {
      const dpr = window.devicePixelRatio || 1;
      const W = cv.clientWidth;
      const H = cv.clientHeight;
      if (cv.width !== W * dpr) { cv.width = W * dpr; cv.height = H * dpr; }
      const g = cv.getContext("2d");
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      g.clearRect(0, 0, W, H);
      const x = (t) => (t / total) * W;
      const rowH = H / (hi - lo + 1);
      const y = (m) => (hi - m) * rowH;

      // Rows: shade Sa rows so the home note is easy to find.
      for (let m = lo; m <= hi; m++) {
        if ((m - track.sa_midi) % 12 === 0) {
          g.fillStyle = "rgba(46,125,79,0.09)";
          g.fillRect(0, y(m), W, rowH);
          g.fillStyle = "#46695a";
          g.font = "10px system-ui";
          g.fillText(`Sa ${noteName(m)}`, 4, y(m) + rowH - 2);
        }
      }
      // Section markers.
      g.font = "11px system-ui";
      track.sections.forEach((s) => {
        g.strokeStyle = "rgba(29,58,42,0.25)";
        g.beginPath(); g.moveTo(x(s.t), 0); g.lineTo(x(s.t), H); g.stroke();
        g.fillStyle = "#1d3a2a";
        g.fillText(s.name, x(s.t) + 4, 12);
      });
      // Notes.
      const now = audioRef.current?.currentTime ?? 0;
      notes.forEach((n) => {
        const active = now >= n.t && now <= n.t + n.d;
        g.fillStyle = COLORS[n.i];
        g.globalAlpha = active ? 1 : n.i === "droplet" ? 0.35 : 0.8;
        g.fillRect(x(n.t), y(n.m) + 1, Math.max(2, x(n.d) - 1), Math.max(2, rowH - 2));
      });
      g.globalAlpha = 1;
      // Playhead.
      g.strokeStyle = "#c0392b";
      g.lineWidth = 2;
      g.beginPath(); g.moveTo(x(now), 0); g.lineTo(x(now), H); g.stroke();
      g.lineWidth = 1;
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, [track, audioRef]);

  const seek = (e) => {
    const a = audioRef.current;
    if (!a) return;
    const r = e.currentTarget.getBoundingClientRect();
    a.currentTime = ((e.clientX - r.left) / r.width) * track.duration;
  };

  return (
    <div className="roll-wrap">
      <canvas ref={canvas} className="roll" onClick={seek}
              aria-label="Piano roll of the melody and chords. Click to jump to a moment." />
      <div className="legend">
        <span><i style={{ background: COLORS.bird }} /> Bird melody</span>
        <span><i style={{ background: COLORS.droplet }} /> Water-drop chords</span>
        <span><i style={{ background: "#c0392b" }} /> Playhead (click to seek)</span>
      </div>
    </div>
  );
}
