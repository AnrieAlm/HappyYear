"""The day boundary and the deterministic daily set.

Fairness rests on one property: given the same date_key and the same tier, both
players must receive the byte-identical card list, in the same order. That is
achieved by seeding a PRNG from sha256(date_key + lang) over a canonically
sorted pool -- no shared state, no coordination, no race at midnight.
"""
from __future__ import annotations

import hashlib
import random
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from .config import settings


def now_local() -> datetime:
    return datetime.now(ZoneInfo(settings().day_tz))


def date_key(moment: datetime | None = None) -> str:
    """YYYY-MM-DD in the shared timezone. Never uses the device clock."""
    m = moment or now_local()
    if m.tzinfo is None:
        m = m.replace(tzinfo=ZoneInfo(settings().day_tz))
    return m.astimezone(ZoneInfo(settings().day_tz)).date().isoformat()


def is_past_key(key: str) -> bool:
    return key < date_key()


def day_seed(key: str, lang: str) -> int:
    digest = hashlib.sha256(f"{key}:{lang}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def pick_daily(card_ids: list[str], key: str, lang: str, size: int) -> list[str]:
    """Deterministic, order-stable selection. Sorted input is what makes it
    reproducible across processes and across players."""
    pool = sorted(set(card_ids))
    rng = random.Random(day_seed(key, lang))
    rng.shuffle(pool)
    return pool[:size]


def days_between(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
