// Shared chrome + small helpers. Every page drops <div id="nav"></div> and
// calls renderNav(), so the header is defined exactly once.
import { clearSession, player, token } from "./api.js";
import { apiBase, setApiBase } from "./config.js";
import { toggleTheme } from "./theme.js";

export const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);

export const pct = (n) => `${Math.round((n || 0) * 100)}%`;

let toastTimer = null;
export function toast(message, kind = "") {
  let host = document.getElementById("toast");
  if (!host) {
    host = document.createElement("div");
    host.id = "toast";
    document.body.appendChild(host);
  }
  host.className = kind;
  host.textContent = message;
  host.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => host.classList.add("hidden"), 4200);
}

export function requireAuth() {
  if (token()) return true;
  location.href = "index.html?next=" + encodeURIComponent(location.pathname + location.search);
  return false;
}

const TABS = [
  ["play.html", "Today", "play"],
  ["storybook.html", "Storybook", "storybook"],
  ["progress.html", "Progress", "progress"],
  ["chronicle.html", "Chronicle", "chronicle"],
];

export function renderNav(active) {
  const host = document.getElementById("nav");
  if (!host) return;
  const signed = !!token();

  host.innerHTML = `
    <div class="topbar ground">
      <div class="wrap inner">
        <a class="brand" href="index.html">Study<b>Duel</b></a>
        <nav class="tabs">
          ${TABS.map(
            ([href, label, key]) =>
              `<a href="${href}"${key === active ? ' aria-current="page"' : ""}>${label}</a>`
          ).join("")}
        </nav>
        <div class="row" style="gap:8px">
          ${signed ? `<span class="small muted">${esc(player())}</span>` : ""}
          <button class="icon-btn" id="themeBtn" title="Switch between day and night">Theme</button>
          <button class="icon-btn" id="apiBtn" title="Where the API lives">API</button>
          ${signed ? `<button class="icon-btn" id="signOutBtn">Sign out</button>` : ""}
        </div>
      </div>
    </div>`;

  document.getElementById("themeBtn").onclick = () =>
    toast("Switched to " + toggleTheme() + " mode", "ok");

  document.getElementById("apiBtn").onclick = () => {
    const next = prompt("API base URL (your Render service):", apiBase());
    if (next === null) return;
    setApiBase(next);
    toast("API address saved. Reloading.", "ok");
    setTimeout(() => location.reload(), 700);
  };

  const out = document.getElementById("signOutBtn");
  if (out) {
    out.onclick = () => {
      clearSession();
      location.href = "index.html";
    };
  }
}

export function langBadge(lang) {
  return `<span class="badge" data-lang="${esc(lang)}">${esc(lang)}</span>`;
}

export function linkStory(storyId, beat) {
  const b = beat === null || beat === undefined ? 0 : beat;
  return `storybook.html?story=${encodeURIComponent(storyId)}&beat=${b}`;
}
