from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

FIXTURE_TIMESTAMP = datetime(2026, 3, 17, 12, 0, 0, tzinfo=timezone.utc)
DEMO_HOUSEHOLD_ID = UUID("44444444-4444-4444-4444-444444444444")


@dataclass(frozen=True)
class HouseholdFixture:
    household_name: str
    featured_package_id: UUID


@dataclass(frozen=True)
class StoryPackagePageFixture:
    text: str
    tts_timing: tuple[int, ...]
    page_image_object_key: str
    page_audio_object_key: str
    vocabulary: tuple[str, ...]
    caregiver_prompt_ids: tuple[str, ...]


@dataclass(frozen=True)
class StoryPackageFixture:
    story_master_id: UUID
    story_variant_id: UUID
    title: str
    subtitle: str
    language_mode: str
    difficulty_level: str
    age_band: str
    estimated_duration_sec: int
    cover_image_object_key: str
    tags: tuple[str, ...]
    pages: tuple[StoryPackagePageFixture, ...]


@dataclass(frozen=True)
class ChildFixture:
    child_id: UUID
    name: str
    age_label: str
    focus: str
    weekly_goal: str
    current_package_id: UUID


@dataclass(frozen=True)
class WeeklyPlanFixture:
    day: str
    mode: str
    package_id: UUID
    objective: str


@dataclass(frozen=True)
class ReadingEventFixture:
    event_id: UUID
    event_type: str
    occurred_at: datetime
    session_id: UUID
    child_id: UUID
    package_id: UUID
    payload: dict[str, object]
    page_index: int | None = None


@dataclass(frozen=True)
class PackageAccessFixture:
    package_id: UUID
    access_state: str
    entitlement_source: str
    reason: str


@dataclass(frozen=True)
class HouseholdEntitlementFixture:
    subscription_status: str
    access_state: str
    plan_name: str
    billing_interval: str
    trial_ends_at: datetime | None
    renews_at: datetime | None
    package_access: tuple[PackageAccessFixture, ...]


HOUSEHOLD_FIXTURES: dict[UUID, HouseholdFixture] = {
    DEMO_HOUSEHOLD_ID: HouseholdFixture(
        household_name="The Rivera household",
        featured_package_id=UUID("33333333-3333-3333-3333-333333333333"),
    ),
}

