from fastapi import APIRouter, Depends, Query, status

from ..config import settings
from ..daily import utc_now
from ..db import col_cards
from ..models import CardOut, ReviewIn, ReviewOut
from ..scoring import grade_answer
from ..security import current_user
from ..services.reviews import due_for, record
from ..state import tier_for

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/due")
async def due(
    lang: str = Query(...),
    user: str = Depends(current_user),
) -> dict:
    tier = await tier_for(lang)
    ids, total = await due_for(user, lang, tier, utc_now())
    ids = ids[: settings().review_size]
    docs = {}
    async for d in col_cards().find({"id": {"$in": ids}}):
        docs[d["id"]] = d
    cards = [
        CardOut(
            id=c["id"], lang=c["lang"], tier=c["tier"], prompt=c["prompt"],
            hint=c.get("hint"), code=bool(c.get("code")),
            story_id=c.get("story_id"), beat=c.get("beat"),
        )
        for cid in ids
        if (c := docs.get(cid))
    ]
    return {"lang": lang, "cards": cards, "due_total": total}


@router.post("/submit", response_model=ReviewOut)
async def submit(body: ReviewIn, user: str = Depends(current_user)) -> ReviewOut:
    """The personal review segment. Unscored by design: if retention points
    counted, the competition would start bending the study schedule."""
    wanted = [a.card_id for a in body.answers]
    docs = {d["id"]: d async for d in col_cards().find({"id": {"$in": wanted}})}
    results = [
        grade_answer(docs[a.card_id], a) for a in body.answers if a.card_id in docs
    ]
    await record(user, body.lang, body.answers, results, utc_now())

    tier = await tier_for(body.lang)
    _, total_due = await due_for(user, body.lang, tier, utc_now())
    return ReviewOut(lang=body.lang, graded=results, due_next=total_due)
