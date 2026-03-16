from datetime import datetime, timezone
from uuid import UUID

from app.schemas.v2.caregiver import (
    CaregiverChildSummaryV1,
    CaregiverDashboardV1,
    CaregiverProgressMetricsV1,
    CaregiverWeeklyPlanItemV1,
)
from app.schemas.v2.reading import ReadingEventV1
from app.schemas.v2.story_package import (
    StoryPackageManifestV1,
    StoryPackageMediaV1,
    StoryPackageOverlayV1,
    StoryPackagePageV1,
    StoryPackageSafetyV1,
    StoryPackageTextRunV1,
)

FIXTURE_TIMESTAMP = datetime(2026, 3, 17, 12, 0, 0, tzinfo=timezone.utc)
DEMO_HOUSEHOLD_ID = UUID("44444444-4444-4444-4444-444444444444")

PACKAGE_FIXTURES: dict[UUID, dict[str, object]] = {
    UUID("33333333-3333-3333-3333-333333333333"): {
        "story_master_id": UUID("11111111-1111-1111-1111-111111111111"),
        "story_variant_id": UUID("22222222-2222-2222-2222-222222222222"),
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
        "story_master_id": UUID("77777777-7777-7777-7777-777777777777"),
        "story_variant_id": UUID("88888888-8888-8888-8888-888888888888"),
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
        "story_master_id": UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "story_variant_id": UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
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

DEFAULT_STORY_FIXTURE: dict[str, object] = {
    "story_master_id": UUID("11111111-1111-1111-1111-111111111111"),
    "story_variant_id": UUID("22222222-2222-2222-2222-222222222222"),
    "title": "小兔子的冒险",
    "subtitle": "V2 content package skeleton",
    "language_mode": "zh-CN",
    "difficulty_level": "L2",
    "age_band": "4-6",
    "estimated_duration_sec": 480,
    "cover_image_url": "https://cdn.lumosreading.local/story-packages/demo/cover.png",
    "tags": ["friendship", "shared-reading", "bilingual-assist"],
    "text": "从前有一只小兔子，它喜欢和朋友一起探险。",
    "tts_timing": [0, 450, 980],
    "image_url": "https://cdn.lumosreading.local/story-packages/demo/page-0.png",
    "audio_url": "https://cdn.lumosreading.local/story-packages/demo/page-0.mp3",
    "vocabulary": ["探险", "朋友"],
    "caregiver_prompt_ids": ["prompt-friendship-1"],
}


def _build_story_package(package_id: UUID, fixture: dict[str, object]) -> StoryPackageManifestV1:
    return StoryPackageManifestV1(
        package_id=package_id,
        story_master_id=fixture["story_master_id"],
        story_variant_id=fixture["story_variant_id"],
        title=str(fixture["title"]),
        subtitle=str(fixture["subtitle"]),
        language_mode=str(fixture["language_mode"]),
        difficulty_level=str(fixture["difficulty_level"]),
        age_band=str(fixture["age_band"]),
        estimated_duration_sec=int(fixture["estimated_duration_sec"]),
        release_channel="pilot",
        cover_image_url=str(fixture["cover_image_url"]),
        tags=[str(value) for value in fixture["tags"]],
        safety=StoryPackageSafetyV1(
            review_status="approved",
            reviewed_at=FIXTURE_TIMESTAMP,
            review_policy_version="2026.03",
        ),
        pages=[
            StoryPackagePageV1(
                page_index=0,
                text_runs=[
                    StoryPackageTextRunV1(
                        text=str(fixture["text"]),
                        lang=str(fixture["language_mode"]),
                        tts_timing=[int(value) for value in fixture["tts_timing"]],
                    )
                ],
                media=StoryPackageMediaV1(
                    image_url=str(fixture["image_url"]),
                    audio_url=str(fixture["audio_url"]),
                ),
                overlays=StoryPackageOverlayV1(
                    vocabulary=[str(value) for value in fixture["vocabulary"]],
                    caregiver_prompt_ids=[str(value) for value in fixture["caregiver_prompt_ids"]],
                ),
            )
        ],
    )


def get_story_package_fixture(package_id: UUID) -> StoryPackageManifestV1:
    fixture = PACKAGE_FIXTURES.get(package_id, DEFAULT_STORY_FIXTURE)
    return _build_story_package(package_id, fixture)


def get_story_package_queue() -> list[StoryPackageManifestV1]:
    return [get_story_package_fixture(package_id) for package_id in PACKAGE_FIXTURES]


def _build_reading_event(
    *,
    event_id: str,
    event_type: str,
    occurred_at: datetime,
    session_id: str,
    child_id: str,
    package_id: str,
    payload: dict[str, object],
    page_index: int | None = None,
) -> ReadingEventV1:
    return ReadingEventV1(
        event_id=UUID(event_id),
        event_type=event_type,
        occurred_at=occurred_at,
        session_id=UUID(session_id),
        child_id=UUID(child_id),
        package_id=UUID(package_id),
        page_index=page_index,
        platform="ipadOS",
        surface="child-app",
        app_version="2.0.0",
        language_mode="zh-CN",
        payload=payload,
    )


def get_recent_reading_events() -> list[ReadingEventV1]:
    return [
        _build_reading_event(
            event_id="c1d3a8c0-05f3-45bd-9a56-72a911200001",
            event_type="session_completed",
            occurred_at=datetime(2026, 3, 16, 19, 42, 0, tzinfo=timezone.utc),
            session_id="d1d3a8c0-05f3-45bd-9a56-72a911200001",
            child_id="55555555-5555-5555-5555-555555555555",
            package_id="33333333-3333-3333-3333-333333333333",
            payload={"dwell_ms": 402000},
        ),
        _build_reading_event(
            event_id="c1d3a8c0-05f3-45bd-9a56-72a911200002",
            event_type="word_revealed_translation",
            occurred_at=datetime(2026, 3, 16, 19, 21, 0, tzinfo=timezone.utc),
            session_id="d1d3a8c0-05f3-45bd-9a56-72a911200002",
            child_id="55555555-5555-5555-5555-555555555555",
            package_id="99999999-9999-9999-9999-999999999999",
            payload={"word": "bridge", "reveal_count": 1},
            page_index=0,
        ),
        _build_reading_event(
            event_id="c1d3a8c0-05f3-45bd-9a56-72a911200003",
            event_type="page_replayed_audio",
            occurred_at=datetime(2026, 3, 15, 11, 12, 0, tzinfo=timezone.utc),
            session_id="d1d3a8c0-05f3-45bd-9a56-72a911200003",
            child_id="12121212-1212-1212-1212-121212121212",
            package_id="66666666-6666-6666-6666-666666666666",
            payload={"replay_count": 2},
            page_index=0,
        ),
        _build_reading_event(
            event_id="c1d3a8c0-05f3-45bd-9a56-72a911200004",
            event_type="assist_mode_enabled",
            occurred_at=datetime(2026, 3, 14, 20, 8, 0, tzinfo=timezone.utc),
            session_id="d1d3a8c0-05f3-45bd-9a56-72a911200004",
            child_id="12121212-1212-1212-1212-121212121212",
            package_id="66666666-6666-6666-6666-666666666666",
            payload={"assist_mode": "focus_support"},
        ),
    ]


def _build_progress_metrics(events: list[ReadingEventV1]) -> CaregiverProgressMetricsV1:
    return CaregiverProgressMetricsV1(
        completed_sessions=sum(1 for event in events if event.event_type == "session_completed"),
        translation_reveals=sum(1 for event in events if event.event_type == "word_revealed_translation"),
        audio_replays=sum(1 for event in events if event.event_type == "page_replayed_audio"),
    )


def get_caregiver_dashboard_fixture(household_id: UUID) -> CaregiverDashboardV1:
    package_queue = get_story_package_queue()
    recent_events = get_recent_reading_events()

    return CaregiverDashboardV1(
        household_id=household_id,
        household_name="The Rivera household" if household_id == DEMO_HOUSEHOLD_ID else "Demo household",
        featured_package_id=UUID("33333333-3333-3333-3333-333333333333"),
        package_queue=package_queue,
        recent_events=recent_events,
        children=[
            CaregiverChildSummaryV1(
                child_id=UUID("55555555-5555-5555-5555-555555555555"),
                name="Mina",
                age_label="Age 5",
                focus="Shared reading and early vocabulary",
                weekly_goal="4 completed sessions",
                current_package_id=UUID("33333333-3333-3333-3333-333333333333"),
            ),
            CaregiverChildSummaryV1(
                child_id=UUID("12121212-1212-1212-1212-121212121212"),
                name="Leo",
                age_label="Age 7",
                focus="Bilingual assist with predictable pacing",
                weekly_goal="3 sessions plus 2 calm replays",
                current_package_id=UUID("99999999-9999-9999-9999-999999999999"),
            ),
        ],
        weekly_plan=[
            CaregiverWeeklyPlanItemV1(
                day="Monday",
                mode="Co-reading",
                package_id=UUID("33333333-3333-3333-3333-333333333333"),
                objective="Warm start for the week with one caregiver prompt per page.",
            ),
            CaregiverWeeklyPlanItemV1(
                day="Wednesday",
                mode="Wind-down",
                package_id=UUID("66666666-6666-6666-6666-666666666666"),
                objective="Use read-to-me mode with low stimulation and a slower page cadence.",
            ),
            CaregiverWeeklyPlanItemV1(
                day="Saturday",
                mode="Bilingual assist",
                package_id=UUID("99999999-9999-9999-9999-999999999999"),
                objective="Reveal only three translation words and track the replay count.",
            ),
        ],
        progress_metrics=_build_progress_metrics(recent_events),
        generated_at=FIXTURE_TIMESTAMP,
    )