PACKAGE_FIXTURES: dict[UUID, StoryPackageFixture] = {
    UUID("33333333-3333-3333-3333-333333333333"): StoryPackageFixture(
        story_master_id=UUID("11111111-1111-1111-1111-111111111111"),
        story_variant_id=UUID("22222222-2222-2222-2222-222222222222"),
        title="The Lantern Trail",
        subtitle="A co-reading story about checking in, waiting, and returning together.",
        language_mode="zh-CN",
        difficulty_level="L2",
        age_band="4-6",
        estimated_duration_sec=480,
        cover_image_object_key="story-packages/demo/lantern/cover.png",
        tags=("friendship", "shared-reading", "comfort"),
        pages=(
            StoryPackagePageFixture(
                text="Mina lifted a lantern and waited while the path outside turned soft and quiet.",
                tts_timing=(0, 320, 840),
                page_image_object_key="story-packages/demo/lantern/pages/0/image.png",
                page_audio_object_key="story-packages/demo/lantern/pages/0/audio.mp3",
                vocabulary=("lantern", "quiet", "path"),
                caregiver_prompt_ids=("prompt-lantern-1",),
            ),
            StoryPackagePageFixture(
                text="At the bridge, she whispered that waiting together can feel warm instead of lonely.",
                tts_timing=(0, 360, 810),
                page_image_object_key="story-packages/demo/lantern/pages/1/image.png",
                page_audio_object_key="story-packages/demo/lantern/pages/1/audio.mp3",
                vocabulary=("bridge", "waiting", "warm"),
                caregiver_prompt_ids=("prompt-lantern-2",),
            ),
            StoryPackagePageFixture(
                text="When the last light blinked home, Mina smiled because every promise had found its way back.",
                tts_timing=(0, 350, 920),
                page_image_object_key="story-packages/demo/lantern/pages/2/image.png",
                page_audio_object_key="story-packages/demo/lantern/pages/2/audio.mp3",
                vocabulary=("light", "promise", "return"),
                caregiver_prompt_ids=("prompt-lantern-3",),
            ),
        ),
    ),
    UUID("66666666-6666-6666-6666-666666666666"): StoryPackageFixture(
        story_master_id=UUID("77777777-7777-7777-7777-777777777777"),
        story_variant_id=UUID("88888888-8888-8888-8888-888888888888"),
        title="Moon Garden Breathing",
        subtitle="A calming package designed for predictable pacing and low stimulation.",
        language_mode="en-US",
        difficulty_level="L1",
        age_band="4-6",
        estimated_duration_sec=360,
        cover_image_object_key="story-packages/demo/moon-garden/cover.png",
        tags=("calm", "predictable", "wind-down"),
        pages=(
            StoryPackagePageFixture(
                text="In the moon garden, Leo counted three silver leaves before he took his first slow breath.",
                tts_timing=(0, 300, 760),
                page_image_object_key="story-packages/demo/moon-garden/pages/0/image.png",
                page_audio_object_key="story-packages/demo/moon-garden/pages/0/audio.mp3",
                vocabulary=("moon", "garden", "breath"),
                caregiver_prompt_ids=("prompt-moon-1",),
            ),
            StoryPackagePageFixture(
                text="The fountain glowed once, then twice, and Leo let his shoulders grow quiet with the light.",
                tts_timing=(0, 280, 720),
                page_image_object_key="story-packages/demo/moon-garden/pages/1/image.png",
                page_audio_object_key="story-packages/demo/moon-garden/pages/1/audio.mp3",
                vocabulary=("fountain", "glow", "quiet"),
                caregiver_prompt_ids=("prompt-moon-2",),
            ),
            StoryPackagePageFixture(
                text="By the time the stars blinked goodnight, Leo knew exactly how to find the calm path home.",
                tts_timing=(0, 330, 780),
                page_image_object_key="story-packages/demo/moon-garden/pages/2/image.png",
                page_audio_object_key="story-packages/demo/moon-garden/pages/2/audio.mp3",
                vocabulary=("stars", "goodnight", "calm"),
                caregiver_prompt_ids=("prompt-moon-3",),
            ),
        ),
    ),
    UUID("99999999-9999-9999-9999-999999999999"): StoryPackageFixture(
        story_master_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        story_variant_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        title="Bridge Words",
        subtitle="A bilingual-assist package with stable English narration and optional translation reveals.",
        language_mode="en-US",
        difficulty_level="L3",
        age_band="6-8",
        estimated_duration_sec=540,
        cover_image_object_key="story-packages/demo/bridge-words/cover.png",
        tags=("bilingual-assist", "vocabulary", "bridge"),
        pages=(
            StoryPackagePageFixture(
                text="A bridge can hold two ideas at once, just like one story can carry two languages.",
                tts_timing=(0, 300, 700),
                page_image_object_key="story-packages/demo/bridge-words/pages/0/image.png",
                page_audio_object_key="story-packages/demo/bridge-words/pages/0/audio.mp3",
                vocabulary=("bridge", "languages", "story"),
                caregiver_prompt_ids=("prompt-bridge-1",),
            ),
            StoryPackagePageFixture(
                text="When Mei heard an echo under the stones, she paused and asked what the new word might mean.",
                tts_timing=(0, 360, 830),
                page_image_object_key="story-packages/demo/bridge-words/pages/1/image.png",
                page_audio_object_key="story-packages/demo/bridge-words/pages/1/audio.mp3",
                vocabulary=("echo", "stones", "mean"),
                caregiver_prompt_ids=("prompt-bridge-2",),
            ),
            StoryPackagePageFixture(
                text="One bright spark of translation was enough, because the main narration still stayed clear.",
                tts_timing=(0, 280, 760),
                page_image_object_key="story-packages/demo/bridge-words/pages/2/image.png",
                page_audio_object_key="story-packages/demo/bridge-words/pages/2/audio.mp3",
                vocabulary=("spark", "translation", "clear"),
                caregiver_prompt_ids=("prompt-bridge-3",),
            ),
        ),
    ),
}

