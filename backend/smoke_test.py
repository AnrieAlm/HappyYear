"""Smoke test for the pieces that decide whether this app is correct:
deterministic daily sets, SM-2 progression, scoring, and seed-data integrity.

Run:  cd backend && PYTHONPATH=. ../.venv/bin/python ../smoke_test.py
"""
import sys
from datetime import datetime, timedelta, timezone
from collections import Counter

FAIL = []


def check(label, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + label + ("" if cond else f"  <- {detail}"))
    if not cond:
        FAIL.append(label)


print("\n[1] seed data integrity")
from app.seed.data import CARDS, STORIES, CAST, BASIC_CARDS, STORY_CARDS

ids = [c["id"] for c in CARDS]
dupes = [i for i, n in Counter(ids).items() if n > 1]
check("card ids unique", not dupes, f"dupes={dupes}")
check("card count ~97", 90 <= len(CARDS) <= 105, f"got {len(CARDS)}")
check("story cards == 30", len(STORY_CARDS) == 30, f"got {len(STORY_CARDS)}")
check("9 stories", len(STORIES) == 9, f"got {len(STORIES)}")
check("cast populated", len(CAST) == 9, f"got {len(CAST)}")

langs = Counter(c["lang"] for c in CARDS)
check("all three languages seeded", set(langs) == {"HTML", "CSS", "JS"}, str(dict(langs)))
check("each language has >= 20 cards", all(langs[l] >= 20 for l in ("HTML", "CSS", "JS")), str(dict(langs)))

story_langs = Counter(s["language"] for s in STORIES)
check("3 stories per language", all(story_langs[l] == 3 for l in ("HTML", "CSS", "JS")), str(dict(story_langs)))

check("tiers are 1..3", all(c["tier"] in (1, 2, 3) for c in CARDS))
check("every card has a prompt and answer", all(c["prompt"] and c["answer"] for c in CARDS))

sids = {s["story_id"]: s for s in STORIES}
bad_ref, bad_beat = [], []
for c in CARDS:
    if c["story_id"] is None:
        continue
    s = sids.get(c["story_id"])
    if s is None:
        bad_ref.append(c["id"])
    elif c["beat"] is None or not (0 <= c["beat"] < len(s["body"])):
        bad_beat.append((c["id"], c["beat"], len(s["body"])))
check("every story_id exists", not bad_ref, str(bad_ref))
check("every beat indexes a real paragraph", not bad_beat, str(bad_beat))
check("story cards have a hint", all(c["hint"] for c in STORY_CARDS))


print("\n[2] scoring")
from app.scoring import normalize, points_for, grade_answer
from app.models import AnswerIn

check("normalize lowercases", normalize("  HREF ") == "href")
check("normalize collapses whitespace", normalize("call,   apply and bind") == "call, apply and bind")
check("normalize strips a trailing semicolon", normalize("color;") == "color")
check("normalize folds smart quotes", normalize("\u201c5\u201d") == '"5"')

check("first try = 100", points_for(True, 1, False) == 100)
check("retry = 60", points_for(True, 2, False) == 60)
check("hint = 30", points_for(True, 1, True) == 30)
check("wrong = 0", points_for(False, 1, False) == 0)
check("hint beats a clean first try", points_for(True, 1, True) == 30)

card = {"id": "x", "answer": "justify-content", "accept": ["justify"], "story_id": "house-of-axes", "beat": 0}
check("exact answer grades correct", grade_answer(card, AnswerIn(card_id="x", answer="justify-content")).correct)
check("accept-list variant grades correct", grade_answer(card, AnswerIn(card_id="x", answer="  JUSTIFY ")).correct)
check("case-insensitive", grade_answer(card, AnswerIn(card_id="x", answer="Justify")).correct)
check("wrong answer grades incorrect", not grade_answer(card, AnswerIn(card_id="x", answer="align-items")).correct)
check("empty answer never grades correct", not grade_answer(card, AnswerIn(card_id="x", answer="   ")).correct)


print("\n[3] SM-2 progression")
from app.srs import apply, new_state, from_correct, is_due

now = datetime(2026, 10, 3, tzinfo=timezone.utc)
st = new_state()
first = apply(st, 2, now)          # good
check("first good -> 1 day", first["interval"] == 1, str(first))
second = apply(first, 2, now)
check("second good -> 3 days", second["interval"] == 3, str(second))
third = apply(second, 2, now)
check("third good -> ~7 days", 6 <= third["interval"] <= 8, str(third))
check("reps accumulate", third["reps"] == 3)
check("due date moves forward", third["due"] > now)

