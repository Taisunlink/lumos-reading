from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.v2.story_generation import (
    StoryBriefCommandV1,
    StoryBriefIndexV1,
    StoryBriefV1,
    StoryGenerationJobCommandV1,
    StoryGenerationJobIndexV1,
    StoryGenerationJobV1,
)
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.story_generation_service import (
    StoryGenerationNotFoundError,
    StoryGenerationValidationError,
    create_story_generation_service,
)

router = APIRouter()
jobs_router = APIRouter()
generation_service = create_story_generation_service(clock=lambda: FIXTURE_TIMESTAMP)


@router.get(
    "",
    response_model=StoryBriefIndexV1,
    response_model_exclude_none=True,
)
async def list_story_briefs() -> StoryBriefIndexV1:
    """Return the AI brief backlog for studio operations."""
    return generation_service.list_briefs()


@router.post(
    "",
    response_model=StoryBriefV1,
    response_model_exclude_none=True,
)
async def create_story_brief(command: StoryBriefCommandV1) -> StoryBriefV1:
    """Create a new editorial brief for AI-assisted draft generation."""
    return generation_service.create_brief(command)


@router.post(
    "/{brief_id}:generate-draft",
    response_model=StoryGenerationJobV1,
    response_model_exclude_none=True,
)
async def generate_story_brief_draft(
    brief_id: UUID,
    command: StoryGenerationJobCommandV1,
) -> StoryGenerationJobV1:
    """Generate a reviewable draft package from a brief."""
    try:
        return generation_service.generate_draft(brief_id, command)
    except StoryGenerationValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StoryGenerationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{brief_id}:generate-media",
    response_model=StoryGenerationJobV1,
    response_model_exclude_none=True,
)
async def generate_story_brief_media(
    brief_id: UUID,
    command: StoryGenerationJobCommandV1,
) -> StoryGenerationJobV1:
    """Generate media assets for a previously assembled AI draft."""
    try:
        return generation_service.generate_media(brief_id, command)
    except StoryGenerationValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StoryGenerationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@jobs_router.get(
    "",
    response_model=StoryGenerationJobIndexV1,
    response_model_exclude_none=True,
)
async def list_story_generation_jobs() -> StoryGenerationJobIndexV1:
    """Return generation jobs across draft and media stages."""
    return generation_service.list_jobs()
