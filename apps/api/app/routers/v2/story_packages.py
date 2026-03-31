from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.v2.story_package import StoryPackageManifestV1
from app.schemas.v2.story_package_release import (
    StoryPackageBuildCommandV1,
    StoryPackageBuildV1,
    StoryPackageDraftIndexV1,
    StoryPackageDraftV1,
    StoryPackageHistoryV1,
    StoryPackageRecallCommandV1,
    StoryPackageReviewCommandV1,
    StoryPackageReleaseCommandV1,
    StoryPackageReleaseV1,
    StoryPackageRollbackCommandV1,
)
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.story_package_release_service import (
    StoryPackageReleaseNotFoundError,
    StoryPackageReleaseValidationError,
    create_release_story_package_services,
)

router = APIRouter()
story_package_service, release_service = create_release_story_package_services(
    clock=lambda: FIXTURE_TIMESTAMP,
)


@router.get(
    "",
    response_model=StoryPackageDraftIndexV1,
    response_model_exclude_none=True,
)
async def list_story_package_drafts() -> StoryPackageDraftIndexV1:
    """Return the package draft list for studio and release surfaces."""
    return release_service.list_drafts()


@router.post(
    "/{package_id}:build",
    response_model=StoryPackageBuildV1,
    response_model_exclude_none=True,
)
async def build_story_package(
    package_id: UUID,
    command: StoryPackageBuildCommandV1,
) -> StoryPackageBuildV1:
    """Create a versioned build record for the requested package."""
    try:
        return release_service.build_package(package_id, command)
    except StoryPackageReleaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StoryPackageReleaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{package_id}:release",
    response_model=StoryPackageReleaseV1,
    response_model_exclude_none=True,
)
async def release_story_package(
    package_id: UUID,
    command: StoryPackageReleaseCommandV1,
) -> StoryPackageReleaseV1:
    """Promote a build into the active runtime lookup path."""
    try:
        return release_service.release_package(package_id, command)
    except StoryPackageReleaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StoryPackageReleaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{package_id}:recall",
    response_model=StoryPackageReleaseV1,
    response_model_exclude_none=True,
)
async def recall_story_package_release(
    package_id: UUID,
    command: StoryPackageRecallCommandV1,
) -> StoryPackageReleaseV1:
    """Recall the active release while preserving lookup fallback semantics."""
    try:
        return release_service.recall_release(package_id, command)
    except StoryPackageReleaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StoryPackageReleaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{package_id}:rollback",
    response_model=StoryPackageReleaseV1,
    response_model_exclude_none=True,
)
async def rollback_story_package_release(
    package_id: UUID,
    command: StoryPackageRollbackCommandV1,
) -> StoryPackageReleaseV1:
    """Promote a historical release back into the active runtime path."""
    try:
        return release_service.rollback_release(package_id, command)
    except StoryPackageReleaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StoryPackageReleaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{package_id}:review",
    response_model=StoryPackageDraftV1,
    response_model_exclude_none=True,
)
async def review_story_package(
    package_id: UUID,
    command: StoryPackageReviewCommandV1,
) -> StoryPackageDraftV1:
    """Record review state changes for editorial and AI-generated drafts."""
    try:
        return release_service.review_package(package_id, command)
    except StoryPackageReleaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StoryPackageReleaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{package_id}/history",
    response_model=StoryPackageHistoryV1,
    response_model_exclude_none=True,
)
async def get_story_package_history(package_id: UUID) -> StoryPackageHistoryV1:
    """Return draft, build, and release history for one package."""
    try:
        return release_service.get_history(package_id)
    except StoryPackageReleaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{package_id}",
    response_model=StoryPackageManifestV1,
    response_model_exclude_none=True,
)
async def get_story_package(package_id: UUID) -> StoryPackageManifestV1:
    """Return the V2 runtime content package skeleton for a story."""
    try:
        return story_package_service.get_story_package(package_id)
    except StoryPackageReleaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StoryPackageReleaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
