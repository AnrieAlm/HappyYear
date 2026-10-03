"""SM-2 spaced repetition, at day granularity.

Each (player, card) pair carries its own schedule. Day granularity (rather than
Anki's minute-level learning steps) because this runs once a day, not in a
cram session.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

# grade -> label used by both the API and the UI buttons
GRADES = {"again": 0, "hard": 1, "good": 2, "easy": 3}

MIN_EASE = 1.3
MAX_EASE = 3.0
MAX_INTERVAL = 180


def from_correct(correct: bool, attempts: int, hint_used: bool) -> int:
    """Infer a grade from how the answer actually went, so the UI can offer
    honest self-grading without the player having to think in SM-2 terms."""
    if not correct:
        return GRADES["again"]
    if hint_used:
        return GRADES["hard"]
    if attempts > 1:
        return GRADES["hard"]
    return GRADES["good"]


def new_state() -> dict:
    return {"ease": 2.5, "interval": 0, "reps": 0, "lapses": 0, "due": None}


def apply(state: dict | None, grade: int, today: datetime) -> dict:
    """Return the next review state. `today` is a UTC-aware datetime."""
    state = {**new_state(), **(state or {})}
    ease = float(state["ease"])
    interval = int(state["interval"])
    reps = int(state["reps"])
    lapses = int(state["lapses"])

    if grade == GRADES["again"]:
        lapses += 1
        reps = 0
        interval = 0  # stays due: it comes back in the same day's review run
    else:
        if grade == GRADES["hard"]:
            ease = max(MIN_EASE, ease - 0.15)
        elif grade == GRADES["easy"]:
            ease = min(MAX_EASE, ease + 0.15)

        reps += 1
        if reps == 1:
            interval = 2 if grade == GRADES["easy"] else 1
        elif reps == 2:
            interval = 6 if grade == GRADES["easy"] else 3
        else:
            interval = round(max(interval, 1) * ease)
            if grade == GRADES["hard"]:
                interval = max(1, round(interval * 0.6))

    interval = max(0, min(MAX_INTERVAL, interval))
    return {
        "ease": round(ease, 3),
        "interval": interval,
        "reps": reps,
        "lapses": lapses,
        "due": today + timedelta(days=interval),
    }


def is_due(state: dict | None, today: datetime) -> bool:
    if not state or state.get("due") is None:
        return True
    due = state["due"]
    if due.tzinfo is None:
        due = due.replace(tzinfo=timezone.utc)
    return due <= today
