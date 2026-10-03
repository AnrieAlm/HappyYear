"""Answer normalisation, grading and the daily score.

Grading happens HERE, never in the browser: the answer key is never sent to the
client, so a network tab cannot spoil tomorrow's cards.
"""
from __future__ import annotations

import re
import unicodedata

from .models import AnswerIn, CardResult

# points for how the answer was reached
PTS_FIRST_TRY = 100
PTS_AFTER_RETRY = 60
PTS_HINT = 30
PTS_WRONG = 0

_WS = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Case-insensitive, whitespace-collapsed, quote/dash-normalised compare.
    Deliberately conservative: it forgives formatting, not wrong answers."""
    s = unicodedata.normalize("NFKC", text or "")
    s = (
        s.replace("\u2018", "'").replace("\u2019", "'")
        .replace("\u201c", '"').replace("\u201d", '"')
        .replace("\u2013", "-").replace("\u2014", "-")
    )
    s = _WS.sub(" ", s).strip().lower()
    # a trailing semicolon is a style choice, not a wrong answer
    return s.rstrip(";")


def points_for(correct: bool, attempts: int, hint_used: bool) -> int:
    """The whole scoring rule, in one place, so the live per-card check and the
    final session score can never drift apart."""
    if not correct:
        return PTS_WRONG
    if hint_used:
        return PTS_HINT
    if attempts > 1:
        return PTS_AFTER_RETRY
    return PTS_FIRST_TRY


def grade_answer(card: dict, given: AnswerIn) -> CardResult:
    accepted = [card["answer"], *(card.get("accept") or [])]
    wanted = [normalize(a) for a in accepted]
    got = normalize(given.answer)
    correct = bool(got) and got in wanted

    return CardResult(
        card_id=card["id"],
        correct=correct,
        canonical=card["answer"],
        points=points_for(correct, given.attempts, given.hint_used),
        story_id=card.get("story_id"),
        beat=card.get("beat"),
    )


def score_run(results: list[CardResult]) -> int:
    return sum(r.points for r in results)


def accuracy(results: list[CardResult]) -> float:
    if not results:
        return 0.0
    return round(sum(1 for r in results if r.correct) / len(results), 4)
