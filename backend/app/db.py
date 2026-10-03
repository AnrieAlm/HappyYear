"""Mongo connection helpers. The client is created on first use so importing
the app never opens a socket (matters for build/test steps)."""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import settings

_client: AsyncIOMotorClient | None = None


def client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings().mongo_uri, tz_aware=True)
    return _client


def db() -> AsyncIOMotorDatabase:
    return client()[settings().mongo_db]


# --- collections -----------------------------------------------------------
def col_cards():        return db()["cards"]
def col_stories():      return db()["stories"]
def col_reviews():      return db()["reviews"]
def col_challenges():   return db()["daily_challenges"]
def col_submissions():  return db()["submissions"]
def col_runs():         return db()["runs"]
def col_winners():      return db()["winners"]
def col_chronicle():    return db()["chronicle"]
def col_meta():         return db()["meta"]


async def ensure_indexes() -> None:
    """Idempotent. Called once on startup."""
    await col_cards().create_index("id", unique=True)
    await col_cards().create_index([("lang", 1), ("tier", 1)])
    await col_stories().create_index("story_id", unique=True)
    await col_reviews().create_index([("user", 1), ("card_id", 1)], unique=True)
    await col_reviews().create_index([("user", 1), ("due", 1)])
    await col_challenges().create_index([("date_key", 1), ("lang", 1)], unique=True)
    await col_submissions().create_index(
        [("date_key", 1), ("lang", 1), ("user", 1)], unique=True
    )
    await col_winners().create_index([("date_key", 1), ("lang", 1)], unique=True)
    await col_runs().create_index(
        [("date_key", 1), ("lang", 1), ("user", 1)], unique=True
    )
    await col_chronicle().create_index([("date_key", 1), ("lang", 1)], unique=True)


async def ping() -> bool:
    await client().admin.command("ping")
    return True
