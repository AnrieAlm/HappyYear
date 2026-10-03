// The scored Daily Challenge: one language, today's card set, immediate
// feedback per card. Scoring and the attempt counter are both server-side.
import { api } from "./api.js";
import { esc, langBadge, linkStory, renderNav, requireAuth, toast } from "./ui.js";

const LANGS = ["HTML", "CSS", "JS"];
let S = null; // { lang, ch, idx, results, cardStart, hintUsed, revealed }

const drill = () => document.getElementById("drill");

function langTabs(active) {
  return `<div class="row" style="gap:8px">${LANGS.map(
    (l) =>
      `<a class="btn small${l === active ? " primary" : ""}" href="play.html?lang=${l}">${l}</a>`
  ).join("")}</div>`;
}

async function boot() {
  renderNav("play");
  if (!requireAuth()) return;

  const wanted = (new URLSearchParams(location.search).get("lang") || "HTML").toUpperCase();
  const lang = LANGS.includes(wanted) ? wanted : "HTML";
  document.getElementById("langTabs").innerHTML = langTabs(lang);
  await start(lang);
}

async function start(lang) {
  drill().innerHTML = `<div class="panel"><p class="muted">Loading today's ${esc(lang)} set...</p></div>`;

  let ch;
  try {
    ch = await api.get("/api/challenge/today?lang=" + encodeURIComponent(lang));
  } catch (err) {
    drill().innerHTML = `<div class="panel"><p>${esc(err.message)}</p>
      <p class="small muted">If the database was just created, give the service a moment and reload.</p></div>`;
    return;
  }

  if (!ch.cards.length) {
    drill().innerHTML = `<div class="panel"><p>No cards for ${esc(lang)} yet. Seed the database, then reload.</p></div>`;
    return;
  }

  if (ch.submitted) return showAlready(ch);

  S = { lang, ch, idx: 0, results: [], cardStart: Date.now(), hintUsed: false, revealed: null };
  renderCard();
}

function progressBar() {
  const done = S.results.length;
  const total = S.ch.cards.length;
  return `<div class="spread small muted">
      <span>${done} of ${total} done &middot; tier ${S.ch.tier}</span>
      <span>${esc(S.ch.date_key)}</span>
    </div>
    <div class="meter"><i style="width:${(done / total) * 100}%"></i></div>`;
}

function renderCard() {
  const card = S.ch.cards[S.idx];
  S.cardStart = Date.now();
  S.hintUsed = false;
  S.revealed = null;

  drill().innerHTML = `
    <div class="panel stack rise">
      <div class="spread">
        ${langBadge(S.lang)}
        <span class="small muted">Card ${S.idx + 1} of ${S.ch.cards.length}</span>
      </div>
      <div class="prompt">${esc(card.prompt)}</div>
      <div id="hintBox" class="hidden"><p class="small muted">Hint: ${esc(card.hint || "no hint for this one")}</p></div>
      <div>
        <input id="answer" class="answer" type="text" autocomplete="off" autocapitalize="off"
               spellcheck="false" placeholder="Type your answer, then press Enter" />
      </div>
      <div id="feedback"></div>
      <div class="row">
        <button class="btn primary" id="submitBtn">Submit</button>
        <button class="btn ghost small" id="hintBtn">Show hint</button>
      </div>
      ${progressBar()}
      <p class="small muted">100 first try, 60 after a retry, 30 with the hint, 0 for a miss.</p>
    </div>`;

  const input = document.getElementById("answer");
  input.focus();
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendAnswer();
  });
  document.getElementById("submitBtn").onclick = sendAnswer;
  document.getElementById("hintBtn").onclick = showHint;
}

async function showHint() {
  const card = S.ch.cards[S.idx];
  document.getElementById("hintBox").classList.remove("hidden");
  S.hintUsed = true;
  try {
    await api.post("/api/session/hint", { lang: S.lang, card_id: card.id });
  } catch {
    /* the cap is enforced server-side at submit anyway */
  }
}

