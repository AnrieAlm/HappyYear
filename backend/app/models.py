"""Request / response schemas."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Lang = Literal["HTML", "CSS", "JS"]


class LoginIn(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    passcode: str = Field(min_length=1, max_length=200)


class LoginOut(BaseModel):
    token: str
    name: str


class CardOut(BaseModel):
    """A card as the player sees it. Never carries the answer."""

    id: str
    lang: Lang
    tier: int
    prompt: str
    hint: str | None = None
    code: bool = False
    story_id: str | None = None
    beat: int | None = None


class ChallengeOut(BaseModel):
    date_key: str
    lang: Lang
    tier: int
    cards: list[CardOut]
    submitted: bool = False
    score: int | None = None


class AnswerIn(BaseModel):
    card_id: str
    answer: str = ""
    attempts: int = 1
    hint_used: bool = False
    ms: int = 0


class CheckIn(BaseModel):
    """Grading one card as the player goes, so they get immediate feedback.
    The server owns the attempt counter -- see routers/session.py."""

    lang: Lang
    card_id: str
    answer: str = ""
    ms: int = 0
    hint_used: bool = False


class HintIn(BaseModel):
    lang: Lang
    card_id: str


class SubmitIn(BaseModel):
    lang: Lang


class CardResult(BaseModel):
    card_id: str
    correct: bool
    canonical: str
    points: int
    story_id: str | None = None
    beat: int | None = None


class CheckOut(CardResult):
    attempts: int


class SubmitOut(BaseModel):
    lang: Lang
    date_key: str
    score: int
    correct: int
    total: int
    time_ms: int
    results: list[CardResult]


class ReviewIn(BaseModel):
    lang: Lang
    answers: list[AnswerIn]


class ReviewOut(BaseModel):
    lang: Lang
    graded: list[CardResult]
    due_next: int


class LangResult(BaseModel):
    lang: Lang
    settled: bool
    winner: str | None = None
    tie: bool = False
    scores: dict[str, int] = {}
    submitted: dict[str, bool] = {}


class TodayResultOut(BaseModel):
    date_key: str
    both_submitted: bool
    langs: list[LangResult]


class StoryBeat(BaseModel):
    story_id: str
    title: str
    concept: str
    language: Lang
    scene: str
    image_url: str
    image_alt: str
    body: list[str]
    unpacking: str


class StoryOut(BaseModel):
    story_id: str
    n: int
    title: str
    concept: str
    language: Lang
    scene: str
    image_url: str
    image_alt: str
    body: list[str]
    unpacking: str


class CastMember(BaseModel):
    name: str
    role: str


class StorybookOut(BaseModel):
    stories: list[StoryOut]
    cast: list[CastMember]


class LangProgress(BaseModel):
    lang: Lang
    tier: int
    total_cards: int
    seen: int
    due: int
    wins: int
    accuracy: float


class ProgressOut(BaseModel):
    name: str
    partner: str
    exam_date: str | None
    streak: int
    days_to_exam: int | None
    langs: list[LangProgress]


class ChronicleEntry(BaseModel):
    date_key: str
    lang: Lang
    text: str
    winner: str | None = None
