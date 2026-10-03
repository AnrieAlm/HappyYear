from fastapi import APIRouter, Depends, Query

from ..daily import date_key, days_between, utc_now
from ..db import col_chronicle, col_submissions
from ..models import ChronicleEntry, LangProgress, ProgressOut
from ..security import current_user
from ..services.reviews import due_for
from ..state import (
    LANGS,
    card_count,
    get_pair,
    partner_of,
    season_streak,
    seen_count,
    tier_for,
    wins_tally,
)

router = APIRouter(prefix="/api", tags=["progress"])


async def _accuracy(user: str, lang: str) -> float:
    correct = total = 0
    async for d in col_submissions().find({"user": user, "lang": lang}):
        correct += int(d.get("correct", 0))
        total += int(d.get("total", 0))
    return round(correct / total, 4) if total else 0.0


@router.get("/progress", response_model=ProgressOut)
async def progress(user: str = Depends(current_user)) -> ProgressOut:
    pair = await get_pair()
    tally = await wins_tally()
    now = utc_now()
    today = date_key()
    exam = pair.get("exam_date")

    langs: list[LangProgress] = []
    for lang in LANGS:
        tier = await tier_for(lang)
        _, due_total = await due_for(user, lang, tier, now)
        langs.append(
            LangProgress(
                lang=lang,
                tier=tier,
                total_cards=await card_count(lang),
                seen=await seen_count(user, lang),
                due=due_total,
                wins=tally.get(lang, {}).get(user, 0),
                accuracy=await _accuracy(user, lang),
            )
        )

    return ProgressOut(
        name=user,
        partner=await partner_of(user),
        exam_date=exam,
        streak=await season_streak(),
        days_to_exam=days_between(today, exam) if exam else None,
        langs=langs,
    )


@router.get("/chronicle", response_model=list[ChronicleEntry])
async def chronicle(limit: int = Query(60, ge=1, le=400)) -> list[ChronicleEntry]:
    out: list[ChronicleEntry] = []
    async for d in col_chronicle().find({}).sort([("date_key", -1), ("lang", 1)]).limit(limit):
        out.append(
            ChronicleEntry(
                date_key=d["date_key"],
                lang=d["lang"],
                text=d.get("text", ""),
                winner=d.get("winner"),
            )
        )
    return out