DEFAULT_STORY_PACKAGE_FIXTURE = StoryPackageFixture(
    story_master_id=UUID("11111111-1111-1111-1111-111111111111"),
    story_variant_id=UUID("22222222-2222-2222-2222-222222222222"),
    title="The Default Lantern Story",
    subtitle="Fallback V2 content package skeleton",
    language_mode="zh-CN",
    difficulty_level="L2",
    age_band="4-6",
    estimated_duration_sec=420,
    cover_image_object_key="story-packages/demo/default/cover.png",
    tags=("friendship", "shared-reading"),
    pages=(
        StoryPackagePageFixture(
            text="A small lantern waited at the front door for the next quiet story to begin.",
            tts_timing=(0, 320, 700),
            page_image_object_key="story-packages/demo/default/pages/0/image.png",
            page_audio_object_key="story-packages/demo/default/pages/0/audio.mp3",
            vocabulary=("lantern", "quiet"),
            caregiver_prompt_ids=("prompt-default-1",),
        ),
        StoryPackagePageFixture(
            text="The story followed a friendly path that always came back home.",
            tts_timing=(0, 290, 640),
            page_image_object_key="story-packages/demo/default/pages/1/image.png",
            page_audio_object_key="story-packages/demo/default/pages/1/audio.mp3",
            vocabulary=("friendly", "path"),
            caregiver_prompt_ids=("prompt-default-2",),
        ),
    ),
)

HOUSEHOLD_PACKAGE_QUEUE_IDS: dict[UUID, tuple[UUID, ...]] = {
    DEMO_HOUSEHOLD_ID: tuple(PACKAGE_FIXTURES.keys()),
}

HOUSEHOLD_CHILD_FIXTURES: dict[UUID, tuple[ChildFixture, ...]] = {
    DEMO_HOUSEHOLD_ID: (
        ChildFixture(
            child_id=UUID("55555555-5555-5555-5555-555555555555"),
            name="Mina",
            age_label="Age 5",
            focus="Shared reading and early vocabulary",
            weekly_goal="4 completed sessions",
            current_package_id=UUID("33333333-3333-3333-3333-333333333333"),
        ),
        ChildFixture(
            child_id=UUID("12121212-1212-1212-1212-121212121212"),
            name="Leo",
            age_label="Age 7",
            focus="Bilingual assist with predictable pacing",
            weekly_goal="3 sessions plus 2 calm replays",
            current_package_id=UUID("66666666-6666-6666-6666-666666666666"),
        ),
    ),
}

HOUSEHOLD_WEEKLY_PLAN_FIXTURES: dict[UUID, tuple[WeeklyPlanFixture, ...]] = {
    DEMO_HOUSEHOLD_ID: (
        WeeklyPlanFixture(
            day="Monday",
            mode="Co-reading",
            package_id=UUID("33333333-3333-3333-3333-333333333333"),
            objective="Warm start for the week with one caregiver prompt per page.",
        ),
        WeeklyPlanFixture(
            day="Wednesday",
            mode="Wind-down",
            package_id=UUID("66666666-6666-6666-6666-666666666666"),
            objective="Use read-to-me mode with low stimulation and a slower page cadence.",
        ),
        WeeklyPlanFixture(
            day="Saturday",
            mode="Replay and retell",
            package_id=UUID("66666666-6666-6666-6666-666666666666"),
            objective="Reread a familiar calm package and let the child retell one page from memory.",
        ),
    ),
}

