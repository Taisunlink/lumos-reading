from uuid import UUID

from fastapi import APIRouter

from app.schemas.v2.story_package import StoryPackageManifestV1
from app.services.v2_demo_data import get_story_package_fixture

router = APIRouter()


@router.get("/{package_id}", response_model=StoryPackageManifestV1)
async def get_story_package(package_id: UUID) -> StoryPackageManifestV1:
    """Return the V2 runtime content package skeleton for a story."""
    return get_story_package_fixture(package_id)