async function sendAnswer() {
  const card = S.ch.cards[S.idx];
  const input = document.getElementById("answer");
  const given = input.value.trim();
  if (!given) {
    toast("Type an answer first.", "lapse");
    input.focus();
    return;
  }

  const btn = document.getElementById("submitBtn");
  btn.disabled = true;

  let res;
  try {
    res = await api.post("/api/session/check", {
      lang: S.lang,
      card_id: card.id,
      answer: given,
      ms: Date.now() - S.cardStart,
      hint_used: S.hintUsed,
    });
  } catch (err) {
    btn.disabled = false;
    toast(err.message, "lapse");
    return;
  }

  if (res.correct) {
    S.results.push(res);
    showReveal(true, res.canonical, "Correct.");
    return;
  }

  if (res.attempts === 1) {
    document.getElementById("feedback").innerHTML =
      `<div class="reveal wrong rise"><p><b>Not quite.</b> One more try.</p></div>`;
    input.value = "";
    input.focus();
    btn.disabled = false;
    return;
  }

  S.results.push(res);
  showReveal(false, res.canonical, "Missed. Read the story when you finish.");
}

function showReveal(correct, canonical, note) {
  const isLast = S.idx >= S.ch.cards.length - 1;
  document.getElementById("feedback").innerHTML = `
    <div class="reveal ${correct ? "correct" : "wrong"} rise">
      <p class="small muted">${esc(note)}</p>
      <p class="canonical">${esc(canonical)}</p>
    </div>`;
  document.getElementById("hintBox").classList.add("hidden");
  document.getElementById("answer").disabled = true;

  const row = document.querySelector("#drill .row");
  row.innerHTML = `<button class="btn primary" id="nextBtn">${
    isLast ? "Finish and submit" : "Next card"
  }</button>`;
  document.getElementById("nextBtn").focus();
  document.getElementById("nextBtn").onclick = isLast ? finish : next;
}

function next() {
  S.idx += 1;
  renderCard();
}

async function finish() {
  drill().innerHTML = `<div class="panel"><p class="muted">Submitting...</p></div>`;
  let out;
  try {
    out = await api.post("/api/session/submit", { lang: S.lang });
  } catch (err) {
    drill().innerHTML = `<div class="panel"><p>${esc(err.message)}</p>
      <button class="btn" onclick="location.reload()">Back to the cards</button></div>`;
    return;
  }
  renderScore(out);
}

function renderScore(out) {
  const missed = out.results.filter((r) => !r.correct);
  const withStory = missed.filter((r) => r.story_id);
  const cardById = Object.fromEntries(S.ch.cards.map((c) => [c.id, c]));

  drill().innerHTML = `
    <div class="panel stack rise">
      <div class="spread">
        ${langBadge(out.lang)}
        <span class="small muted">${esc(out.date_key)}</span>
      </div>
      <h2>${out.score} points</h2>
      <p class="muted">${out.correct} of ${out.total} correct, in ${Math.round(out.time_ms / 1000)}s.</p>
      <p class="small muted">Both scores stay hidden until your partner has also played. Then the day's winner is declared for each language.</p>
      <div class="row">
        <a class="btn primary" href="play.html?lang=${LANGS[(LANGS.indexOf(out.lang) + 1) % 3]}">Next language</a>
        <a class="btn" href="progress.html">See the standings</a>
      </div>
    </div>
    ${
      withStory.length
        ? `<div class="panel stack rise">
             <h3>The ones that slipped</h3>
             <p class="muted small">You miss a card, you re-read the scene that explains it. That is the whole method.</p>
             ${withStory
               .map((r) => {
                 const c = cardById[r.card_id] || {};
                 return `<div class="row spread" style="border-top:1px solid var(--line);padding-top:12px">
                     <div><div>${esc(c.prompt || r.card_id)}</div>
                     <div class="small muted">Answer: <span class="code">${esc(r.canonical)}</span></div></div>
                     <a class="btn small" href="${linkStory(r.story_id, r.beat)}">Read the story</a>
                   </div>`;
               })
               .join("")}
           </div>`
        : ""
    }`;

  // Personal review segment: unscored, purely for retention.
  document.getElementById("reviewSlot").innerHTML =
    `<div class="panel stack rise">
       <h3>Personal review</h3>
       <p class="muted small">Unscored on purpose. This is your own spaced-repetition queue, so it never affects the day's standings.</p>
       <div id="reviewBody"><button class="btn" id="reviewBtn" data-lang="${esc(out.lang)}">Start the review run</button></div>
     </div>`;
  document.getElementById("reviewBtn").onclick = startReview;
}

