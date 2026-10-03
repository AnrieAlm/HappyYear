# Study Duel

A two-player study game for HTML, CSS and JavaScript, built for exam prep.

Two people, three languages, one **identical** card set each per day. You play separately,
at whatever time suits you. When the day closes, a winner is declared **per language** — so
there are three results every day. Underneath sits real spaced repetition (SM-2) and a
mnemonic story for every rule that keeps slipping.

- **Frontend:** plain HTML / CSS / JavaScript — no build step, deployed to **GitHub Pages**
- **Backend:** **FastAPI** (Python) — deployed to **Render**
- **Database:** **MongoDB** (Atlas free tier, or self-hosted on Render)

---

## 1. How a day works

Each day is split into **two segments**, and the split is the whole design:

| Segment | Scored? | Cards | Purpose |
|---|---|---|---|
| **Daily Challenge** | Yes | 20 per language | The competition. Identical for both players. |
| **Personal Review** | No | your due queue | Retention. Your own SM-2 schedule. |

**Why identical cards?** If each player faced their own spaced-repetition queue, the two
scores would not be comparable. So the scored set is derived deterministically from
`sha256(date_key + language)` over a sorted pool — same cards, same order, no coordination
and no race at midnight. Your personal SM-2 queue still runs, but unscored, so a heavy
backlog can never cost you the day.

**Scoring** (identical rules for both, always computed server-side):

| How the answer went | Points |
|---|---|
| Correct, first try | 100 |
| Correct after one retry | 60 |
| Hint opened | 30 (caps the card) |
| Missed | 0 |

**Tiers.** Each language has three tiers. A tier moves up only when **both** players clear
80% on the same day — that is what keeps the daily sets comparable over weeks, rather than
one player racing ahead into material the other has never seen.

**The story reteach.** Every hard rule has a mnemonic story with a paragraph that explains
it. Miss a card and the drill offers a link straight to *that paragraph*, highlighted. The
story is shown **after** a missed recall, never before — otherwise it becomes a crutch and
the recall stops happening.

---

## 2. Repo layout

```
backend/                       FastAPI + MongoDB
  app/
    main.py                    app, CORS, startup (indexes + auto-seed)
    config.py                  settings from env
    db.py                      Mongo client, collections, indexes
    security.py                two-person allowlist, JWT
    models.py                  request/response schemas
    srs.py                     SM-2 spaced repetition
    scoring.py                 normalisation, grading, points
    daily.py                   day boundary + deterministic daily set
    state.py                   the pair document, tiers, tallies
    routers/                   auth, challenge, session, review, progress, content
    services/
      reviews.py               record reviews, find what is due
      settle.py                winners per language, chronicle, tier advance
    seed/
      data.py                  <- the 9 stories, the cast, and ~97 cards
      load.py                  idempotent loader
  smoke_test.py                logic + seed integrity (no database needed)
  e2e_test.py                  full game loop against an in-memory Mongo
  requirements.txt

frontend/                      static site -> GitHub Pages
  index.html                   landing + sign-in + API address
  play.html                    today's duel
  storybook.html               the 9 stories, deep-linkable
  progress.html                today's result + the season
  chronicle.html               the day-by-day record
  css/tokens.css               palette + type
  css/app.css                  components
  js/                          config, api, ui, theme, drill, storybook, progress, chronicle
  .nojekyll

render.yaml                    Render Blueprint
.github/workflows/pages.yml    deploys frontend/ to Pages
```

---

## 3. Local development

Requires Python 3.11+ and a MongoDB (local or Atlas).

**1. Database.** Either run one locally:

```bash
docker run -d -p 27017:27017 --name study-duel-db mongo:7
```

or make a free **MongoDB Atlas** cluster and use its connection string.

**2. Backend**

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` — at minimum set `USERS` with your two long passcodes. Then:

```bash
.venv/bin/python -m app.seed.load     # idempotent
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Check <http://127.0.0.1:8000/api/health> and the interactive docs at `/docs`.
The app also auto-seeds on a first boot against an empty database.

**3. Frontend**

```bash
cd frontend
python3 -m http.server 5500
```

