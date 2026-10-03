"""The single `pair` document: who plays, the exam date, and each language's
current tier. Tiers advance as a PAIR, never individually -- otherwise the
deterministic daily sets stop being comparable between the two players."""
from __future__ import annotations

from .config import settings
from .db import col_meta, col_reviews, col_submissions, col_winners, col_cards
from .seed import data as seed_data

PAIR_KEY = "pair"

LANGS = ["HTML", "CSS", "JS"]


async def get_pair() -> dict:
    doc = await col_meta().find_one({"_id": PAIR_KEY})
    if doc:
        return doc
    fresh = {"_id": PAIR_KEY, **seed_data.PAIR}
    await col_meta().insert_one(fresh)
    return fresh


async def save_pair(pair: dict) -> None:
    await col_meta().replace_one({"_id": PAIR_KEY}, pair, upsert=True)


async def partner_of(user: str) -> str:
    pair = await get_pair()
    members = pair.get("members") or []
    others = [m for m in members if m != user]
    return others[0] if others else ""


async def tier_for(lang: str) -> int:
    pair = await get_pair()
    return int((pair.get("current_tier") or {}).get(lang, 1))


async def pool_ids(lang: str, tier: int) -> list[str]:
    """Everything at or below the current tier, so each day rotates across all
    material learned so far rather than repeating one tier."""
    cursor = col_cards().find({"lang": lang, "tier": {"$lte": tier}}, {"id": 1})
    return [d["id"] async for d in cursor]


async def wins_tally() -> dict[str, dict[str, int]]:
    """lang -> {user: wins}"""
    tally: dict[str, dict[str, int]] = {lang: {} for lang in LANGS}
    pair = await get_pair()
    for member in pair.get("members") or []:
        for lang in LANGS:
            tally[lang][member] = 0
    async for doc in col_winners().find({"winner": {"$ne": None}}):
        lang = doc.get("lang")
        winner = doc.get("winner")
        if lang in tally and winner in tally[lang]:
            tally[lang][winner] += 1
    return tally


async def season_streak() -> int:
    """Consecutive days (ending today or yesterday) on which at least one
    submission was recorded. Counting pair activity, not individual."""
    keys: list[str] = []
    async for doc in col_submissions().find({}, {"date_key": 1}).sort("date_key", -1):
        k = doc["date_key"]
        if not keys or keys[-1] != k:
            keys.append(k)
    if not keys:
        return 0
    from .daily import date_key as today_key, days_between

    today = today_key()
    if keys[0] != today and days_between(keys[0], today) > 1:
        return 0
    streak = 1
    for a, b in zip(keys, keys[1:]):
        if days_between(b, a) == 1:
            streak += 1
        else:
            break
    return streak


async def card_count(lang: str) -> int:
    return await col_cards().count_documents({"lang": lang})


async def seen_count(user: str, lang: str) -> int:
    ids = {d["id"] async for d in col_cards().find({"lang": lang}, {"id": 1})}
    if not ids:
        return 0
    return await col_reviews().count_documents({"user": user, "card_id": {"$in": list(ids)}})
