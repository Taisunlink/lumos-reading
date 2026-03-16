import {
  CAREGIVER_PLAN_SCHEMA_VERSION,
  CAREGIVER_PROGRESS_SCHEMA_VERSION,
  READING_EVENT_SCHEMA_VERSION,
  STORY_PACKAGE_SCHEMA_VERSION,
  type CaregiverPlanV1,
  type CaregiverProgressV1,
  type ReadingEventV1,
  type StoryPackageManifestV1,
} from "@lumosreading/contracts";

export const demoHouseholdId = "44444444-4444-4444-4444-444444444444";

function buildPlaceholderAssetUrl(objectKey: string): string {
  return `https://oss-placeholder.lumosreading.local/${objectKey}`;
}

function buildPackage(args: {
  packageId: string;
  storyMasterId: string;
  storyVariantId: string;
  title: string;
  subtitle: string;
  languageMode: string;
  difficultyLevel: string;
  ageBand: string;
  durationSec: number;
  tags: string[];
  vocabulary: string[];
  imageUrl: string;
  audioUrl: string;
}): StoryPackageManifestV1 {
  return {
    schema_version: STORY_PACKAGE_SCHEMA_VERSION,
    package_id: args.packageId,
    story_master_id: args.storyMasterId,
    story_variant_id: args.storyVariantId,
    title: args.title,
    subtitle: args.subtitle,
    language_mode: args.languageMode,
    difficulty_level: args.difficultyLevel,
    age_band: args.ageBand,
    estimated_duration_sec: args.durationSec,
    release_channel: "pilot",
    cover_image_url: args.imageUrl,
    tags: args.tags,
    safety: {
      review_status: "approved",
      reviewed_at: "2026-03-17T12:00:00Z",
      review_policy_version: "2026.03",
    },
    pages: [
      {
        page_index: 0,
        text_runs: [
          {
            text: args.subtitle,
            lang: args.languageMode,
            tts_timing: [0, 320, 840],
          },
        ],
        media: {
          image_url: args.imageUrl,
          audio_url: args.audioUrl,
        },
        overlays: {
          vocabulary: args.vocabulary,
          caregiver_prompt_ids: ["prompt-1", "prompt-2"],
        },
      },
    ],
  };
}

function buildEvent(args: {
  eventId: string;
  type: ReadingEventV1["event_type"];
  occurredAt: string;
  sessionId: string;
  childId: string;
  packageId: string;
  payload: ReadingEventV1["payload"];
  pageIndex?: number;
}): ReadingEventV1 {
  return {
    schema_version: READING_EVENT_SCHEMA_VERSION,
    event_id: args.eventId,
    event_type: args.type,
    occurred_at: args.occurredAt,
    session_id: args.sessionId,
    child_id: args.childId,
    package_id: args.packageId,
    page_index: args.pageIndex ?? null,
    platform: "ipadOS",
    surface: "child-app",
    app_version: "2.0.0",
    language_mode: "zh-CN",
    payload: args.payload,
  };
}

