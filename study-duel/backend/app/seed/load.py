"""Loader for the seed content. Idempotent: safe to run repeatedly.

    python -m app.seed.load            # upsert stories, cards and the pair doc
    python -m app.seed.load --force    # wipe cards/stories first (keeps play history)

Card and story docs are upserted by id, so editing data.py and re-running
updates the content without touching anyone's progress or submissions.
"""
from __future__ import annotations

import asyncio
import sys

from ..db import client, col_cards, col_meta, col_stories, ensure_indexes
from .data import CARDS, PAIR, STORIES


async def seed_all(force: bool = False) -> dict:
    await ensure_indexes()
    if force:
        await col_cards().delete_many({})
        await col_stories().delete_many({})

    for s in STORIES:
        await col_stories().update_one({"story_id": s["story_id"]}, {"$set": s}, upsert=True)

    for card in CARDS:
        await col_cards().update_one({"id": card["id"]}, {"$set": card}, upsert=True)

    if not await col_meta().find_one({"_id": "pair"}):
        await col_meta().insert_one({"_id": "pair", **PAIR})

    return {
        "stories": await col_stories().count_documents({}),
        "cards": await col_cards().count_documents({}),
        "html": await col_cards().count_documents({"lang": "HTML"}),
        "css": await col_cards().count_documents({"lang": "CSS"}),
        "js": await col_cards().count_documents({"lang": "JS"}),
        "with_story": await col_cards().count_documents({"story_id": {"$ne": None}}),
    }


async def _main() -> None:
    stats = await seed_all(force="--force" in sys.argv)
    print("seeded:", stats)
    client().close()


if __name__ == "__main__":
    asyncio.run(_main())
