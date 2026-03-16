from uuid import UUID

from fastapi import APIRouter

from app.schemas.v2.story_package import StoryPackageManifestV1
from app.services.v2.story_package_service import DemoStoryPackageService

router = APIRouter()
story_package_service = DemoStoryPackageService()


@router.get("/{package_id}", response_model=StoryPackageManifestV1)
async def get_story_package(package_id: UUID) -> StoryPackageManifestV1:
    """Return the V2 runtime content package skeleton for a story."""
    return story_package_service.get_story_package(package_id)