const packageQueue = [
  buildPackage({
    packageId: "33333333-3333-3333-3333-333333333333",
    storyMasterId: "11111111-1111-1111-1111-111111111111",
    storyVariantId: "22222222-2222-2222-2222-222222222222",
    title: "The Lantern Trail",
    subtitle: "A co-reading story about checking in, waiting, and returning together.",
    languageMode: "zh-CN",
    difficultyLevel: "L2",
    ageBand: "4-6",
    durationSec: 480,
    tags: ["friendship", "shared-reading", "comfort"],
    vocabulary: ["lantern", "promise", "return"],
    imageUrl: buildPlaceholderAssetUrl("story-packages/demo/lantern/cover.png"),
    audioUrl: buildPlaceholderAssetUrl("story-packages/demo/lantern/pages/0/audio.mp3"),
  }),
  buildPackage({
    packageId: "66666666-6666-6666-6666-666666666666",
    storyMasterId: "77777777-7777-7777-7777-777777777777",
    storyVariantId: "88888888-8888-8888-8888-888888888888",
    title: "Moon Garden Breathing",
    subtitle: "A calming package designed for predictable pacing and low stimulation.",
    languageMode: "en-US",
    difficultyLevel: "L1",
    ageBand: "4-6",
    durationSec: 360,
    tags: ["calm", "predictable", "wind-down"],
    vocabulary: ["garden", "breathing", "glow"],
    imageUrl: buildPlaceholderAssetUrl("story-packages/demo/moon-garden/cover.png"),
    audioUrl: buildPlaceholderAssetUrl("story-packages/demo/moon-garden/pages/0/audio.mp3"),
  }),
  buildPackage({
    packageId: "99999999-9999-9999-9999-999999999999",
    storyMasterId: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    storyVariantId: "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    title: "Bridge Words",
    subtitle: "A bilingual-assist package with stable English narration and optional translation reveals.",
    languageMode: "en-US",
    difficultyLevel: "L3",
    ageBand: "6-8",
    durationSec: 540,
    tags: ["bilingual-assist", "vocabulary", "bridge"],
    vocabulary: ["bridge", "echo", "spark"],
    imageUrl: buildPlaceholderAssetUrl("story-packages/demo/bridge-words/cover.png"),
    audioUrl: buildPlaceholderAssetUrl("story-packages/demo/bridge-words/pages/0/audio.mp3"),
  }),
];

export const fallbackCaregiverPlan: CaregiverPlanV1 = {
  schema_version: CAREGIVER_PLAN_SCHEMA_VERSION,
  household_id: demoHouseholdId,
  package_queue: packageQueue,
  weekly_plan: [
    {
      day: "Monday",
      mode: "Co-reading",
      package_id: packageQueue[0].package_id,
      objective: "Warm start for the week with one caregiver prompt per page.",
      package: packageQueue[0],
    },
    {
      day: "Wednesday",
      mode: "Wind-down",
      package_id: packageQueue[1].package_id,
      objective: "Use read-to-me mode with low stimulation and a slower page cadence.",
      package: packageQueue[1],
    },
    {
      day: "Saturday",
      mode: "Bilingual assist",
      package_id: packageQueue[2].package_id,
      objective: "Reveal only three translation words and track the replay count.",
      package: packageQueue[2],
    },
  ],
  generated_at: "2026-03-17T12:00:00Z",
};

export const fallbackCaregiverProgress: CaregiverProgressV1 = {
  schema_version: CAREGIVER_PROGRESS_SCHEMA_VERSION,
  household_id: demoHouseholdId,
  recent_events: [
    {
      event: buildEvent({
        eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200001",
        type: "session_completed",
        occurredAt: "2026-03-16T19:42:00Z",
        sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200001",
        childId: "55555555-5555-5555-5555-555555555555",
        packageId: packageQueue[0].package_id,
        payload: { dwell_ms: 402000 },
      }),
      child_name: "Mina",
      package_title: packageQueue[0].title,
    },
    {
      event: buildEvent({
        eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200002",
        type: "word_revealed_translation",
        occurredAt: "2026-03-16T19:21:00Z",
        sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200002",
        childId: "55555555-5555-5555-5555-555555555555",
        packageId: packageQueue[2].package_id,
        payload: { word: "bridge", reveal_count: 1 },
        pageIndex: 0,
      }),
      child_name: "Mina",
      package_title: packageQueue[2].title,
    },
    {
      event: buildEvent({
        eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200003",
        type: "page_replayed_audio",
        occurredAt: "2026-03-15T11:12:00Z",
        sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200003",
        childId: "12121212-1212-1212-1212-121212121212",
        packageId: packageQueue[1].package_id,
        payload: { replay_count: 2 },
        pageIndex: 0,
      }),
      child_name: "Leo",
      package_title: packageQueue[1].title,
    },
  ],
  progress_metrics: {
    completed_sessions: 1,
    translation_reveals: 1,
    audio_replays: 1,
  },
  generated_at: "2026-03-17T12:00:00Z",
};
