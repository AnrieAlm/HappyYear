// The season chronicle: the day-by-day record, written at settlement.
import { api } from "./api.js";
import { esc, langBadge, renderNav } from "./ui.js";

const mount = () => document.getElementById("chronicle");

async function boot() {
  renderNav("chronicle");
  mount().innerHTML = `<p class="muted">Loading...</p>`;

  let rows;
  try {
    rows = await api.get("/api/chronicle?limit=200");
  } catch (err) {
    mount().innerHTML = `<div class="panel"><p>${esc(err.message)}</p></div>`;
    return;
  }

  if (!rows.length) {
    mount().innerHTML = `<div class="panel stack">
      <h3 style="margin:0">Nothing written yet</h3>
      <p class="muted">Once you and your partner have both played a day, an entry lands here for each language. This is the record of the whole run -- the reason to keep it after the exam.</p>
      <a class="btn primary" href="play.html">Play today</a>
    </div>`;
    return;
  }

  const byDay = new Map();
  for (const r of rows) {
    if (!byDay.has(r.date_key)) byDay.set(r.date_key, []);
    byDay.get(r.date_key).push(r);
  }

  mount().innerHTML = `
    <div class="panel stack" style="margin-bottom:16px">
      <h3 style="margin:0">The chronicle</h3>
      <p class="muted small">Every settled day, in the order it happened. Winners are named, misses are not punished, ties are called ties.</p>
    </div>
    ${[...byDay.entries()]
      .map(
        ([day, entries]) => `
        <div class="panel" style="margin-bottom:12px">
          <div class="spread"><span style="font-family:var(--font-display)">${esc(day)}</span>
            <span class="row" style="gap:6px">${entries.map((e) => langBadge(e.lang)).join("")}</span>
          </div>
          <div class="stack" style="margin-top:10px">
            ${entries.map((e) => `<p class="beat accents" data-lang="${esc(e.lang)}" style="margin:0">${esc(e.text)}</p>`).join("")}
          </div>
        </div>`
      )
      .join("")}`;
}

boot();