Open <http://localhost:5500>. On localhost the frontend defaults to
`http://127.0.0.1:8000`, so it just works. Any static server will do.

---

## 4. Deploying

### Step 1 — push to GitHub

```bash
git init
git add .
git commit -m "Study Duel"
git branch -M main
git remote add origin git@github.com:<you>/study-duel.git
git push -u origin main
```

`.env` is gitignored. Never commit real passcodes or a connection string.

### Step 2 — MongoDB

Create a free **Atlas M0** cluster, then:

1. **Database Access** — add a user with a strong password.
2. **Network Access** — allow `0.0.0.0/0`. Render's free tier has no fixed outbound IP,
   so an IP allowlist will not work with it.
3. Copy the connection string:

```
mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

> **On "MongoDB on Render":** Render does **not** offer managed MongoDB. The two real
> options are Atlas (above) or self-hosting the `mongo` image as a private Render service —
> `backend/mongo/Dockerfile` and a commented-out service block in `render.yaml` are there
> for that. Self-hosting needs a paid instance because of the persistent disk, and you own
> backups. Atlas is less work and comes with them.

### Step 3 — Render

1. Render dashboard → **New +** → **Blueprint** → pick your repo.
2. Render reads `render.yaml` and creates `study-duel-api`.
3. Set the env vars marked `sync: false`:

| Key | Value |
|---|---|
| `MONGO_URI` | your Atlas connection string |
| `USERS` | `{"farmerB":"a-long-passcode","maya":"another-long-passcode"}` |
| `ALLOWED_ORIGINS` | `https://<your-github-username>.github.io` |

`JWT_SECRET` is generated for you. `DAY_TZ` decides the shared day boundary — both players
must be measured against the same clock, so pick your real timezone.

4. Deploy, then check `https://<your-service>.onrender.com/api/health`.

The free tier sleeps after ~15 minutes idle; the first request of the day takes a few
seconds to wake. Fine for this.

### Step 4 — GitHub Pages

1. Repo → **Settings** → **Pages** → Source: **GitHub Actions**.
2. Push to `main` (or run the workflow manually). `pages.yml` publishes `frontend/`.
3. Your site: `https://<you>.github.io/<repo>/`.

### Step 5 — point the site at the API

Open the deployed site and click **API** in the top right. Paste your Render URL and save.
That is stored in the browser (`localStorage`), so you can move the API without editing
code or redeploying.

To set it permanently for everyone, edit `PROD_BASE` in `frontend/js/config.js` and push.

---

## 5. The two accounts

There is no public signup. `USERS` is a JSON object of `name → passcode` in the API's env:

```json
{"farmerB":"a-long-passcode","maya":"another-passcode"}
```

Change the names to whatever you like — they are just labels, and they appear in the
chronicle. Removing someone from `USERS` revokes their access on their next request.
Sign-in returns a JWT that the frontend keeps in `localStorage`; it lasts `JWT_TTL_DAYS`.

---

## 6. Running it

- **Sign in**, then **Today** → pick HTML, CSS or JS. Answer every card, then submit.
- Scores stay hidden until **both** of you have played, so nobody can calibrate off a
  visible target.
- **Progress** shows today's three results and the season standings.
- **Chronicle** is the written record: one entry per language per settled day.
- **Storybook** is public — anyone can read the mnemonics without signing in.

---

## 7. Editing the content

Everything lives in **`backend/app/seed/data.py`**:

- **`STORIES`** — the nine mnemonics. `body` is a list of paragraphs; the index of a
  paragraph is its **beat**.
- **`STORY_CARDS`** — cards that point back at a story via `story_id` + `beat`. This is
  what powers the reteach deep-link. Do not copy the prose in; just reference it.
- **`BASIC_CARDS`** — plain tier-1 cards with no story.
- **`PAIR`** — the two members, the timezone, the starting tiers, and **`exam_date`**.

After editing, re-run the loader. Cards and stories are upserted by id, so your progress
and history are untouched:

```bash
cd backend && .venv/bin/python -m app.seed.load
```

Set the exam date by editing `PAIR["exam_date"]` to `"2026-12-15"` and re-running. The
countdown appears on Progress.

---

## 8. API reference

