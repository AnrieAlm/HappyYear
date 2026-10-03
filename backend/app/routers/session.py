"""The scored Daily Challenge.

Integrity note: the attempt counter lives on the SERVER (a `runs` document),
never in the client payload. Grading one card at a time is what gives the
player immediate feedback, but if the client supplied its own `attempts`, a
player could call /check to harvest an answer and then submit it claiming
first-try. Here, every /check increments the stored counter, so harvesting a
reveal is self-defeating: the card can only ever score as after-retry.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from ..config import settings
from ..daily import date_key, pick_daily, utc_now
from ..db import col_cards, col_runs, col_submissions
from ..models import (
    AnswerIn,
    CardResult,
    CheckIn,
    CheckOut,
    HintIn,
    SubmitIn,
    SubmitOut,
)
from ..scoring import grade_answer, points_for
from ..security import current_user
from ..services.reviews import record
from ..services.settle import settle_day
from ..state import pool_ids, tier_for

router = APIRouter(prefix="/api/session", tags=["session"])


async def _daily_ids(lang: str) -> list[str]:
    key = date_key()
    tier = await tier_for(lang)
    return pick_daily(await pool_ids(lang, tier), key, lang, settings().daily_size)


async def _already_submitted(user: str, lang: str, key: str) -> bool:
    return bool(
        await col_submissions().find_one(
            {"date_key": key, "lang": lang, "user": user}, {"_id": 1}
        )
    )


@router.post("/check", response_model=CheckOut)
async def check(body: CheckIn, user: str = Depends(current_user)) -> CheckOut:
    key = date_key()
    if await _already_submitted(user, body.lang, key):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "You already submitted today for this language."
        )

    card = await col_cards().find_one({"id": body.card_id})
    if not card:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown card")

    run = await col_runs().find_one(
        {"date_key": key, "lang": body.lang, "user": user}
    ) or {}
    prev = (run.get("checks") or {}).get(body.card_id) or {}

    attempts = int(prev.get("attempts", 0)) + 1
    hint_used = bool(prev.get("hint_used") or body.hint_used)
    # keep the FIRST reported duration; it can never be revised downward
    ms = int(prev.get("ms") or max(0, body.ms))

    result = grade_answer(
        card,
        AnswerIn(
            card_id=body.card_id,
            answer=body.answer,
            attempts=attempts,
            hint_used=hint_used,
            ms=ms,
        ),
    )

    await col_runs().update_one(
        {"date_key": key, "lang": body.lang, "user": user},
        {
            "$set": {
                f"checks.{body.card_id}": {
                    "attempts": attempts,
                    "hint_used": hint_used,
                    "correct": result.correct,
                    "ms": ms,
                },
                "updated_at": utc_now(),
            },
            "$setOnInsert": {
                "date_key": key,
                "lang": body.lang,
                "user": user,
                "started_at": utc_now(),
            },
        },
        upsert=True,
    )

    return CheckOut(attempts=attempts, **result.model_dump())


@router.post("/hint")
async def hint(body: HintIn, user: str = Depends(current_user)) -> dict:
    """Record that the hint was opened. A hint is not an attempt, but it does
    cap the card at 30 points."""
    key = date_key()
    await col_runs().update_one(
        {"date_key": key, "lang": body.lang, "user": user},
        {
            "$set": {
                f"checks.{body.card_id}.hint_used": True,
                "updated_at": utc_now(),
            },
            "$setOnInsert": {
                "date_key": key,
                "lang": body.lang,
                "user": user,
                "started_at": utc_now(),
            },
        },
        upsert=True,
    )
    return {"ok": True}


@router.post("/submit", response_model=SubmitOut)
async def submit(body: SubmitIn, user: str = Depends(current_user)) -> SubmitOut:
    key = date_key()
    if await _already_submitted(user, body.lang, key):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "You already submitted today for this language."
        )

    run = await col_runs().find_one(
        {"date_key": key, "lang": body.lang, "user": user}
    )
    checks: dict = (run or {}).get("checks") or {}
    ids = await _daily_ids(body.lang)

    missing = [c for c in ids if not (checks.get(c) or {}).get("attempts")]
    if missing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Answer every card before submitting -- {len(missing)} still open.",
        )

    docs = {d["id"]: d async for d in col_cards().find({"id": {"$in": ids}})}

    results: list[CardResult] = []
    for cid in ids:
        st = checks.get(cid) or {}
        card = docs.get(cid)
        if card is None:
            continue
        correct = bool(st.get("correct"))
        results.append(
            CardResult(
                card_id=cid,
                correct=correct,
                canonical=card["answer"],
                points=points_for(
                    correct, int(st.get("attempts", 1)), bool(st.get("hint_used"))
                ),
                story_id=card.get("story_id"),
                beat=card.get("beat"),
            )
        )

    score = sum(r.points for r in results)
    correct_count = sum(1 for r in results if r.correct)
    time_ms = sum(int((checks.get(c) or {}).get("ms") or 0) for c in ids)

    await col_submissions().insert_one(
        {
            "date_key": key,
            "lang": body.lang,
            "user": user,
            "score": score,
            "correct": correct_count,
            "total": len(results),
            "time_ms": time_ms,
            "tier_at": await tier_for(body.lang),
            "results": [
                {"card_id": r.card_id, "correct": r.correct, "points": r.points}
                for r in results
            ],
            "submitted_at": utc_now(),
        }
    )

    answers = [
        AnswerIn(
            card_id=cid,
            attempts=int((checks.get(cid) or {}).get("attempts", 1)),
            hint_used=bool((checks.get(cid) or {}).get("hint_used")),
            ms=int((checks.get(cid) or {}).get("ms") or 0),
        )
        for cid in ids
    ]
    await record(user, body.lang, answers, results, utc_now())
    await col_runs().update_one(
        {"date_key": key, "lang": body.lang, "user": user},
        {"$set": {"submitted": True, "submitted_at": utc_now()}},
    )

    return SubmitOut(
        lang=body.lang,
        date_key=key,
        score=score,
        correct=correct_count,
        total=len(results),
        time_ms=time_ms,
        results=results,
    )


@router.get("/result/today")
async def result_today(user: str = Depends(current_user)) -> dict:
    """Settle lazily on read. The other player's score is withheld until both
    have submitted, so nobody can calibrate off a visible target."""
    key = date_key()
    langs = await settle_day(key)
    both = all(all(l.submitted.values()) for l in langs)
    out = []
    for l in langs:
        out.append(
            {
                "lang": l.lang,
                "settled": l.settled,
                "winner": l.winner,
                "tie": l.tie,
                "submitted": l.submitted,
                "scores": {} if not l.settled else l.scores,
                "your_score": l.scores.get(user, 0) if l.settled else None,
            }
        )
    return {"date_key": key, "both_submitted": both, "langs": out, "you": user}
