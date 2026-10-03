"""Recording reviews (SM-2) and finding what is due."""
from __future__ import annotations

from datetime import datetime

from ..db import col_reviews
from ..models import AnswerIn, CardResult
from ..srs import apply, from_correct, is_due
from ..state import pool_ids


async def record(
    user: str,
    lang: str,
    answers: list[AnswerIn],
    results: list[CardResult],
    now: datetime,
) -> int:
    """Apply each graded answer to that player's own schedule. The grade is
    inferred from how the answer actually went, so the player never has to
    think in SM-2 terms."""
    by_id = {r.card_id: r for r in results}
    touched = 0
    for a in answers:
        r = by_id.get(a.card_id)
        if r is None:
            continue
        grade = from_correct(r.correct, a.attempts, a.hint_used)
        current = await col_reviews().find_one({"user": user, "card_id": a.card_id})
        nxt = apply(current, grade, now)
        await col_reviews().update_one(
            {"user": user, "card_id": a.card_id},
            {
                "$set": {
                    "user": user,
                    "card_id": a.card_id,
                    "lang": lang,
                    "last_grade": grade,
                    "updated_at": now,
                    **nxt,
                }
            },
            upsert=True,
        )
        touched += 1
    return touched


async def due_for(user: str, lang: str, tier: int, now: datetime) -> tuple[list[str], int]:
    """Return (ordered id list, total due count) for the personal review run."""
    ids = await pool_ids(lang, tier)
    if not ids:
        return [], 0
    states = {
        d["card_id"]: d
        async for d in col_reviews().find({"user": user, "card_id": {"$in": ids}})
    }

    def sort_key(cid: str):
        due = (states.get(cid) or {}).get("due")
        return (due.isoformat() if due else "", cid)

    # Only cards the player has actually answered can be "due". Unseen cards are
    # the daily challenge's job; counting them here would inflate the Due stat
    # and duplicate the challenge's work in the review run.
    due = sorted(
        (cid for cid in ids if cid in states and is_due(states.get(cid), now)),
        key=sort_key,
    )
    return due, len(due)
