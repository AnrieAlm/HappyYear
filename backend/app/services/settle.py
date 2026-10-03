"""Settlement: decide the day's winner for each language and write the chronicle.

Runs lazily on read rather than on a cron, which matters on Render's free tier
where a scheduled job is an extra moving part. A day settles when BOTH players
have submitted, or when the day is over and only one of them showed up.

Also owns tier advancement: a tier moves up only when both players clear 80%
on the same day, so the two stay in lock-step.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..daily import date_key, days_between, is_past_key
from ..db import col_chronicle, col_submissions, col_winners
from ..models import LangResult
from ..state import LANGS, get_pair, save_pair

ADVANCE_AT = 0.80


def _give_up(score: int) -> str:
    if score == 0:
        return "asleep in the barn"
    if score < 150:
        return "off to a slow start"
    return "close behind"


async def settle_day(key: str) -> list[LangResult]:
    pair = await get_pair()
    members: list[str] = list(pair.get("members") or [])
    a, b = (members + ["", ""])[0], (members + ["", ""])[1]
    closed = is_past_key(key)
    out: list[LangResult] = []

    for lang in LANGS:
        subs = {
            d["user"]: d
            async for d in col_submissions().find({"date_key": key, "lang": lang})
        }
        scores = {m: int(subs[m]["score"]) if m in subs else 0 for m in (a, b)}
        submitted = {m: m in subs for m in (a, b)}

        both = all(submitted.values())
        any_one = any(submitted.values())

        if not any_one or (not both and not closed):
            # Still waiting on the other player, and the day is not over.
            out.append(
                LangResult(lang=lang, settled=False, scores=scores, submitted=submitted)
            )
            continue

        contenders = [m for m in (a, b) if submitted[m]]
        best = max(scores[m] for m in contenders)
        leaders = [m for m in contenders if scores[m] == best]
        tie = len(leaders) > 1
        winner = None if tie else leaders[0]

        await col_winners().update_one(
            {"date_key": key, "lang": lang},
            {
                "$set": {
                    "date_key": key,
                    "lang": lang,
                    "winner": winner,
                    "tie": tie,
                    "scores": scores,
                    "settled_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

        loser = b if (winner or "") == a else a
        if tie:
            text = (
                f"{key} · {lang} ended level at {best}. "
                f"Both farmers walk away with the points."
            )
        elif len(contenders) == 1:
            text = (
                f"{key} · {lang} went to {winner} by walkover -- "
                f"{loser} never made it out to the plot."
            )
        else:
            text = (
                f"{key} · {lang} went to {winner} on {best}, "
                f"with {loser} {_give_up(scores[loser])} on {scores[loser]}."
            )

        await col_chronicle().update_one(
            {"date_key": key, "lang": lang},
            {
                "$setOnInsert": {
                    "date_key": key,
                    "lang": lang,
                    "text": text,
                    "winner": winner,
                }
            },
            upsert=True,
        )

        # --- tier advance: both players must clear the bar on the same day ---
        if both and (pair.get("current_tier") or {}).get(lang, 1) < 3:
            win_doc = await col_winners().find_one({"date_key": key, "lang": lang})
            if not (win_doc or {}).get("tier_advanced"):
                accs = [
                    (subs[m].get("correct", 0) / max(1, subs[m].get("total", 0)))
                    for m in (a, b)
                ]
                if all(acc >= ADVANCE_AT for acc in accs):
                    tiers = dict(pair.get("current_tier") or {})
                    tiers[lang] = int(tiers.get(lang, 1)) + 1
                    pair["current_tier"] = tiers
                    await save_pair(pair)
                    await col_winners().update_one(
                        {"date_key": key, "lang": lang},
                        {"$set": {"tier_advanced": True, "advanced_to": tiers[lang]}},
                    )

        out.append(
            LangResult(lang=lang, settled=True, winner=winner, tie=tie,
                       scores=scores, submitted=submitted)
        )

    return out


async def sweep_unsettled(days: int = 14) -> None:
    """Settle any recent past days that never got a second submission, so the
    chronicle has no holes. Cheap: winners/ chronicle upserts are idempotent."""
    today = date_key()
    keys: set[str] = set()
    async for d in col_submissions().find({}, {"date_key": 1}):
        k = d["date_key"]
        if k < today:
            keys.add(k)

    for k in sorted(keys)[-days:]:
        if 0 < days_between(k, today) <= days:
            await settle_day(k)
