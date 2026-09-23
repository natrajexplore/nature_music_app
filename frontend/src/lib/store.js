// Per-browser conveniences (progress, history). Always safe if storage is unavailable.
const PREFIX = "nature-orchestra:";

export function load(key, fallback) {
  try {
    const v = localStorage.getItem(PREFIX + key);
    return v == null ? fallback : JSON.parse(v);
  } catch {
    return fallback;
  }
}

export function save(key, value) {
  try {
    localStorage.setItem(PREFIX + key, JSON.stringify(value));
  } catch {
    // Storage full or blocked: progress simply isn't remembered.
  }
}