HOUSEHOLD_READING_EVENT_FIXTURES: dict[UUID, tuple[ReadingEventFixture, ...]] = {
    DEMO_HOUSEHOLD_ID: (
        ReadingEventFixture(
            event_id=UUID("c1d3a8c0-05f3-45bd-9a56-72a911200001"),
            event_type="session_completed",
            occurred_at=datetime(2026, 3, 16, 19, 42, 0, tzinfo=timezone.utc),
            session_id=UUID("d1d3a8c0-05f3-45bd-9a56-72a911200001"),
            child_id=UUID("55555555-5555-5555-5555-555555555555"),
            package_id=UUID("33333333-3333-3333-3333-333333333333"),
            payload={"dwell_ms": 402000},
        ),
        ReadingEventFixture(
            event_id=UUID("c1d3a8c0-05f3-45bd-9a56-72a911200002"),
            event_type="word_revealed_translation",
            occurred_at=datetime(2026, 3, 16, 19, 21, 0, tzinfo=timezone.utc),
            session_id=UUID("d1d3a8c0-05f3-45bd-9a56-72a911200002"),
            child_id=UUID("55555555-5555-5555-5555-555555555555"),
            package_id=UUID("99999999-9999-9999-9999-999999999999"),
            payload={"word": "bridge", "reveal_count": 1},
            page_index=0,
        ),
        ReadingEventFixture(
            event_id=UUID("c1d3a8c0-05f3-45bd-9a56-72a911200003"),
            event_type="page_replayed_audio",
            occurred_at=datetime(2026, 3, 15, 11, 12, 0, tzinfo=timezone.utc),
            session_id=UUID("d1d3a8c0-05f3-45bd-9a56-72a911200003"),
            child_id=UUID("12121212-1212-1212-1212-121212121212"),
            package_id=UUID("66666666-6666-6666-6666-666666666666"),
            payload={"replay_count": 2},
            page_index=0,
        ),
        ReadingEventFixture(
            event_id=UUID("c1d3a8c0-05f3-45bd-9a56-72a911200004"),
            event_type="assist_mode_enabled",
            occurred_at=datetime(2026, 3, 14, 20, 8, 0, tzinfo=timezone.utc),
            session_id=UUID("d1d3a8c0-05f3-45bd-9a56-72a911200004"),
            child_id=UUID("12121212-1212-1212-1212-121212121212"),
            package_id=UUID("66666666-6666-6666-6666-666666666666"),
            payload={"assist_mode": "focus_support"},
        ),
    ),
}

CHILD_SUPPORT_MODE_DEFAULTS: dict[UUID, tuple[str, ...]] = {
    UUID("55555555-5555-5555-5555-555555555555"): (
        "read_aloud_sync",
        "focus_support",
    ),
    UUID("12121212-1212-1212-1212-121212121212"): (
        "read_aloud_sync",
        "focus_support",
        "translation_support",
    ),
}

HOUSEHOLD_ENTITLEMENT_FIXTURES: dict[UUID, HouseholdEntitlementFixture] = {
    DEMO_HOUSEHOLD_ID: HouseholdEntitlementFixture(
        subscription_status="trial_active",
        access_state="trial",
        plan_name="Founding household trial",
        billing_interval="none",
        trial_ends_at=datetime(2026, 4, 17, 12, 0, 0, tzinfo=timezone.utc),
        renews_at=None,
        package_access=(
            PackageAccessFixture(
                package_id=UUID("33333333-3333-3333-3333-333333333333"),
                access_state="entitled",
                entitlement_source="editorial_free",
                reason="Included in the starter household shelf.",
            ),
            PackageAccessFixture(
                package_id=UUID("66666666-6666-6666-6666-666666666666"),
                access_state="entitled",
                entitlement_source="trial",
                reason="Unlocked during the active household trial.",
            ),
            PackageAccessFixture(
                package_id=UUID("99999999-9999-9999-9999-999999999999"),
                access_state="locked",
                entitlement_source="subscription",
                reason="Requires the paid bilingual support plan.",
            ),
        ),
    ),
}
