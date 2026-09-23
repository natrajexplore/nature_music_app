// Shared music-theory helpers for the browser (mirrors theory.py on the backend).

export const KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
export const SARGAM = ["Sa", "re", "Re", "ga", "Ga", "Ma", "Ma#", "Pa", "dha", "Dha", "ni", "Ni"];
export const SOLFEGE = ["Do", "Ra", "Re", "Me", "Mi", "Fa", "Fi", "Sol", "Le", "La", "Te", "Ti"];
export const SEMI = Object.fromEntries(SARGAM.map((n, i) => [n, i]));
export const INTERVALS = [
  "unison", "minor 2nd", "major 2nd", "minor 3rd", "major 3rd", "perfect 4th",
  "tritone", "perfect 5th", "minor 6th", "major 6th", "minor 7th", "major 7th", "octave",
];

/** MIDI note of Sa for a key, in the same F3..E4 range the backend uses. */
export function saMidi(key) {
  const pc = KEYS.indexOf(key);
  return pc <= 4 ? 60 + pc : 48 + pc;
}

/** ".Dha" -> -3, "Sa" -> 0, "Re'" -> 14 (semitones above middle Sa). */
export function tokenSemi(tok) {
  const oct = tok.startsWith(".") ? -12 : tok.endsWith("'") ? 12 : 0;
  return SEMI[tok.replace(/[.']/g, "")] + oct;
}

export function western(key, semi) {
  return KEYS[(((KEYS.indexOf(key) + semi) % 12) + 12) % 12];
}

export function noteName(midi) {
  return KEYS[((midi % 12) + 12) % 12] + (Math.floor(midi / 12) - 1);
}

/** Show a sargam note with its octave: .Dha (low), Sa, Re' (high). */
export function sargamLabel(name, octave) {
  if (octave < 0) return "." + name;
  if (octave > 0) return name + "'";
  return name;
}

export const isBlack = (midi) => [1, 3, 6, 8, 10].includes(((midi % 12) + 12) % 12);

export function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
