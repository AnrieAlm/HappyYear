"""Study Duel API -- FastAPI + MongoDB.

Two players, three languages, one deterministic daily set each. Deployed on
Render; the static frontend on GitHub Pages talks to it over CORS.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import col_cards, ensure_indexes, ping
from .routers import auth, challenge, content, progress, review, session
from .seed.load import seed_all


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ensure_indexes()
    # First boot on a fresh database seeds itself, so a new Render deploy is
    # playable without shelling in. Later editors to data.py: re-run the loader.
    if await col_cards().count_documents({}) == 0:
        stats = await seed_all()
        print("auto-seeded:", stats)
    yield


app = FastAPI(
    title="Study Duel API",
    version="1.0.0",
    description="A two-player, three-language daily recall duel.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings().origins,
    allow_credentials=False,  # Bearer tokens, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, challenge, session, review, progress, content):
    app.include_router(r.router)


@app.get("/")
async def root() -> dict:
    return {"service": "study-duel", "docs": "/docs", "health": "/api/health"}


@app.get("/api/health")
async def health() -> dict:
    try:
        await ping()
        ok = True
    except Exception:  # noqa: BLE001 - health must never raise
        ok = False
    return {
        "ok": ok,
        "cards": await col_cards().count_documents({}) if ok else 0,
        "day_tz": settings().day_tz,
        "players": list(settings().users_map.keys()),
    }
