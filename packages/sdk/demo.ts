import {
  CAREGIVER_CHILDREN_SCHEMA_VERSION,
  CAREGIVER_DASHBOARD_SCHEMA_VERSION,
  CAREGIVER_HOUSEHOLD_SCHEMA_VERSION,
  CAREGIVER_PLAN_SCHEMA_VERSION,
  CAREGIVER_PROGRESS_SCHEMA_VERSION,
  READING_EVENT_SCHEMA_VERSION,
  STORY_PACKAGE_SCHEMA_VERSION,
  type CaregiverChildAssignmentV1,
  type CaregiverChildSummaryV1,
  type CaregiverChildrenV1,
  type CaregiverDashboardV1,
  type CaregiverHouseholdV1,
  type CaregiverPlanV1,
  type CaregiverPlannedSessionV1,
  type CaregiverProgressEventV1,
  type CaregiverProgressV1,
  type CaregiverWeeklyPlanItemV1,
  type ReadingEventBatchRequestV2,
  type ReadingEventIngestedResponseV2,
  type ReadingEventV1,
  type ReadingSessionCreateV2,
  type ReadingSessionResponseV2,
  type StoryPackageManifestV1,
} from "@lumosreading/contracts";
import {
  buildChildDomainView,
  buildHouseholdOverview,
  buildPlanDomainView,
  buildProgressDomainView,
} from "./caregiver";
import { createPlaceholderOssStorageService } from "./object-storage";

export const demoHouseholdId = "44444444-4444-4444-4444-444444444444";
export const demoChildId = "55555555-5555-5555-5555-555555555555";
export const demoSecondaryChildId = "12121212-1212-1212-1212-121212121212";
export const demoReadingSessionId = "d1d3a8c0-05f3-45bd-9a56-72a911200099";
export const demoAcceptedAt = "2026-03-17T20:00:30Z";

export type ResolvedChildSnapshot = CaregiverChildSummaryV1 & {
  currentPackage: StoryPackageManifestV1;
};

export type ResolvedWeeklyPlanItem = CaregiverWeeklyPlanItemV1 & {
  package: StoryPackageManifestV1;
};

const placeholderStorage = createPlaceholderOssStorageService();

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
  coverObjectKey: string;
  audioObjectKey: string;
}): StoryPackageManifestV1 {
  const coverImageUrl = placeholderStorage.getPublicUrl(args.coverObjectKey);
  const audioUrl = placeholderStorage.getPublicUrl(args.audioObjectKey);

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
    cover_image_url: coverImageUrl,
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
          image_url: coverImageUrl,
          audio_url: audioUrl,
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
    coverObjectKey: "story-packages/demo/lantern/cover.png",
    audioObjectKey: "story-packages/demo/lantern/pages/0/audio.mp3",
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
    coverObjectKey: "story-packages/demo/moon-garden/cover.png",
    audioObjectKey: "story-packages/demo/moon-garden/pages/0/audio.mp3",
  }),
  bridgeWords: buildPackage({
    packageId: "99999999-9999-9999-9999-999999999999",
    storyMasterId: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    storyVariantId: "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    title: "Bridge Words",
    subtitle:
      "A bilingual-assist package with stable English narration and optional translation reveals.",
    languageMode: "en-US",
    difficultyLevel: "L3",
    ageBand: "6-8",
    durationSec: 540,
    tags: ["bilingual-assist", "vocabulary", "bridge"],
    vocabulary: ["bridge", "echo", "spark"],
    coverObjectKey: "story-packages/demo/bridge-words/cover.png",
    audioObjectKey: "story-packages/demo/bridge-words/pages/0/audio.mp3",
  }),
};

export const demoStoryPackageId = packageLibrary.friendshipTrail.package_id;
export const demoStoryPackage = packageLibrary.friendshipTrail;
export const demoPackageQueue = [
  packageLibrary.friendshipTrail,
  packageLibrary.moonGarden,
  packageLibrary.bridgeWords,
] as const;

const recentEvents: ReadingEventV1[] = [
  buildEvent({
    eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200001",
    type: "session_completed",
    occurredAt: "2026-03-16T19:42:00Z",
    sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200001",
    childId: demoChildId,
    packageId: packageLibrary.friendshipTrail.package_id,
    payload: { dwell_ms: 402000 },
  }),
  buildEvent({
    eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200002",
    type: "word_revealed_translation",
    occurredAt: "2026-03-16T19:21:00Z",
    sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200002",
    childId: demoChildId,
    packageId: packageLibrary.bridgeWords.package_id,
    payload: { word: "bridge", reveal_count: 1 },
    pageIndex: 0,
  }),
  buildEvent({
    eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200003",
    type: "page_replayed_audio",
    occurredAt: "2026-03-15T11:12:00Z",
    sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200003",
    childId: demoSecondaryChildId,
    packageId: packageLibrary.moonGarden.package_id,
    payload: { replay_count: 2 },
    pageIndex: 0,
  }),
  buildEvent({
    eventId: "c1d3a8c0-05f3-45bd-9a56-72a911200004",
    type: "assist_mode_enabled",
    occurredAt: "2026-03-14T20:08:00Z",
    sessionId: "d1d3a8c0-05f3-45bd-9a56-72a911200004",
    childId: demoSecondaryChildId,
    packageId: packageLibrary.moonGarden.package_id,
    payload: { assist_mode: "focus_support" },
  }),
];