| Method | Path | Notes |
|---|---|---|
| `POST` | `/api/auth/login` | name + passcode → token |
| `GET` | `/api/me` | who you are, who your partner is |
| `GET` | `/api/challenge/today?lang=HTML` | today's set. **Never includes answers.** |
| `POST` | `/api/session/check` | grade one card live; server owns the attempt counter |
| `POST` | `/api/session/hint` | record that the hint was opened |
| `POST` | `/api/session/submit` | finalise and score. Every card must be answered. |
| `GET` | `/api/session/result/today` | settle and return the day's winners |
| `GET` | `/api/review/due?lang=HTML` | your spaced-repetition queue |
| `POST` | `/api/review/submit` | record a review (unscored) |
| `GET` | `/api/progress` | per-language tier, wins, accuracy, due, streak |
| `GET` | `/api/chronicle` | the season record |
| `GET` | `/api/storybook` | the stories and the cast (public) |
| `GET` | `/api/health` | service + database health |

Two integrity details worth knowing:

- **The answer key never ships.** The challenge payload has no `answer` field; grading is
  server-side only.
- **The attempt counter is server-side.** Grading one card at a time is what gives you
  immediate feedback, but if the client reported its own `attempts`, you could call
  `/check` to harvest an answer and then submit it claiming a first try. Every `/check`
  increments the stored counter, so harvesting a reveal is self-defeating — the card can
  only ever score as a retry.

---

## 9. Tests

```bash
cd backend
../.venv/bin/pip install mongomock-motor httpx   # dev-only, not in requirements.txt

.venv/bin/python smoke_test.py   # logic, seed integrity, routes, auth  (no database)
.venv/bin/python e2e_test.py     # the whole game loop, in-memory MongoDB
```

`e2e_test.py` signs both players in, proves they receive identical sets, plays a full day,
checks the scoring bands, verifies settlement and the winner, confirms the tier only
advances when both clear 80%, and reads back the chronicle entry.

---

## 10. Design notes

The visual identity is carried over from the companion storybook so the two feel like one
product: deep forest green, bone, amber and leaf, with Pixelify Sans for display and Nunito
for body text, JetBrains Mono for code.

Two additions here:

- **A day theme.** Warm paper for daytime drilling, the night theme for evenings. The theme
  follows the clock (07:00–19:00) with a manual override, so you are never fighting the room
  you are in.
- **Language hues.** HTML `#e2a33c` and CSS `#6f9c53` are unchanged from the storybook; JS
  became a river slate `#5c8095` because it was `bone` — the body text colour — which would
  vanish on a light background. Amber stays the only UI accent; language colours only tint a
  badge or a rule.

Calm-by-construction rules, which matter more than the hexes: no pure `#fff` or `#000`,
body contrast around 12–14:1 rather than 21:1, no saturated red anywhere (a miss is
information, not an alarm), entrance-only motion gated on `prefers-reduced-motion`, one
action per screen, and no countdown timers or streak-panic.

---

## 11. Troubleshooting

| Symptom | Cause |
|---|---|
| "Cannot reach the API" | Wrong API address — click **API** in the top right and paste the Render URL. |
| First load of the day is slow | Render free tier was asleep. It wakes on first request. |
| Sign-in fails with correct details | `USERS` on Render is not valid JSON, or the name differs. |
| Browser console shows a CORS error | `ALLOWED_ORIGINS` does not exactly match your Pages origin (scheme + host, no trailing slash). |
| "No cards seeded yet" | Run the loader, or check `MONGO_URI`. The app also auto-seeds an empty database on boot. |
| `ServerSelectionTimeoutError` | Atlas Network Access is not allowing Render. Use `0.0.0.0/0`. |

---

## 12. Where this goes next

- **Pixel art.** The story images are Picsum placeholders. Swap the `image_url` values in
  `data.py` for a real set — nothing else changes.
- **More cards.** ~97 today. The `CAST` already flags Linus as "hoisting, next chapter",
  and the town clock for shorthand order.
- **A third player.** It is a config change, not a code change: add a name to `USERS` and to
  `PAIR["members"]`. The settlement logic handles two, so anything past that wants a small
  refactor to generalise the winner calculation.
