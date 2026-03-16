import {
  CAREGIVER_DASHBOARD_SCHEMA_VERSION,
  READING_EVENT_SCHEMA_VERSION,
  STORY_PACKAGE_SCHEMA_VERSION,
  type CaregiverChildSummaryV1,
  type CaregiverDashboardV1,
  type CaregiverWeeklyPlanItemV1,
  type ReadingEventV1,
  type StoryPackageManifestV1,
} from "@lumosreading/contracts";

export const demoHouseholdId = "44444444-4444-4444-4444-444444444444";

export type ResolvedChildSnapshot = CaregiverChildSummaryV1 & {
  currentPackage: StoryPackageManifestV1;
};

export type ResolvedWeeklyPlanItem = CaregiverWeeklyPlanItemV1 & {
  package: StoryPackageManifestV1;
};

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
  pageIndex?: number;
  payload: ReadingEventV1["payload"];
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

const packageLibrary = {
  friendshipTrail: buildPackage({
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
    imageUrl: "https://cdn.lumosreading.local/story-packages/demo/lantern-cover.png",
    audioUrl: "https://cdn.lumosreading.local/story-packages/demo/lantern-page-0.mp3",
  }),
  moonGarden: buildPackage({
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
    imageUrl: "https://cdn.lumosreading.local/story-packages/demo/moon-cover.png",
    audioUrl: "https://cdn.lumosreading.local/story-packages/demo/moon-page-0.mp3",
  }),
  bridgeWords: buildPackage({
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
    imageUrl: "https://cdn.lumosreading.local/story-packages/demo/bridge-cover.png",
    audioUrl: "https://cdn.lumosreading.local/story-packages/demo/bridge-page-0.mp3",
  }),
};

const recentEvents: ReadingEventV1[] = [
  buildEvent({
    eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200001",
    type: "session_completed",
    occurredAt: "2026-03-16T19:42:00Z",
    sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200001",
    childId: "55555555-5555-5555-5555-555555555555",
    packageId: packageLibrary.friendshipTrail.package_id,
    payload: { dwell_ms: 402000 },
  }),
  buildEvent({
    eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200002",
    type: "word_revealed_translation",
    occurredAt: "2026-03-16T19:21:00Z",
    sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200002",
    childId: "55555555-5555-5555-5555-555555555555",
    packageId: packageLibrary.bridgeWords.package_id,
    pageIndex: 0,
    payload: { word: "bridge", reveal_count: 1 },
  }),
  buildEvent({
    eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200003",
    type: "page_replayed_audio",
    occurredAt: "2026-03-15T11:12:00Z",
    sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200003",
    childId: "12121212-1212-1212-1212-121212121212",
    packageId: packageLibrary.moonGarden.package_id,
    pageIndex: 0,
    payload: { replay_count: 2 },
  }),
  buildEvent({
    eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200004",
    type: "assist_mode_enabled",
    occurredAt: "2026-03-14T20:08:00Z",
    sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200004",
    childId: "12121212-1212-1212-1212-121212121212",
    packageId: packageLibrary.moonGarden.package_id,
    payload: { assist_mode: "focus_support" },
  }),
];

export const fallbackCaregiverDashboard: CaregiverDashboardV1 = {
  schema_version: CAREGIVER_DASHBOARD_SCHEMA_VERSION,
  household_id: demoHouseholdId,
  household_name: "The Rivera household",
  featured_package_id: packageLibrary.friendshipTrail.package_id,
  package_queue: [packageLibrary.friendshipTrail, packageLibrary.moonGarden, packageLibrary.bridgeWords],
  recent_events: recentEvents,
  children: [
    {
      child_id: "55555555-5555-5555-5555-555555555555",
      name: "Mina",
      age_label: "Age 5",
      focus: "Shared reading and early vocabulary",
      weekly_goal: "4 completed sessions",
      current_package_id: packageLibrary.friendshipTrail.package_id,
    },
    {
      child_id: "12121212-1212-1212-1212-121212121212",
      name: "Leo",
      age_label: "Age 7",
      focus: "Bilingual assist with predictable pacing",
      weekly_goal: "3 sessions plus 2 calm replays",
      current_package_id: packageLibrary.bridgeWords.package_id,
    },
  ],
  weekly_plan: [
    {
      day: "Monday",
      mode: "Co-reading",
      package_id: packageLibrary.friendshipTrail.package_id,
      objective: "Warm start for the week with one caregiver prompt per page.",
    },
    {
      day: "Wednesday",
      mode: "Wind-down",
      package_id: packageLibrary.moonGarden.package_id,
      objective: "Use read-to-me mode with low stimulation and a slower page cadence.",
    },
    {
      day: "Saturday",
      mode: "Bilingual assist",
      package_id: packageLibrary.bridgeWords.package_id,
      objective: "Reveal only three translation words and track the replay count.",
    },
  ],
  progress_metrics: {
    completed_sessions: recentEvents.filter((event) => event.event_type === "session_completed").length,
    translation_reveals: recentEvents.filter((event) => event.event_type === "word_revealed_translation").length,
    audio_replays: recentEvents.filter((event) => event.event_type === "page_replayed_audio").length,
  },
  generated_at: "2026-03-17T12:00:00Z",
};

export function buildPackageMap(dashboard: CaregiverDashboardV1): Record<string, StoryPackageManifestV1> {
  return dashboard.package_queue.reduce<Record<string, StoryPackageManifestV1>>((accumulator, item) => {
    accumulator[item.package_id] = item;
    return accumulator;
  }, {});
}

export function resolveFeaturedPackage(dashboard: CaregiverDashboardV1): StoryPackageManifestV1 {
  const packageMap = buildPackageMap(dashboard);
  return packageMap[dashboard.featured_package_id] ?? dashboard.package_queue[0];
}

export function resolveChildren(dashboard: CaregiverDashboardV1): ResolvedChildSnapshot[] {
  const packageMap = buildPackageMap(dashboard);

  return dashboard.children.map((child) => ({
    ...child,
    currentPackage:
      packageMap[child.current_package_id] ??
      dashboard.package_queue.find((item) => item.package_id === child.current_package_id) ??
      dashboard.package_queue[0],
  }));
}

export function resolveWeeklyPlan(dashboard: CaregiverDashboardV1): ResolvedWeeklyPlanItem[] {
  const packageMap = buildPackageMap(dashboard);

  return dashboard.weekly_plan.map((item) => ({
    ...item,
    package:
      packageMap[item.package_id] ??
      dashboard.package_queue.find((candidate) => candidate.package_id === item.package_id) ??
      dashboard.package_queue[0],
  }));
}

export const startupOrder = [
  "docs/v2/01-strategy-review-and-references.md",
  "docs/v2/02-v2-architecture-and-migration-blueprint.md",
  "packages/contracts/schemas/README.md",
  "apps/README.md",
  "packages/contracts/README.md",
];
