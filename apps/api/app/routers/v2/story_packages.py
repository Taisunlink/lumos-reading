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


def _build_story_package(
    package_id: UUID,
    *,
    story_master_id: str,
    story_variant_id: str,
    title: str,
    subtitle: str,
    language_mode: str,
    difficulty_level: str,
    age_band: str,
    estimated_duration_sec: int,
    cover_image_url: str,
    tags: list[str],
    text: str,
    tts_timing: list[int],
    image_url: str,
    audio_url: str,
    vocabulary: list[str],
    caregiver_prompt_ids: list[str],
) -> StoryPackageManifestV1:
    return StoryPackageManifestV1(
        package_id=package_id,
        story_master_id=UUID(story_master_id),
        story_variant_id=UUID(story_variant_id),
        title=title,
        subtitle=subtitle,
        language_mode=language_mode,
        difficulty_level=difficulty_level,
        age_band=age_band,
        estimated_duration_sec=estimated_duration_sec,
        release_channel="pilot",
        cover_image_url=cover_image_url,
        tags=tags,
        safety=StoryPackageSafetyV1(
            review_status="approved",
            review_policy_version="2026.03",
        ),
        pages=[
            StoryPackagePageV1(
                page_index=0,
                text_runs=[
                    StoryPackageTextRunV1(
                        text=text,
                        lang=language_mode,
                        tts_timing=tts_timing,
                    )
                ],
                media=StoryPackageMediaV1(
                    image_url=image_url,
                    audio_url=audio_url,
                ),
                overlays=StoryPackageOverlayV1(
                    vocabulary=vocabulary,
                    caregiver_prompt_ids=caregiver_prompt_ids,
                ),
            )
        ],
    )


KNOWN_PACKAGE_FIXTURES: dict[UUID, dict[str, object]] = {
    UUID("33333333-3333-3333-3333-333333333333"): {
        "story_master_id": "11111111-1111-1111-1111-111111111111",
        "story_variant_id": "22222222-2222-2222-2222-222222222222",
        "title": "The Lantern Trail",
        "subtitle": "A co-reading story about checking in, waiting, and returning together.",
        "language_mode": "zh-CN",
        "difficulty_level": "L2",
        "age_band": "4-6",
        "estimated_duration_sec": 480,
        "cover_image_url": "https://cdn.lumosreading.local/story-packages/demo/lantern-cover.png",
        "tags": ["friendship", "shared-reading", "comfort"],
        "text": "灯笼沿着小路摇晃，小伙伴们约好一起出发，也一起回家。",
        "tts_timing": [0, 420, 910],
        "image_url": "https://cdn.lumosreading.local/story-packages/demo/lantern-page-0.png",
        "audio_url": "https://cdn.lumosreading.local/story-packages/demo/lantern-page-0.mp3",
        "vocabulary": ["灯笼", "约定", "回来"],
        "caregiver_prompt_ids": ["prompt-friendship-1", "prompt-friendship-2"],
    },
    UUID("66666666-6666-6666-6666-666666666666"): {
        "story_master_id": "77777777-7777-7777-7777-777777777777",
        "story_variant_id": "88888888-8888-8888-8888-888888888888",
        "title": "Moon Garden Breathing",
        "subtitle": "A calming package designed for predictable pacing and low stimulation.",
        "language_mode": "en-US",
        "difficulty_level": "L1",
        "age_band": "4-6",
        "estimated_duration_sec": 360,
        "cover_image_url": "https://cdn.lumosreading.local/story-packages/demo/moon-cover.png",
        "tags": ["calm", "predictable", "wind-down"],
        "text": "Moonlight settles over the garden, and every breath makes the silver leaves glow a little more.",
        "tts_timing": [0, 390, 870],
        "image_url": "https://cdn.lumosreading.local/story-packages/demo/moon-page-0.png",
        "audio_url": "https://cdn.lumosreading.local/story-packages/demo/moon-page-0.mp3",
        "vocabulary": ["moonlight", "garden", "breathing"],
        "caregiver_prompt_ids": ["prompt-calm-1"],
    },
    UUID("99999999-9999-9999-9999-999999999999"): {
        "story_master_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "story_variant_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "title": "Bridge Words",
        "subtitle": "A bilingual-assist package with stable English narration and optional translation reveals.",
        "language_mode": "en-US",
        "difficulty_level": "L3",
        "age_band": "6-8",
        "estimated_duration_sec": 540,
        "cover_image_url": "https://cdn.lumosreading.local/story-packages/demo/bridge-cover.png",
        "tags": ["bilingual-assist", "vocabulary", "bridge"],
        "text": "At the bridge, Mina hears one story in English and unlocks just a few helper words in Chinese.",
        "tts_timing": [0, 360, 790],
        "image_url": "https://cdn.lumosreading.local/story-packages/demo/bridge-page-0.png",
        "audio_url": "https://cdn.lumosreading.local/story-packages/demo/bridge-page-0.mp3",
        "vocabulary": ["bridge", "echo", "spark"],
        "caregiver_prompt_ids": ["prompt-bridge-1", "prompt-bridge-2"],
    },
}


def _build_default_story_package(package_id: UUID) -> StoryPackageManifestV1:
    return _build_story_package(
        package_id,
        story_master_id="11111111-1111-1111-1111-111111111111",
        story_variant_id="22222222-2222-2222-2222-222222222222",
        title="小兔子的冒险",
        subtitle="V2 content package skeleton",
        language_mode="zh-CN",
        difficulty_level="L2",
        age_band="4-6",
        estimated_duration_sec=480,
        cover_image_url="https://cdn.lumosreading.local/story-packages/demo/cover.png",
        tags=["friendship", "shared-reading", "bilingual-assist"],
        text="从前有一只小兔子，它喜欢和朋友一起探险。",
        tts_timing=[0, 450, 980],
        image_url="https://cdn.lumosreading.local/story-packages/demo/page-0.png",
        audio_url="https://cdn.lumosreading.local/story-packages/demo/page-0.mp3",
        vocabulary=["探险", "朋友"],
        caregiver_prompt_ids=["prompt-friendship-1"],
    )


@router.get("/{package_id}", response_model=StoryPackageManifestV1)
async def get_story_package(package_id: UUID) -> StoryPackageManifestV1:
    """Return the V2 runtime content package skeleton for a story."""
    fixture = KNOWN_PACKAGE_FIXTURES.get(package_id)
    if fixture is None:
        return _build_default_story_package(package_id)

    return _build_story_package(
        package_id,
        story_master_id=str(fixture["story_master_id"]),
        story_variant_id=str(fixture["story_variant_id"]),
        title=str(fixture["title"]),
        subtitle=str(fixture["subtitle"]),
        language_mode=str(fixture["language_mode"]),
        difficulty_level=str(fixture["difficulty_level"]),
        age_band=str(fixture["age_band"]),
        estimated_duration_sec=int(fixture["estimated_duration_sec"]),
        cover_image_url=str(fixture["cover_image_url"]),
        tags=[str(tag) for tag in fixture["tags"]],
        text=str(fixture["text"]),
        tts_timing=[int(value) for value in fixture["tts_timing"]],
        image_url=str(fixture["image_url"]),
        audio_url=str(fixture["audio_url"]),
        vocabulary=[str(value) for value in fixture["vocabulary"]],
        caregiver_prompt_ids=[str(value) for value in fixture["caregiver_prompt_ids"]],
    )
