// The storybook tab. Public -- readable without signing in, because it is a
// study aid first. Supports storybook.html?story=<id>&beat=<n>, which is how
// the drill deep-links you to the exact paragraph you just missed.
import { api } from "./api.js";
import { esc, renderNav } from "./ui.js";

const mount = () => document.getElementById("book");

let stories = [];
let cast = [];
let index = 0;
let track = null;

function slide(s, markBeat) {
  return `
    <article class="slide" aria-label="Story ${s.n}: ${esc(s.title)}">
      <div class="story-hero">
        <img src="${esc(s.image_url)}" alt="${esc(s.image_alt)}" loading="${s.n === 1 ? "eager" : "lazy"}" />
        <div class="fade"></div>
        <div class="spread" style="position:absolute;left:18px;right:18px;top:16px">
          <span class="badge" data-lang="${esc(s.language)}">${esc(s.language)}</span>
          <span class="small muted">${String(s.n).padStart(2, "0")} / ${String(stories.length).padStart(2, "0")}</span>
        </div>
      </div>
      <div class="wrap narrow" style="padding:22px 20px 28px">
        <p class="small" style="margin:0;color:var(--accent);letter-spacing:.14em;text-transform:uppercase;font-family:var(--font-display)">${esc(s.concept)}</p>
        <h2 style="margin-top:6px">${esc(s.title)}</h2>
        <p class="muted" style="margin-top:4px">${esc(s.scene)}</p>
        <div class="stack" style="margin-top:18px;font-size:1.06rem">
          ${s.body
            .map(
              (p, b) => `<p class="beat${b === markBeat ? " marked" : ""}">${esc(p)}</p>`
            )
            .join("")}
        </div>
        <div class="panel tight" style="margin-top:20px;background:var(--surface-2)">
          <p class="small" style="margin:0;color:var(--accent);letter-spacing:.16em;text-transform:uppercase;font-family:var(--font-display)">Unpacking</p>
          <p style="margin:6px 0 0">${esc(s.unpacking)}</p>
        </div>
        <p class="small muted" style="margin-top:14px">Placeholder art. Swap the image for your pixel-art set when it is ready.</p>
      </div>
    </article>`;
}

function render(markBeat) {
  mount().innerHTML = `
    <div class="spread" style="margin-bottom:14px">
      <div class="row" style="gap:6px" id="jump"></div>
      <div class="row" style="gap:8px">
        <button class="btn small" id="prevBtn">Previous</button>
        <button class="btn small" id="nextBtn">Next</button>
      </div>
    </div>
    <div class="swiper panel" id="track" style="padding:0">
      ${stories.map((s, i) => slide(s, i === index ? markBeat : null)).join("")}
    </div>
    <div class="panel" style="margin-top:16px">
      <h3>The cast</h3>
      <p class="small muted">Every rule in the deck belongs to someone in the valley. That is what makes it stick.</p>
      <div class="grid cols-3" style="margin-top:12px">
        ${cast
          .map(
            (m) =>
              `<div class="cast-item"><div class="name">${esc(m.name)}</div><p class="small muted" style="margin:6px 0 0">${esc(m.role)}</p></div>`
          )
          .join("")}
      </div>
    </div>`;

  const jump = document.getElementById("jump");
  jump.innerHTML = stories
    .map(
      (s, i) =>
        `<a class="btn small${i === index ? " primary" : ""}" href="storybook.html?story=${encodeURIComponent(s.story_id)}">${String(s.n).padStart(2, "0")}</a>`
    )
    .join("");

  track = document.getElementById("track");

  const go = (i) => {
    index = Math.max(0, Math.min(stories.length - 1, i));
    track.scrollTo({ left: index * track.clientWidth, behavior: "smooth" });
    jump.querySelectorAll("a").forEach((a, k) => {
      a.className = "btn small" + (k === index ? " primary" : "");
    });
  };

  document.getElementById("prevBtn").onclick = () => go(index - 1);
  document.getElementById("nextBtn").onclick = () => go(index + 1);
  window.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") go(index + 1);
    if (e.key === "ArrowLeft") go(index - 1);
  });

  requestAnimationFrame(() => {
    track.scrollLeft = index * track.clientWidth;
    if (markBeat !== null && markBeat >= 0) {
      document
        .querySelector(".beat.marked")
        ?.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  });
}

async function boot() {
  renderNav("storybook");
  mount().innerHTML = `<p class="muted">Loading the stories...</p>`;

  let data;
  try {
    data = await api.get("/api/storybook");
  } catch (err) {
    mount().innerHTML = `<div class="panel"><p>${esc(err.message)}</p>
      <p class="small muted">The storybook needs the API reachable. Check the API button in the top right.</p></div>`;
    return;
  }

  stories = data.stories || [];
  cast = data.cast || [];

  const params = new URLSearchParams(location.search);
  const found = stories.findIndex((s) => s.story_id === params.get("story"));
  index = found >= 0 ? found : 0;
  const beat = params.get("beat");
  render(beat === null ? null : Number(beat));
}

boot();
