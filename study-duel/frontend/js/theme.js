// Theme follows the clock: warm paper for daytime drilling, the night theme
// for evening. A manual choice sticks. Calm is partly just sameness, so this
// never changes mid-session on its own beyond the 07:00 / 19:00 boundary.
const KEY = "sd_theme";

function autoTheme() {
  const h = new Date().getHours();
  return h >= 7 && h < 19 ? "day" : "night";
}

export function applyTheme() {
  document.documentElement.dataset.theme = localStorage.getItem(KEY) || autoTheme();
}

export function toggleTheme() {
  const next = document.documentElement.dataset.theme === "day" ? "night" : "day";
  localStorage.setItem(KEY, next);
  document.documentElement.dataset.theme = next;
  return next;
}

applyTheme();