hard_after = apply(third, 1, now)
check("hard shortens the next interval", hard_after["interval"] < round(third["interval"] * third["ease"]))
check("hard lowers ease", hard_after["ease"] < third["ease"])

lapsed = apply(third, 0, now)
check("again resets reps", lapsed["reps"] == 0)
check("again counts a lapse", lapsed["lapses"] == 1)
check("again is due immediately", lapsed["interval"] == 0)

check("ease never below floor", apply({**new_state(), "ease": 1.31}, 1, now)["ease"] >= 1.3)
easy_chain = new_state()
for _ in range(6):
    easy_chain = apply(easy_chain, 3, now)
check("easy raises ease but is capped", easy_chain["ease"] <= 3.0, str(easy_chain["ease"]))
check("interval is capped at 180", easy_chain["interval"] <= 180, str(easy_chain["interval"]))

check("missing state is due", is_due(None, now))
check("future due is not due", not is_due({"due": now + timedelta(days=3)}, now))
check("past due is due", is_due({"due": now - timedelta(days=1)}, now))

check("from_correct: miss -> again", from_correct(False, 1, False) == 0)
check("from_correct: hint -> hard", from_correct(True, 1, True) == 1)
check("from_correct: retry -> hard", from_correct(True, 2, False) == 1)
check("from_correct: clean -> good", from_correct(True, 1, False) == 2)


print("\n[4] deterministic daily set (the fairness property)")
from app.daily import pick_daily, day_seed, date_key

pool = [c["id"] for c in CARDS if c["lang"] == "HTML"]
a = pick_daily(pool, "2026-10-03", "HTML", 20)
b = pick_daily(pool, "2026-10-03", "HTML", 20)
check("same date+lang -> identical list", a == b)
check("order is stable too", a == list(b))
check("picks the requested size", len(a) == 20, f"got {len(a)}")
check("no duplicates in the set", len(set(a)) == len(a))
check("all picks come from the pool", set(a) <= set(pool))

c = pick_daily(pool, "2026-10-04", "HTML", 20)
check("a new day gives a different set", a != c)
check("different language gives a different set", pick_daily(pool, "2026-10-03", "CSS", 20) != a)
check("shuffled pool order does not matter", pick_daily(list(reversed(pool)), "2026-10-03", "HTML", 20) == a)
check("seed is a stable int", day_seed("2026-10-03", "HTML") == day_seed("2026-10-03", "HTML"))
check("date_key format", len(date_key()) == 10 and date_key()[4] == "-", date_key())
check("oversized request is clipped to the pool", len(pick_daily(pool, "2026-10-03", "HTML", 999)) == len(set(pool)))


print("\n[5] auth")
from app.security import issue_token, verify_passcode
import jwt as pyjwt
from app.config import settings

tok = issue_token("farmerB")
payload = pyjwt.decode(tok, settings().jwt_secret, algorithms=["HS256"])
check("token carries the subject", payload["sub"] == "farmerB")
check("correct passcode accepted", verify_passcode("farmerB", settings().users_map["farmerB"]))
check("wrong passcode rejected", not verify_passcode("farmerB", "nope"))
check("unknown user rejected", not verify_passcode("maya-x", "changeme"))
check("allowlist has exactly 2 players", len(settings().users_map) == 2, str(list(settings().users_map)))


print("\n[6] app imports cleanly")
import app.main as main

# FastAPI registers included routers as nested objects, so read the OpenAPI
# schema rather than walking app.routes directly.
paths = set(main.app.openapi().get("paths", {}).keys())
for want in ("/api/auth/login", "/api/challenge/today", "/api/session/check",
             "/api/session/submit", "/api/session/hint", "/api/session/result/today",
             "/api/review/due", "/api/review/submit", "/api/progress",
             "/api/chronicle", "/api/storybook", "/api/health"):
    check(f"route {want}", want in paths, str(sorted(paths)))


print("\n[7] CORS + health wiring")
check("CORS middleware installed",
      any("CORSMiddleware" in str(m) for m in main.app.user_middleware), str(main.app.user_middleware))
check("lifespan attached", main.app.router.lifespan_context is not None)


print("\n" + "=" * 62)
if FAIL:
    print(f"{len(FAIL)} CHECK(S) FAILED:")
    for f in FAIL:
        print("  -", f)
    sys.exit(1)
print("ALL CHECKS PASSED")
