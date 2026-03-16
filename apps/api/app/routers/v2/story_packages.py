from uuid import UUID

from fastapi import APIRouter

from app.schemas.v2.story_package import (
    StoryPackageManifestV1,
    StoryPackageMediaV1,
    StoryPackageOverlayV1,
    StoryPackagePageV1,
    StoryPackageSafetyV1,
    StoryPackageTextRunV1,
)

router = APIRouter()


def _build_story_package(package_id: UUID) -> StoryPackageManifestV1:
    return StoryPackageManifestV1(
        package_id=package_id,
        story_master_id=UUID("11111111-1111-1111-1111-111111111111"),
        story_variant_id=UUID("22222222-2222-2222-2222-222222222222"),
        title="小兔子的冒险",
        subtitle="V2 content package skeleton",
        language_mode="zh-CN",
        difficulty_level="L2",
        age_band="4-6",
        estimated_duration_sec=480,
        release_channel="pilot",
        cover_image_url="https://cdn.lumosreading.local/story-packages/demo/cover.png",
        tags=["friendship", "shared-reading", "bilingual-assist"],
        safety=StoryPackageSafetyV1(
            review_status="approved",
            review_policy_version="2026.03",
        ),
        pages=[
            StoryPackagePageV1(
                page_index=0,
                text_runs=[
                    StoryPackageTextRunV1(
                        text="从前有一只小兔子，它喜欢和朋友一起探险。",
                        lang="zh-CN",
                        tts_timing=[0, 450, 980],
                    )
                ],
                media=StoryPackageMediaV1(
                    image_url="https://cdn.lumosreading.local/story-packages/demo/page-0.png",
                    audio_url="https://cdn.lumosreading.local/story-packages/demo/page-0.mp3",
                ),
                overlays=StoryPackageOverlayV1(
                    vocabulary=["探险", "朋友"],
                    caregiver_prompt_ids=["prompt-friendship-1"],
                ),
            )
        ],
    )


@router.get("/{package_id}", response_model=StoryPackageManifestV1)
async def get_story_package(package_id: UUID) -> StoryPackageManifestV1:
    """Return the V2 runtime content package skeleton for a story."""
    return _build_story_package(package_id)