export const fallbackCaregiverDashboard: CaregiverDashboardV1 = {
  schema_version: CAREGIVER_DASHBOARD_SCHEMA_VERSION,
  household_id: demoHouseholdId,
  household_name: "The Rivera household",
  featured_package_id: packageLibrary.friendshipTrail.package_id,
  package_queue: [
    packageLibrary.friendshipTrail,
    packageLibrary.moonGarden,
    packageLibrary.bridgeWords,
  ],
  recent_events: recentEvents,
  children: [
    {
      child_id: demoChildId,
      name: "Mina",
      age_label: "Age 5",
      focus: "Shared reading and early vocabulary",
      weekly_goal: "4 completed sessions",
      current_package_id: packageLibrary.friendshipTrail.package_id,
    },
    {
      child_id: demoSecondaryChildId,
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
    completed_sessions: recentEvents.filter((event) => event.event_type === "session_completed")
      .length,
    translation_reveals: recentEvents.filter(
      (event) => event.event_type === "word_revealed_translation",
    ).length,
    audio_replays: recentEvents.filter((event) => event.event_type === "page_replayed_audio")
      .length,
  },
  generated_at: "2026-03-17T12:00:00Z",
};

export function buildPackageMap(
  dashboard: CaregiverDashboardV1,
): Record<string, StoryPackageManifestV1> {
  return dashboard.package_queue.reduce<Record<string, StoryPackageManifestV1>>(
    (accumulator, item) => {
      accumulator[item.package_id] = item;
      return accumulator;
    },
    {},
  );
}

export function resolveFeaturedPackage(
  dashboard: CaregiverDashboardV1,
): StoryPackageManifestV1 {
  const packageMap = buildPackageMap(dashboard);
  return packageMap[dashboard.featured_package_id] ?? dashboard.package_queue[0];
}

export function resolveChildren(
  dashboard: CaregiverDashboardV1,
): ResolvedChildSnapshot[] {
  const packageMap = buildPackageMap(dashboard);

  return dashboard.children.map((child) => ({
    ...child,
    currentPackage:
      packageMap[child.current_package_id] ??
      dashboard.package_queue.find(
        (candidate) => candidate.package_id === child.current_package_id,
      ) ??
      dashboard.package_queue[0],
  }));
}

export function resolveWeeklyPlan(
  dashboard: CaregiverDashboardV1,
): ResolvedWeeklyPlanItem[] {
  const packageMap = buildPackageMap(dashboard);

  return dashboard.weekly_plan.map((item) => ({
    ...item,
    package:
      packageMap[item.package_id] ??
      dashboard.package_queue.find((candidate) => candidate.package_id === item.package_id) ??
      dashboard.package_queue[0],
  }));
}

export const fallbackCaregiverHousehold: CaregiverHouseholdV1 = {
  schema_version: CAREGIVER_HOUSEHOLD_SCHEMA_VERSION,
  household_id: fallbackCaregiverDashboard.household_id,
  household_name: fallbackCaregiverDashboard.household_name,
  featured_package_id: fallbackCaregiverDashboard.featured_package_id,
  featured_package: resolveFeaturedPackage(fallbackCaregiverDashboard),
  package_queue: fallbackCaregiverDashboard.package_queue,
  child_count: fallbackCaregiverDashboard.children.length,
  progress_metrics: fallbackCaregiverDashboard.progress_metrics,
  generated_at: fallbackCaregiverDashboard.generated_at,
};

export const fallbackCaregiverChildren: CaregiverChildrenV1 = {
  schema_version: CAREGIVER_CHILDREN_SCHEMA_VERSION,
  household_id: fallbackCaregiverDashboard.household_id,
  children: resolveChildren(fallbackCaregiverDashboard).map<CaregiverChildAssignmentV1>(
    (child) => ({
      child_id: child.child_id,
      name: child.name,
      age_label: child.age_label,
      focus: child.focus,
      weekly_goal: child.weekly_goal,
      current_package_id: child.current_package_id,
      current_package: child.currentPackage,
    }),
  ),
  planned_session_count: fallbackCaregiverDashboard.weekly_plan.length,
  generated_at: fallbackCaregiverDashboard.generated_at,
};

export const fallbackCaregiverPlan: CaregiverPlanV1 = {
  schema_version: CAREGIVER_PLAN_SCHEMA_VERSION,
  household_id: fallbackCaregiverDashboard.household_id,
  package_queue: fallbackCaregiverDashboard.package_queue,
  weekly_plan: resolveWeeklyPlan(fallbackCaregiverDashboard).map<CaregiverPlannedSessionV1>(
    (item) => ({
      day: item.day,
      mode: item.mode,
      package_id: item.package_id,
      objective: item.objective,
      package: item.package,
    }),
  ),
  generated_at: fallbackCaregiverDashboard.generated_at,
};

export const fallbackCaregiverProgress: CaregiverProgressV1 = {
  schema_version: CAREGIVER_PROGRESS_SCHEMA_VERSION,
  household_id: fallbackCaregiverDashboard.household_id,
  recent_events: fallbackCaregiverDashboard.recent_events.map<CaregiverProgressEventV1>(
    (event) => ({
      event,
      child_name:
        fallbackCaregiverDashboard.children.find(
          (child) => child.child_id === event.child_id,
        )?.name ?? event.child_id,
      package_title:
        fallbackCaregiverDashboard.package_queue.find(
          (storyPackage) => storyPackage.package_id === event.package_id,
        )?.title ?? event.package_id,
    }),
  ),
  progress_metrics: fallbackCaregiverDashboard.progress_metrics,
  generated_at: fallbackCaregiverDashboard.generated_at,
};

export const fallbackHouseholdOverview = buildHouseholdOverview(
  fallbackCaregiverHousehold,
);
export const fallbackChildDomainView = buildChildDomainView(
  fallbackCaregiverChildren,
);
export const fallbackPlanDomainView = buildPlanDomainView(
  fallbackCaregiverPlan,
);
export const fallbackProgressDomainView = buildProgressDomainView(
  fallbackCaregiverProgress,
);

export type DemoReadingSessionPayloadOptions = {
  childId?: string;
  packageId?: string;
  startedAt?: string;
  mode?: string;
  languageMode?: string;
  assistMode?: string[];
};

export function buildDemoReadingSessionPayload(
  options: DemoReadingSessionPayloadOptions = {},
): ReadingSessionCreateV2 {
  return {
    child_id: options.childId ?? demoChildId,
    package_id: options.packageId ?? demoStoryPackageId,
    started_at: options.startedAt ?? new Date().toISOString(),
    mode: options.mode ?? "read_to_me",
    language_mode: options.languageMode ?? "zh-CN",
    assist_mode: options.assistMode ?? ["read_aloud_sync"],
  };
}

export type DemoReadingSessionResponseOptions = {
  sessionId?: string;
  childId?: string;
  packageId?: string;
  acceptedAt?: string;
};

export function buildDemoReadingSessionResponse(
  options: DemoReadingSessionResponseOptions = {},
): ReadingSessionResponseV2 {
  return {
    session_id: options.sessionId ?? demoReadingSessionId,
    status: "accepted",
    accepted_at: options.acceptedAt ?? demoAcceptedAt,
    child_id: options.childId ?? demoChildId,
    package_id: options.packageId ?? demoStoryPackageId,
  };
}

export type DemoReadingEventBatchRequestOptions = {
  childId?: string;
  packageId?: string;
  sessionId?: string;
  occurredAt?: string;
  appVersion?: string;
  languageMode?: string;
};

export function buildDemoReadingEventBatchRequest(
  options: DemoReadingEventBatchRequestOptions = {},
): ReadingEventBatchRequestV2 {
  const childId = options.childId ?? demoChildId;
  const packageId = options.packageId ?? demoStoryPackageId;
  const sessionId = options.sessionId ?? demoReadingSessionId;
  const occurredAt = options.occurredAt ?? new Date().toISOString();
  const appVersion = options.appVersion ?? "2.0.0";
  const languageMode = options.languageMode ?? "zh-CN";

  return {
    events: [
      {
        schema_version: READING_EVENT_SCHEMA_VERSION,
        event_id: "c1d3a8c0-05f3-45bd-9a56-72a911200101",
        event_type: "session_started",
        occurred_at: occurredAt,
        session_id: sessionId,
        child_id: childId,
        package_id: packageId,
        page_index: null,
        platform: "ipadOS",
        surface: "child-app",
        app_version: appVersion,
        language_mode: languageMode,
        payload: {
          source: "api-workbench",
        },
      },
      {
        schema_version: READING_EVENT_SCHEMA_VERSION,
        event_id: "c1d3a8c0-05f3-45bd-9a56-72a911200102",
        event_type: "page_viewed",
        occurred_at: occurredAt,
        session_id: sessionId,
        child_id: childId,
        package_id: packageId,
        page_index: 0,
        platform: "ipadOS",
        surface: "child-app",
        app_version: appVersion,
        language_mode: languageMode,
        payload: {
          dwell_ms: 18000,
          source: "api-workbench",
        },
      },
    ],
  };
}

export type DemoReadingEventIngestedResponseOptions = {
  acceptedAt?: string;
  acceptedCount?: number;
  sessionIds?: string[];
};

export function buildDemoReadingEventIngestedResponse(
  options: DemoReadingEventIngestedResponseOptions = {},
): ReadingEventIngestedResponseV2 {
  return {
    status: "accepted",
    accepted_count: options.acceptedCount ?? 2,
    accepted_at: options.acceptedAt ?? demoAcceptedAt,
    session_ids: options.sessionIds ?? [demoReadingSessionId],
  };
}