async function startReview() {
  const lang = document.getElementById("reviewBtn").dataset.lang;
  const box = document.getElementById("reviewBody");
  box.innerHTML = `<p class="muted small">Loading your due cards...</p>`;

  let data;
  try {
    data = await api.get("/api/review/due?lang=" + encodeURIComponent(lang));
  } catch (err) {
    box.innerHTML = `<p>${esc(err.message)}</p>`;
    return;
  }
  if (!data.cards.length) {
    box.innerHTML = `<p class="muted small">Nothing due. Come back tomorrow.</p>`;
    return;
  }

  let i = 0;
  let attempts = 0;
  let hinted = false;
  const queue = data.cards;

  const paint = () => {
    const c = queue[i];
    attempts = 0;
    hinted = false;
    box.innerHTML = `
      <div class="spread small muted"><span>Review ${i + 1} of ${queue.length}</span><span>${data.due_total} due in total</span></div>
      <div class="prompt">${esc(c.prompt)}</div>
      <div id="rFeedback"></div>
      <input id="rAnswer" class="answer" type="text" autocomplete="off" spellcheck="false" placeholder="Answer, then Enter" />
      <div class="row">
        <button class="btn primary" id="rSubmit">Submit</button>
        <button class="btn ghost small" id="rHint">Show hint</button>
      </div>`;
    const input = document.getElementById("rAnswer");
    input.focus();
    input.addEventListener("keydown", (e) => e.key === "Enter" && answer());
    document.getElementById("rSubmit").onclick = answer;
    document.getElementById("rHint").onclick = () => {
      hinted = true;
      document.getElementById("rFeedback").innerHTML =
        `<p class="small muted">Hint: ${esc(c.hint || "none")}</p>`;
    };
  };

  const answer = async () => {
    const c = queue[i];
    const given = document.getElementById("rAnswer").value.trim();
    if (!given) return;
    attempts += 1;
    // The review run is unscored, so it grades through its own endpoint and
    // never touches the scored run document.
    let res;
    try {
      res = await api.post("/api/review/submit", {
        lang,
        answers: [{ card_id: c.id, answer: given, attempts, hint_used: hinted, ms: 0 }],
      });
    } catch (err) {
      document.getElementById("rFeedback").innerHTML = `<p>${esc(err.message)}</p>`;
      return;
    }
    const graded = (res.graded || [])[0] || { correct: false, canonical: "" };

    if (!graded.correct && attempts === 1) {
      document.getElementById("rFeedback").innerHTML =
        `<div class="reveal wrong"><p><b>Not quite.</b> One more try.</p></div>`;
      document.getElementById("rAnswer").value = "";
      document.getElementById("rAnswer").focus();
      return;
    }
    document.getElementById("rFeedback").innerHTML = `
      <div class="reveal ${graded.correct ? "correct" : "wrong"}">
        <p class="canonical">${esc(graded.canonical)}</p>
      </div>`;
    advance();
  };

  const advance = () => {
    i += 1;
    if (i >= queue.length) {
      box.innerHTML = `<p class="muted small">Review done. This is what keeps it from slipping.</p>`;
      return;
    }
    setTimeout(paint, 700);
  };

  paint();
}

function showAlready(ch) {
  drill().innerHTML = `
    <div class="panel stack rise">
      <div class="spread">${langBadge(ch.lang)}<span class="small muted">${esc(ch.date_key)}</span></div>
      <h3>You have played ${esc(ch.lang)} today</h3>
      <p class="muted">Your score: <b>${ch.score ?? 0}</b></p>
      <p class="small muted">Scores unlock for both of you once your partner has played. The day's winners are declared per language.</p>
      <div class="row">
        <a class="btn primary" href="progress.html">Today's result</a>
        <a class="btn" href="storybook.html">Read the stories</a>
      </div>
    </div>`;
}

boot();
