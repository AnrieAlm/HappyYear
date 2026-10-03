from fastapi import APIRouter

from ..db import col_stories
from ..models import CastMember, StoryOut, StorybookOut
from ..seed import data as seed_data

router = APIRouter(prefix="/api", tags=["content"])


@router.get("/storybook", response_model=StorybookOut)
async def storybook() -> StorybookOut:
    """Public: the storybook is readable without signing in, which is the whole
    point of it being a study aid rather than a game screen."""
    rows = [d async for d in col_stories().find({}).sort("n", 1)]
    if not rows:
        rows = seed_data.STORIES
    stories = [
        StoryOut(
            story_id=s.get("story_id", ""),
            n=int(s.get("n", 0)),
            title=s.get("title", ""),
            concept=s.get("concept", ""),
            language=s.get("language", "HTML"),
            scene=s.get("scene", ""),
            image_url=s.get("image_url", ""),
            image_alt=s.get("image_alt", ""),
            body=list(s.get("body") or []),
            unpacking=s.get("unpacking", ""),
        )
        for s in rows
    ]
    return StorybookOut(
        stories=stories,
        cast=[CastMember(**m) for m in seed_data.CAST],
    )
