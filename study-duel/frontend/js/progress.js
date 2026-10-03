// Standings: today's result plus the season so far.
import { api, player } from "./api.js";
import { esc, langBadge, pct, renderNav, requireAuth } from "./ui.js";

const mount = () => document.getElementById("progress");
let me = "";

async function boot() {
  renderNav("progress");
  if (!requireAuth()) return;
  me = player();
  mount().innerHTML = `<p class="muted">Loading...</p>`;

  let today, prog;
  try {
    [today, prog] = await Promise.all([
      api.get("/api/session/result/today"),
      api.get("/api/progress"),
    ]);
  } catch (err) {
    mount().innerHTML = `<div class="panel"><p>${esc(err.message)}</p></div>`;
    return;
  }

  mount().innerHTML = `
    <div class="panel stack rise" style="margin-bottom:16px">
      <div class="spread">
        <h3 style="margin:0">Today &middot; ${esc(today.date_key)}</h3>
        <span class="badge${today.both_submitted ? " ok" : ""}">${
          today.both_submitted ? "both played" : "waiting on your partner"
        }</span>
      </div>
      <p class="small muted">One winner per language. Scores stay hidden until both of you have played, so nobody can calibrate off a visible target.</p>
      <div class="grid cols-3">${today.langs.map(todayCard).join("")}</div>
    </div>

    <div class="grid cols-2" style="margin-bottom:16px">
      <div class="panel stack rise">
        <h3 style="margin:0">Season</h3>
        <div class="row" style="gap:28px">
          <div class="stat"><span class="k">Streak</span><span class="v">${prog.streak}</span></div>
          <div class="stat"><span class="k">Days to exam</span><span class="v">${
            prog.days_to_exam === null || prog.days_to_exam === undefined ? "--" : prog.days_to_exam
          }</span></div>
        </div>
        <p class="small muted">Streak counts days on which at least one of you played. To light up the countdown, set <span class="code">exam_date</span> in the PAIR block of <span class="code">app/seed/data.py</span> and re-run the loader.</p>
      </div>
      <div class="panel stack rise">
        <h3 style="margin:0">The two of you</h3>
        <p class="muted">${esc(prog.name)} vs ${esc(prog.partner)}</p>
        <p class="small muted">A tier moves up only when BOTH of you clear 80% on the same day, so the daily sets stay comparable from then on.</p>
        <a class="btn small" href="chronicle.html">Read the chronicle</a>
      </div>
    </div>

    <h3>The three languages</h3>
    <div class="grid cols-3" style="margin-top:10px">${prog.langs.map(langCard).join("")}</div>`;

  document.querySelectorAll("[data-play]").forEach((btn) => {
    btn.onclick = () => (location.href = "play.html?lang=" + btn.dataset.play);
  });
}

function todayCard(l) {
  const verdict = !l.settled
    ? "Not settled"
    : l.tie
      ? "Level"
      : `Won by ${esc(l.winner)}`;

  const detail = l.settled
    ? Object.entries(l.scores)
        .map(([n, s]) => `${esc(n)} ${s}`)
        .join(" &middot; ")
    : Object.entries(l.submitted)
        .map(([n, s]) => `${esc(n)}: ${s ? "played" : "not yet"}`)
        .join(" &middot; ");

  return `
    <div class="panel tight accents" data-lang="${esc(l.lang)}">
      ${langBadge(l.lang)}
      <p style="margin:10px 0 0;font-family:var(--font-display);font-size:1.1rem">${verdict}</p>
      <p class="small muted" style="margin:6px 0 0">${detail}</p>
      ${
        l.your_score === null || l.your_score === undefined
          ? ""
          : `<p class="small" style="margin:6px 0 0">Your score: <b>${l.your_score}</b></p>`
      }
    </div>`;
}

function langCard(l) {
  const seenPct = l.total_cards ? (l.seen / l.total_cards) * 100 : 0;
  return `
    <div class="panel stack accents" data-lang="${esc(l.lang)}">
      <div class="spread">
        ${langBadge(l.lang)}
        <span class="small muted">tier ${l.tier}</span>
      </div>
      <div class="row" style="gap:22px">
        <div class="stat"><span class="k">Wins</span><span class="v">${l.wins}</span></div>
        <div class="stat"><span class="k">Accuracy</span><span class="v">${pct(l.accuracy)}</span></div>
        <div class="stat"><span class="k">Due</span><span class="v">${l.due}</span></div>
      </div>
      <div>
        <div class="spread small muted"><span>Seen</span><span>${l.seen} / ${l.total_cards}</span></div>
        <div class="meter" style="margin-top:6px"><i style="width:${seenPct}%"></i></div>
      </div>
      <button class="btn small" data-play="${esc(l.lang)}">Play ${esc(l.lang)}</button>
    </div>`;
}

boot();
