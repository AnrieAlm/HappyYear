from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..config import settings
from ..daily import date_key, pick_daily
from ..db import col_cards, col_submissions
from ..models import CardOut, ChallengeOut, Lang
from ..security import current_user
from ..state import pool_ids, tier_for

router = APIRouter(prefix="/api/challenge", tags=["challenge"])


@router.get("/today", response_model=ChallengeOut)
async def today(lang: Lang = Query(...), user: str = Depends(current_user)) -> ChallengeOut:
    """The scored set for today. Both players get the identical list, because
    it is derived from sha256(date_key + lang) over a sorted pool -- no shared
    state, no coordination."""
    key = date_key()
    tier = await tier_for(lang)
    ids = await pool_ids(lang, tier)
    if not ids:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "No cards seeded yet. Run `python -m app.seed.load`.",
        )

    picked = pick_daily(ids, key, lang, settings().daily_size)
    docs = {}
    async for d in col_cards().find({"id": {"$in": picked}}):
        docs[d["id"]] = d

    cards = [
        CardOut(
            id=c["id"],
            lang=c["lang"],
            tier=c["tier"],
            prompt=c["prompt"],
            hint=c.get("hint"),
            code=bool(c.get("code")),
            story_id=c.get("story_id"),
            beat=c.get("beat"),
        )
        for cid in picked
        if (c := docs.get(cid))
    ]

    sub = await col_submissions().find_one(
        {"date_key": key, "lang": lang, "user": user}
    )
    return ChallengeOut(
        date_key=key,
        lang=lang,
        tier=tier,
        cards=cards,
        submitted=bool(sub),
        score=(sub or {}).get("score"),
    )
