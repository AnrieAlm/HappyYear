"""End-to-end test of the full game loop, against an in-memory MongoDB.

This drives the real FastAPI app through ASGI, so it exercises the routers,
the run/attempt bookkeeping, server-side grading, settlement, tier advance and
the chronicle -- not just the pure helpers.

Installs needed: mongomock-motor, httpx (dev-only; not in requirements.txt).

Run:  cd backend && ../.venv/bin/python e2e_test.py
"""
import asyncio
import sys

from mongomock_motor import AsyncMongoMockClient
import httpx

FAIL = []
WRONG = "zzz-definitely-not-the-answer"


def check(label, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + label + ("" if cond else f"  <- {detail}"))
    if not cond:
        FAIL.append(label)


async def main() -> int:
    import app.db as dbmod

    # Point the app at an in-memory Mongo before anything touches it.
    dbmod._client = AsyncMongoMockClient()

    from app.config import settings
    from app.db import col_chronicle, col_meta, col_winners
    from app.main import app
    from app.seed.data import CARDS
    from app.seed.load import seed_all

    await seed_all()
    answers = {c["id"]: c["answer"] for c in CARDS}
    users = settings().users_map
    names = list(users.keys())
    A, B = "farmerB", "maya"
    assert A in users and B in users, f"expected farmerB/maya in USERS, got {names}"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http:
        print("\n[1] sign in")
        h = {}
        for who in (A, B):
            r = await http.post("/api/auth/login", json={"name": who, "passcode": users[who]})
            check(f"{who} can sign in", r.status_code == 200, r.text)
            h[who] = {"Authorization": "Bearer " + r.json()["token"]}

        r = await http.post("/api/auth/login", json={"name": A, "passcode": "wrong"})
        check("a wrong passcode is refused", r.status_code == 401, r.status_code)

        r = await http.get("/api/challenge/today?lang=HTML")
        check("the challenge needs a token", r.status_code in (401, 403), r.status_code)

        print("\n[2] the fairness property, through the API")
        sets = {}
        story_cards = {}
        for lang in ("HTML", "CSS", "JS"):
            seen = {}
            for who in (A, B):
                r = await http.get(f"/api/challenge/today?lang={lang}", headers=h[who])
                check(f"{who} GETs today's {lang} set", r.status_code == 200, r.text)
                body = r.json()
                seen[who] = [c["id"] for c in body["cards"]]
                check(f"{lang} card carries no answer key", all("answer" not in c for c in body["cards"]))
                check(f"{lang} set has 20 cards", len(body["cards"]) == 20, len(body["cards"]))
                check(f"{lang} starts at tier 1", body["tier"] == 1, body["tier"])
                if who == A:
                    story_cards[lang] = sum(1 for c in body["cards"] if c["story_id"])
            check(f"{lang}: both players get the identical set, in order", seen[A] == seen[B])
            sets[lang] = seen[A]

        # The mnemonic layer must be visible on day one, or the storybook is a
        # feature nobody meets until a tier advances.
        for lang in ("HTML", "CSS", "JS"):
            check(f"{lang} day-1 set includes mnemonic cards", story_cards[lang] > 0, story_cards)

        print("\n[3] playing HTML to the end")
        html = sets["HTML"]

        # A: one card wrong then right (an attempt-2 card = 60), the rest first try.
        first = html[0]
        r = await http.post("/api/session/check", headers=h[A],
                            json={"lang": "HTML", "card_id": first, "answer": WRONG, "ms": 900})
        check("a wrong answer on attempt 1 is marked incorrect", r.json()["correct"] is False, r.text)
        check("the server reports attempt 1", r.json()["attempts"] == 1, r.text)
        r = await http.post("/api/session/check", headers=h[A],
                            json={"lang": "HTML", "card_id": first, "answer": answers[first], "ms": 900})
        check("a retry is accepted", r.json()["correct"] is True, r.text)
        check("the server counts attempt 2", r.json()["attempts"] == 2, r.text)
        check("a retry scores 60, not 100", r.json()["points"] == 60, r.text)

        for cid in html[1:]:
            r = await http.post("/api/session/check", headers=h[A],
                                json={"lang": "HTML", "card_id": cid, "answer": answers[cid], "ms": 1200})
            if not r.json()["correct"]:
                check(f"first-try answer accepted for {cid}", False, r.text)
        check("first-try cards score 100", r.json()["points"] == 100, r.text)

        # B answers only half, and tries to submit early.
        r = await http.post("/api/session/check", headers=h[B],
                            json={"lang": "HTML", "card_id": html[0], "answer": answers[html[0]], "ms": 1000})
        r = await http.post("/api/session/submit", json={"lang": "HTML"}, headers=h[B])
        check("submitting an incomplete set is refused", r.status_code == 400, r.text)

        # B finishes: two cards missed twice (0 points each), rest first try.
        for cid in html[1:3]:
            await http.post("/api/session/check", headers=h[B],
                            json={"lang": "HTML", "card_id": cid, "answer": WRONG, "ms": 800})
            r = await http.post("/api/session/check", headers=h[B],
                                json={"lang": "HTML", "card_id": cid, "answer": WRONG, "ms": 800})
            check("a second miss scores 0", r.json()["points"] == 0, r.text)
        for cid in html[3:]:
            await http.post("/api/session/check", headers=h[B],
                            json={"lang": "HTML", "card_id": cid, "answer": answers[cid], "ms": 1100})

        r = await http.post("/api/session/submit", json={"lang": "HTML"}, headers=h[A])
        check(f"{A} submits HTML", r.status_code == 200, r.text)
        A_report = r.json()
        check("A scored 19*100 + 1*60", A_report["score"] == 1960, A_report)
        check("A off by 20 (a retry still counts as correct)", A_report["correct"] == 20, A_report["correct"])

        r = await http.post("/api/session/submit", json={"lang": "HTML"}, headers=h[B])
        B_report = r.json()
        check("B scored 18*100", B_report["score"] == 1800, B_report)
        check("B off by 18", B_report["correct"] == 18, B_report["correct"])

        print("\n[4] double-submit and post-submit checks are refused")
        r = await http.post("/api/session/submit", json={"lang": "HTML"}, headers=h[A])
        check("submitting twice is refused", r.status_code == 409, r.status_code)
        r = await http.post("/api/session/check", headers=h[A],
                            json={"lang": "HTML", "card_id": html[0], "answer": answers[html[0]], "ms": 100})
        check("checking after submitting is refused", r.status_code == 409, r.status_code)

        print("\n[5] settlement: a winner per language")
        r = await http.get("/api/session/result/today", headers=h[A])
        res = r.json()
        by = {l["lang"]: l for l in res["langs"]}
        check("HTML is settled once both played", by["HTML"]["settled"] is True, by["HTML"])
        check("HTML goes to the higher score", by["HTML"]["winner"] == A, by["HTML"])
        check("HTML is not a tie", by["HTML"]["tie"] is False, by["HTML"])
        check("both scores visible after both played",
              by["HTML"]["scores"] == {A: 1960, B: 1800}, by["HTML"]["scores"])
        check("CSS is not settled yet", by["CSS"]["settled"] is False, by["CSS"])
        check("CSS hides the scores while open", by["CSS"]["scores"] == {}, by["CSS"])
        check("JS reports who has played", by["JS"]["submitted"] == {A: False, B: False}, by["JS"]["submitted"])

        print("\n[6] tier advances only when BOTH clear 80%")
        pair = await col_meta().find_one({"_id": "pair"})
        check("HTML tier moved to 2 (A 100%, B 90%)", pair["current_tier"]["HTML"] == 2, pair["current_tier"])
        check("CSS tier stays at 1", pair["current_tier"]["CSS"] == 1, pair["current_tier"])
        check("JS tier stays at 1", pair["current_tier"]["JS"] == 1, pair["current_tier"])

        win = await col_winners().find_one({"lang": "HTML"})
        check("tier advance is recorded once", win.get("tier_advanced") is True, win)

        print("\n[7] the chronicle was written")
        entry = await col_chronicle().find_one({"lang": "HTML"})
        check("an HTML chronicle entry exists", entry is not None, entry)
        if entry:
            check("the entry names the winner", A in entry["text"], entry["text"])
            check("the entry reads as prose", len(entry["text"]) > 40, entry["text"])
            print("        ->", entry["text"])

        print("\n[8] progress and wins tally")
        r = await http.get("/api/progress", headers=h[A])
        prog = r.json()
        check("progress returns the partner", prog["partner"] == B, prog)
        by_lang = {l["lang"]: l for l in prog["langs"]}
        check("A has 1 HTML win", by_lang["HTML"]["wins"] == 1, by_lang["HTML"])
        check("A has 0 CSS wins", by_lang["CSS"]["wins"] == 0, by_lang["CSS"])
        check("HTML now shows tier 2", by_lang["HTML"]["tier"] == 2, by_lang["HTML"])
        check("every language reports a card count", all(l["total_cards"] >= 20 for l in prog["langs"]),
              {l["lang"]: l["total_cards"] for l in prog["langs"]})
        check("streak is 1 today", prog["streak"] == 1, prog["streak"])
        check("no exam date set yet", prog["days_to_exam"] is None, prog["days_to_exam"])

        print("\n[9] the story reteach path")
        r = await http.get("/api/storybook")
        book = r.json()
        check("storybook is public", r.status_code == 200, r.status_code)
        check("9 stories served", len(book["stories"]) == 9, len(book["stories"]))
        check("cast served", len(book["cast"]) == 9, len(book["cast"]))
        check("a story carries its paragraphs", all(s["body"] for s in book["stories"]))

        r = await http.get(f"/api/challenge/today?lang=CSS", headers=h[A])
        css_cards = {c["id"]: c for c in r.json()["cards"]}
        linked = [c for c in css_cards.values() if c["story_id"]]
        check("CSS set contains story-linked cards", len(linked) > 0, len(linked))
        if linked:
            s = linked[0]
            story = next((x for x in book["stories"] if x["story_id"] == s["story_id"]), None)
            check("the linked story exists", story is not None, s["story_id"])
            check("the beat indexes a real paragraph",
                  story is not None and 0 <= s["beat"] < len(story["body"]), (s.get("beat"), len(story["body"])))

        print("\n[10] personal review segment")
        r = await http.get("/api/review/due?lang=HTML", headers=h[A])
        due = r.json()
        check("review queue answers", r.status_code == 200, r.text)
        check("everything just answered is no longer due", len(due["cards"]) == 0, due)

    print("\n" + "=" * 62)
    if FAIL:
        print(f"{len(FAIL)} CHECK(S) FAILED:")
        for f in FAIL:
            print("  -", f)
        return 1
    print("ALL E2E CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
