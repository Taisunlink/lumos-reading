import {
  CAREGIVER_ASSIGNMENT_COMMAND_SCHEMA_VERSION,
  CAREGIVER_ASSIGNMENT_RESPONSE_SCHEMA_VERSION,
  type CaregiverAssignmentCommandV1,
  type CaregiverAssignmentResponseV1,
  CAREGIVER_CHILDREN_SCHEMA_VERSION,
  CAREGIVER_DASHBOARD_SCHEMA_VERSION,
  CAREGIVER_HOUSEHOLD_SCHEMA_VERSION,
  CAREGIVER_PLAN_SCHEMA_VERSION,
  CAREGIVER_PROGRESS_SCHEMA_VERSION,
  CHILD_HOME_SCHEMA_VERSION,
  READING_EVENT_SCHEMA_VERSION,
  SAFETY_AUDIT_SCHEMA_VERSION,
  STORY_BRIEF_COMMAND_SCHEMA_VERSION,
  STORY_BRIEF_INDEX_SCHEMA_VERSION,
  STORY_BRIEF_SCHEMA_VERSION,
  STORY_GENERATION_JOB_COMMAND_SCHEMA_VERSION,
  STORY_GENERATION_JOB_INDEX_SCHEMA_VERSION,
  STORY_GENERATION_JOB_SCHEMA_VERSION,
  STORY_PACKAGE_BUILD_COMMAND_SCHEMA_VERSION,
  STORY_PACKAGE_BUILD_SCHEMA_VERSION,
  STORY_PACKAGE_DRAFT_INDEX_SCHEMA_VERSION,
  STORY_PACKAGE_DRAFT_SCHEMA_VERSION,
  STORY_PACKAGE_HISTORY_SCHEMA_VERSION,
  STORY_PACKAGE_RECALL_COMMAND_SCHEMA_VERSION,
  STORY_PACKAGE_REVIEW_COMMAND_SCHEMA_VERSION,
  STORY_PACKAGE_RELEASE_COMMAND_SCHEMA_VERSION,
  STORY_PACKAGE_RELEASE_SCHEMA_VERSION,
  STORY_PACKAGE_ROLLBACK_COMMAND_SCHEMA_VERSION,
  STORY_PACKAGE_SCHEMA_VERSION,
  type ChildHomeV1,
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
  type SafetyAuditV1,
  type StoryBriefCommandV1,
  type StoryBriefIndexV1,
  type StoryBriefV1,
  type StoryGenerationJobCommandV1,
  type StoryGenerationJobIndexV1,
  type StoryGenerationJobV1,
  type StoryPackageBuildCommandV1,
  type StoryPackageBuildV1,
  type StoryPackageDraftIndexV1,
  type StoryPackageDraftV1,
  type StoryPackageHistoryV1,
  type StoryPackageRecallCommandV1,
  type StoryPackageReviewCommandV1,
  type StoryPackageReleaseCommandV1,
  type StoryPackageReleaseV1,
  type StoryPackageRollbackCommandV1,
  type StoryPackageManifestV1,
} from '@lumosreading/contracts';
import {
  buildChildDomainView,
  buildHouseholdOverview,
  buildPlanDomainView,
  buildProgressDomainView,
} from './caregiver';
import { createPlaceholderOssStorageService } from './object-storage';

export const demoHouseholdId = '44444444-4444-4444-4444-444444444444';
export const demoChildId = '55555555-5555-5555-5555-555555555555';
export const demoSecondaryChildId = '12121212-1212-1212-1212-121212121212';
export const demoReadingSessionId = 'd1d3a8c0-05f3-45bd-9a56-72a911200099';
export const demoAcceptedAt = '2026-03-17T20:00:30Z';
export const demoDraftId = '45454545-4545-4545-4545-454545454545';
export const demoBuildId = '56565656-5656-5656-5656-565656565656';
export const demoReleaseId = '67676767-6767-6767-6767-676767676767';
export const demoStoryBriefId = '10101010-1010-4010-8010-101010101010';
export const demoAiPackageId = '20202020-2020-4020-8020-202020202020';
export const demoAiDraftId = '30303030-3030-4030-8030-303030303030';
export const demoAiAuditId = '40404040-4040-4040-4040-404040404040';
export const demoDraftGenerationJobId = '50505050-5050-4050-8050-505050505050';
export const demoMediaGenerationJobId = '60606060-6060-4060-8060-606060606060';

export type ResolvedChildSnapshot = CaregiverChildSummaryV1 & {
  currentPackage: StoryPackageManifestV1;
};

export type ResolvedWeeklyPlanItem = CaregiverWeeklyPlanItemV1 & {
  package: StoryPackageManifestV1;
};

const placeholderStorage = createPlaceholderOssStorageService();

type DemoPackagePageInput = {
  text: string;
  vocabulary: string[];
  imageObjectKey?: string;
  audioObjectKey?: string;
  caregiverPromptIds?: string[];
  lang?: string;
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
  coverObjectKey: string;
  audioObjectKey: string;
  pages?: DemoPackagePageInput[];
}): StoryPackageManifestV1 {
  const coverImageUrl = placeholderStorage.getPublicUrl(args.coverObjectKey);
  const pages = (
    args.pages ?? [
      {
        text: args.subtitle,
        vocabulary: [],
      },
    ]
  ).map((page, pageIndex) => ({
    page_index: pageIndex,
    text_runs: [
      {
        text: page.text,
        lang: page.lang ?? args.languageMode,
        tts_timing: [0, 320, 840],
      },
    ],
    media: {
      image_url: placeholderStorage.getPublicUrl(
        page.imageObjectKey ?? args.coverObjectKey
      ),
      audio_url: placeholderStorage.getPublicUrl(
        page.audioObjectKey ?? args.audioObjectKey
      ),
    },
    overlays: {
      vocabulary: page.vocabulary,
      caregiver_prompt_ids: page.caregiverPromptIds ?? [
        `prompt-${pageIndex + 1}`,
      ],
    },
  }));

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
    release_channel: 'pilot',
    cover_image_url: coverImageUrl,
    tags: args.tags,
    safety: {
      review_status: 'approved',
      reviewed_at: '2026-03-17T12:00:00Z',
      review_policy_version: '2026.03',
    },
    pages,
  };
}

function buildEvent(args: {
  eventId: string;
  type: ReadingEventV1['event_type'];
  occurredAt: string;
  sessionId: string;
  childId: string;
  packageId: string;
  payload: ReadingEventV1['payload'];
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
    platform: 'ipadOS',
    surface: 'child-app',
    app_version: '2.0.0',
    language_mode: resolveDemoPackageLanguageMode(args.packageId),
    payload: args.payload,
  };
}

const packageLibrary = {
  friendshipTrail: buildPackage({
    packageId: '33333333-3333-3333-3333-333333333333',
    storyMasterId: '11111111-1111-1111-1111-111111111111',
    storyVariantId: '22222222-2222-2222-2222-222222222222',
    title: 'The Lantern Trail',
    subtitle:
      'A co-reading story about checking in, waiting, and returning together.',
    languageMode: 'zh-CN',
    difficultyLevel: 'L2',
    ageBand: '4-6',
    durationSec: 480,
    tags: ['friendship', 'shared-reading', 'comfort'],
    coverObjectKey: 'story-packages/demo/lantern/cover.png',
    audioObjectKey: 'story-packages/demo/lantern/pages/0/audio.mp3',
    pages: [
      {
        text: 'Mina lifted a lantern and waited while the path outside turned soft and quiet.',
        vocabulary: ['lantern', 'quiet', 'path'],
        audioObjectKey: 'story-packages/demo/lantern/pages/0/audio.mp3',
      },
      {
        text: 'At the bridge, she whispered that waiting together can feel warm instead of lonely.',
        vocabulary: ['bridge', 'waiting', 'warm'],
        audioObjectKey: 'story-packages/demo/lantern/pages/1/audio.mp3',
      },
      {
        text: 'When the last light blinked home, Mina smiled because every promise had found its way back.',
        vocabulary: ['light', 'promise', 'return'],
        audioObjectKey: 'story-packages/demo/lantern/pages/2/audio.mp3',
      },
    ],
  }),
  moonGarden: buildPackage({
    packageId: '66666666-6666-6666-6666-666666666666',
    storyMasterId: '77777777-7777-7777-7777-777777777777',
    storyVariantId: '88888888-8888-8888-8888-888888888888',
    title: 'Moon Garden Breathing',
    subtitle:
      'A calming package designed for predictable pacing and low stimulation.',
    languageMode: 'en-US',
    difficultyLevel: 'L1',
    ageBand: '4-6',
    durationSec: 360,
    tags: ['calm', 'predictable', 'wind-down'],
    coverObjectKey: 'story-packages/demo/moon-garden/cover.png',
    audioObjectKey: 'story-packages/demo/moon-garden/pages/0/audio.mp3',
    pages: [
      {
        text: 'In the moon garden, Leo counted three silver leaves before he took his first slow breath.',
        vocabulary: ['moon', 'garden', 'breath'],
        audioObjectKey: 'story-packages/demo/moon-garden/pages/0/audio.mp3',
      },
      {
        text: 'The fountain glowed once, then twice, and Leo let his shoulders grow quiet with the light.',
        vocabulary: ['fountain', 'glow', 'quiet'],
        audioObjectKey: 'story-packages/demo/moon-garden/pages/1/audio.mp3',
      },
      {
        text: 'By the time the stars blinked goodnight, Leo knew exactly how to find the calm path home.',
        vocabulary: ['stars', 'goodnight', 'calm'],
        audioObjectKey: 'story-packages/demo/moon-garden/pages/2/audio.mp3',
      },
    ],
  }),
  bridgeWords: buildPackage({
    packageId: '99999999-9999-9999-9999-999999999999',
    storyMasterId: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    storyVariantId: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    title: 'Bridge Words',
    subtitle:
      'A bilingual-assist package with stable English narration and optional translation reveals.',
    languageMode: 'en-US',
    difficultyLevel: 'L3',
    ageBand: '6-8',
    durationSec: 540,
    tags: ['bilingual-assist', 'vocabulary', 'bridge'],
    coverObjectKey: 'story-packages/demo/bridge-words/cover.png',
    audioObjectKey: 'story-packages/demo/bridge-words/pages/0/audio.mp3',
    pages: [
      {
        text: 'A bridge can hold two ideas at once, just like one story can carry two languages.',
        vocabulary: ['bridge', 'languages', 'story'],
        audioObjectKey: 'story-packages/demo/bridge-words/pages/0/audio.mp3',
      },
      {
        text: 'When Mei heard an echo under the stones, she paused and asked what the new word might mean.',
        vocabulary: ['echo', 'stones', 'mean'],
        audioObjectKey: 'story-packages/demo/bridge-words/pages/1/audio.mp3',
      },
      {
        text: 'One bright spark of translation was enough, because the main narration still stayed clear.',
        vocabulary: ['spark', 'translation', 'clear'],
        audioObjectKey: 'story-packages/demo/bridge-words/pages/2/audio.mp3',
      },
    ],
  }),
};

export const demoStoryPackageId = packageLibrary.friendshipTrail.package_id;
export const demoStoryPackage = packageLibrary.friendshipTrail;
export const demoPackageQueue = [
  packageLibrary.friendshipTrail,
  packageLibrary.moonGarden,
  packageLibrary.bridgeWords,
] as const;

export const demoSafetyAudit: SafetyAuditV1 = {
  schema_version: SAFETY_AUDIT_SCHEMA_VERSION,
  audit_id: '78787878-7878-7878-7878-787878787878',
  target_type: 'story_package',
  target_id: demoStoryPackageId,
  audit_source: 'pre_release',
  audit_status: 'approved',
  severity: 'low',
  policy_version: '2026.03',
  findings: [],
  reviewer: {
    reviewer_type: 'hybrid',
    reviewer_id: 'ops.review.bot',
  },
  created_at: '2026-03-17T11:45:00Z',
  reviewed_at: '2026-03-17T12:00:00Z',
  resolution: {
    action: 'release',
    notes: 'Bootstrap package cleared for pilot release.',
    resolved_at: '2026-03-17T12:00:00Z',
  },
};

export const fallbackStoryPackageDraft: StoryPackageDraftV1 = {
  schema_version: STORY_PACKAGE_DRAFT_SCHEMA_VERSION,
  draft_id: demoDraftId,
  package_id: demoStoryPackageId,
  source_type: 'editorial',
  workflow_state: 'released',
  package_preview: demoStoryPackage,
  safety_audit: demoSafetyAudit,
  operator_notes: ['Bootstrap runtime package seeded for release-loop validation.'],
  latest_build_id: demoBuildId,
  active_release_id: demoReleaseId,
  created_at: '2026-03-17T11:40:00Z',
  updated_at: demoAcceptedAt,
};

export const fallbackStoryPackageDraftIndex: StoryPackageDraftIndexV1 = {
  schema_version: STORY_PACKAGE_DRAFT_INDEX_SCHEMA_VERSION,
  generated_at: demoAcceptedAt,
  drafts: [fallbackStoryPackageDraft],
};

export const demoAiSafetyAudit: SafetyAuditV1 = {
  schema_version: SAFETY_AUDIT_SCHEMA_VERSION,
  audit_id: demoAiAuditId,
  target_type: 'story_package',
  target_id: demoAiPackageId,
  audit_source: 'pre_release',
  audit_status: 'pending',
  severity: 'medium',
  policy_version: '2026.04-ai-draft',
  findings: [
    {
      code: 'human-review-required',
      title: 'Human review required',
      description:
        'AI-generated content must be reviewed before build and release.',
      severity: 'medium',
      page_index: null,
      action_required: true,
    },
  ],
  reviewer: {
    reviewer_type: 'system',
    reviewer_id: 'ai.supply-chain',
  },
  created_at: '2026-03-31T09:05:00Z',
  reviewed_at: null,
  resolution: {
    action: 'revise',
    notes: 'Awaiting editor review after AI generation.',
    resolved_at: null,
  },
};

export const demoAiStoryPackage: StoryPackageManifestV1 = {
  schema_version: STORY_PACKAGE_SCHEMA_VERSION,
  package_id: demoAiPackageId,
  story_master_id: '70707070-7070-4070-8070-707070707070',
  story_variant_id: '80808080-8080-4080-8080-808080808080',
  title: 'Cloud Post for Tomorrow',
  subtitle: 'A reviewable AI draft about patience and promise-keeping.',
  language_mode: 'en-US',
  difficulty_level: 'L2',
  age_band: '4-6',
  estimated_duration_sec: 450,
  release_channel: 'internal',
  cover_image_url: placeholderStorage.getPublicUrl(
    `story-packages/generated/${demoAiPackageId}/placeholder/cover.png`,
  ),
  tags: ['patience', 'ai-generated', 'review-required'],
  safety: {
    review_status: 'limited_release',
    reviewed_at: null,
    review_policy_version: '2026.04-ai-draft',
  },
  pages: [
    {
      page_index: 0,
      text_runs: [
        {
          text: "Nia wrote a cloud post so tomorrow would remember today's promise.",
          lang: 'en-US',
          tts_timing: [0, 320, 760, 1180],
        },
      ],
      media: {
        image_url: placeholderStorage.getPublicUrl(
          `story-packages/generated/${demoAiPackageId}/placeholder/pages/0/image.png`,
        ),
        audio_url: placeholderStorage.getPublicUrl(
          `story-packages/generated/${demoAiPackageId}/placeholder/pages/0/audio.mp3`,
        ),
      },
      overlays: {
        vocabulary: ['promise', 'tomorrow'],
        caregiver_prompt_ids: ['ai-draft-prompt-1'],
      },
    },
    {
      page_index: 1,
      text_runs: [
        {
          text: 'She tucked the message under a blue leaf and waited without peeking.',
          lang: 'en-US',
          tts_timing: [0, 320, 760, 1180],
        },
      ],
      media: {
        image_url: placeholderStorage.getPublicUrl(
          `story-packages/generated/${demoAiPackageId}/placeholder/pages/1/image.png`,
        ),
        audio_url: placeholderStorage.getPublicUrl(
          `story-packages/generated/${demoAiPackageId}/placeholder/pages/1/audio.mp3`,
        ),
      },
      overlays: {
        vocabulary: ['wait', 'leaf'],
        caregiver_prompt_ids: ['ai-draft-prompt-2'],
      },
    },
    {
      page_index: 2,
      text_runs: [
        {
          text: 'In the morning, the cloud post returned with a small answer and a calm smile.',
          lang: 'en-US',
          tts_timing: [0, 320, 760, 1180],
        },
      ],
      media: {
        image_url: placeholderStorage.getPublicUrl(
          `story-packages/generated/${demoAiPackageId}/placeholder/pages/2/image.png`,
        ),
        audio_url: placeholderStorage.getPublicUrl(
          `story-packages/generated/${demoAiPackageId}/placeholder/pages/2/audio.mp3`,
        ),
      },
      overlays: {
        vocabulary: ['return', 'answer'],
        caregiver_prompt_ids: ['ai-draft-prompt-3'],
      },
    },
  ],
};

export const fallbackAiStoryPackageDraft: StoryPackageDraftV1 = {
  schema_version: STORY_PACKAGE_DRAFT_SCHEMA_VERSION,
  draft_id: demoAiDraftId,
  package_id: demoAiPackageId,
  source_type: 'ai_generated',
  workflow_state: 'draft',
  package_preview: demoAiStoryPackage,
  safety_audit: demoAiSafetyAudit,
  operator_notes: [
    "AI draft assembled from brief 'Cloud Post for Tomorrow' with 3 generated pages.",
    'Media generation completed with placeholder after qwen credentials were unavailable.',
  ],
  latest_build_id: null,
  active_release_id: null,
  created_at: '2026-03-31T09:00:00Z',
  updated_at: '2026-03-31T09:10:00Z',
};

export const fallbackStoryBrief: StoryBriefV1 = {
  schema_version: STORY_BRIEF_SCHEMA_VERSION,
  brief_id: demoStoryBriefId,
  package_id: demoAiPackageId,
  title: 'Cloud Post for Tomorrow',
  theme: 'patience',
  premise:
    'A child leaves a message for tomorrow and learns that waiting can be gentle.',
  language_mode: 'en-US',
  age_band: '4-6',
  desired_page_count: 3,
  status: 'media_ready',
  source_outline: 'Keep the emotional arc calm and bedtime-friendly.',
  latest_job_id: demoMediaGenerationJobId,
  latest_failure_reason: null,
  created_at: '2026-03-31T09:00:00Z',
  updated_at: '2026-03-31T09:10:00Z',
};

export const fallbackStoryBriefIndex: StoryBriefIndexV1 = {
  schema_version: STORY_BRIEF_INDEX_SCHEMA_VERSION,
  generated_at: '2026-03-31T09:10:00Z',
  briefs: [fallbackStoryBrief],
};

export const fallbackDraftGenerationJob: StoryGenerationJobV1 = {
  schema_version: STORY_GENERATION_JOB_SCHEMA_VERSION,
  job_id: demoDraftGenerationJobId,
  brief_id: demoStoryBriefId,
  package_id: demoAiPackageId,
  job_type: 'brief_to_draft',
  status: 'succeeded',
  selected_provider: 'placeholder',
  attempts: [
    {
      provider: 'placeholder',
      status: 'succeeded',
      reason: 'deterministic_draft_assembly',
    },
  ],
  generated_asset_keys: [],
  requested_by: 'studio.operator',
  requested_at: '2026-03-31T09:05:00Z',
  completed_at: '2026-03-31T09:05:00Z',
  failure_reason: null,
  notes: 'Seeded AI draft for studio review visibility.',
};

export const fallbackMediaGenerationJob: StoryGenerationJobV1 = {
  schema_version: STORY_GENERATION_JOB_SCHEMA_VERSION,
  job_id: demoMediaGenerationJobId,
  brief_id: demoStoryBriefId,
  package_id: demoAiPackageId,
  job_type: 'draft_to_media',
  status: 'succeeded',
  selected_provider: 'placeholder',
  attempts: [
    {
      provider: 'qwen',
      status: 'failed',
      reason: 'credentials_unavailable',
    },
    {
      provider: 'placeholder',
      status: 'succeeded',
      reason: 'placeholder_generation',
    },
  ],
  generated_asset_keys: [
    `story-packages/generated/${demoAiPackageId}/placeholder/cover.png`,
    `story-packages/generated/${demoAiPackageId}/placeholder/pages/0/image.png`,
    `story-packages/generated/${demoAiPackageId}/placeholder/pages/0/audio.mp3`,
    `story-packages/generated/${demoAiPackageId}/placeholder/pages/1/image.png`,
    `story-packages/generated/${demoAiPackageId}/placeholder/pages/1/audio.mp3`,
    `story-packages/generated/${demoAiPackageId}/placeholder/pages/2/image.png`,
    `story-packages/generated/${demoAiPackageId}/placeholder/pages/2/audio.mp3`,
  ],
  requested_by: 'studio.operator',
  requested_at: '2026-03-31T09:10:00Z',
  completed_at: '2026-03-31T09:10:00Z',
  failure_reason: null,
  notes: 'Seeded media fallback record with placeholder assets.',
};

export const fallbackStoryGenerationJobIndex: StoryGenerationJobIndexV1 = {
  schema_version: STORY_GENERATION_JOB_INDEX_SCHEMA_VERSION,
  generated_at: '2026-03-31T09:10:00Z',
  jobs: [fallbackMediaGenerationJob, fallbackDraftGenerationJob],
};

export function buildDemoStoryBriefCommand(
  overrides: Partial<StoryBriefCommandV1> = {},
): StoryBriefCommandV1 {
  return {
    schema_version: STORY_BRIEF_COMMAND_SCHEMA_VERSION,
    title: overrides.title ?? fallbackStoryBrief.title,
    theme: overrides.theme ?? fallbackStoryBrief.theme,
    premise: overrides.premise ?? fallbackStoryBrief.premise,
    language_mode: overrides.language_mode ?? fallbackStoryBrief.language_mode,
    age_band: overrides.age_band ?? fallbackStoryBrief.age_band,
    desired_page_count:
      overrides.desired_page_count ?? fallbackStoryBrief.desired_page_count,
    source_outline: overrides.source_outline ?? fallbackStoryBrief.source_outline,
    requested_by: overrides.requested_by ?? 'studio.operator',
    requested_at: overrides.requested_at ?? '2026-03-31T09:00:00Z',
  };
}

export function buildDemoStoryGenerationJobCommand(
  overrides: Partial<StoryGenerationJobCommandV1> = {},
): StoryGenerationJobCommandV1 {
  return {
    schema_version: STORY_GENERATION_JOB_COMMAND_SCHEMA_VERSION,
    job_type: overrides.job_type ?? 'brief_to_draft',
    provider_preference: overrides.provider_preference ?? 'placeholder',
    notes: overrides.notes ?? 'Drive seeded AI generation flow.',
    requested_by: overrides.requested_by ?? 'studio.operator',
    requested_at: overrides.requested_at ?? '2026-03-31T09:05:00Z',
  };
}

export function buildDemoStoryPackageReviewCommand(
  overrides: Partial<StoryPackageReviewCommandV1> = {},
): StoryPackageReviewCommandV1 {
  return {
    schema_version: STORY_PACKAGE_REVIEW_COMMAND_SCHEMA_VERSION,
    audit_status: overrides.audit_status ?? 'approved',
    resolution_action: overrides.resolution_action ?? 'release',
    reviewer_type: overrides.reviewer_type ?? 'human',
    reviewer_id: overrides.reviewer_id ?? 'studio.reviewer',
    notes: overrides.notes ?? 'Cleared for package build and runtime release.',
    requested_by: overrides.requested_by ?? 'studio.operator',
    requested_at: overrides.requested_at ?? '2026-03-31T09:20:00Z',
  };
}

export function buildDemoStoryPackageBuildCommand(
  overrides: Partial<StoryPackageBuildCommandV1> = {},
): StoryPackageBuildCommandV1 {
  return {
    schema_version: STORY_PACKAGE_BUILD_COMMAND_SCHEMA_VERSION,
    build_reason: overrides.build_reason ?? 'editorial_release',
    requested_by: overrides.requested_by ?? 'studio.operator',
    requested_at: overrides.requested_at ?? demoAcceptedAt,
  };
}

export function buildDemoStoryPackageBuild(
  overrides: Partial<StoryPackageBuildV1> = {},
): StoryPackageBuildV1 {
  return {
    schema_version: STORY_PACKAGE_BUILD_SCHEMA_VERSION,
    build_id: overrides.build_id ?? demoBuildId,
    draft_id: overrides.draft_id ?? demoDraftId,
    package_id: overrides.package_id ?? demoStoryPackageId,
    build_version: overrides.build_version ?? 2,
    status: overrides.status ?? 'succeeded',
    build_reason: overrides.build_reason ?? 'editorial_release',
    worker_job_id: overrides.worker_job_id ?? 'story-package-build:demo:2',
    manifest_object_key:
      overrides.manifest_object_key ??
      `story-packages/runtime/${demoStoryPackageId}/build-2/manifest.json`,
    artifact_root_object_key:
      overrides.artifact_root_object_key ??
      `story-packages/runtime/${demoStoryPackageId}/build-2`,
    requested_by: overrides.requested_by ?? 'studio.operator',
    requested_at: overrides.requested_at ?? demoAcceptedAt,
    completed_at: overrides.completed_at ?? demoAcceptedAt,
    failure_message: overrides.failure_message ?? null,
    built_package: overrides.built_package ?? {
      ...demoStoryPackage,
      cover_image_url: placeholderStorage.getPublicUrl(
        `story-packages/runtime/${demoStoryPackageId}/build-2/cover.png`
      ),
      pages: demoStoryPackage.pages.map((page) => ({
        ...page,
        media: {
          image_url: placeholderStorage.getPublicUrl(
            `story-packages/runtime/${demoStoryPackageId}/build-2/pages/${page.page_index}/image.png`
          ),
          audio_url: placeholderStorage.getPublicUrl(
            `story-packages/runtime/${demoStoryPackageId}/build-2/pages/${page.page_index}/audio.mp3`
          ),
        },
      })),
    },
  };
}

export function buildDemoStoryPackageReleaseCommand(
  overrides: Partial<StoryPackageReleaseCommandV1> = {},
): StoryPackageReleaseCommandV1 {
  return {
    schema_version: STORY_PACKAGE_RELEASE_COMMAND_SCHEMA_VERSION,
    build_id: overrides.build_id ?? demoBuildId,
    release_channel: overrides.release_channel ?? 'general',
    requested_by: overrides.requested_by ?? 'studio.operator',
    requested_at: overrides.requested_at ?? demoAcceptedAt,
    notes: overrides.notes ?? 'Promote build for runtime validation.',
  };
}

export function buildDemoStoryPackageRelease(
  overrides: Partial<StoryPackageReleaseV1> = {},
): StoryPackageReleaseV1 {
  return {
    schema_version: STORY_PACKAGE_RELEASE_SCHEMA_VERSION,
    release_id: overrides.release_id ?? demoReleaseId,
    package_id: overrides.package_id ?? demoStoryPackageId,
    draft_id: overrides.draft_id ?? demoDraftId,
    build_id: overrides.build_id ?? demoBuildId,
    release_version: overrides.release_version ?? 2,
    release_channel: overrides.release_channel ?? 'general',
    status: overrides.status ?? 'active',
    runtime_lookup_key:
      overrides.runtime_lookup_key ?? `/api/v2/story-packages/${demoStoryPackageId}`,
    requested_by: overrides.requested_by ?? 'studio.operator',
    released_at: overrides.released_at ?? demoAcceptedAt,
    notes: overrides.notes ?? 'Promote build for runtime validation.',
    recalled_at: overrides.recalled_at ?? null,
    rollback_of_release_id: overrides.rollback_of_release_id ?? null,
  };
}

export function buildDemoStoryPackageRecallCommand(
  overrides: Partial<StoryPackageRecallCommandV1> = {},
): StoryPackageRecallCommandV1 {
  return {
    schema_version: STORY_PACKAGE_RECALL_COMMAND_SCHEMA_VERSION,
    release_id: overrides.release_id ?? demoReleaseId,
    requested_by: overrides.requested_by ?? 'studio.operator',
    requested_at: overrides.requested_at ?? demoAcceptedAt,
    reason: overrides.reason ?? 'Recall after operator review.',
  };
}

export function buildDemoStoryPackageRollbackCommand(
  overrides: Partial<StoryPackageRollbackCommandV1> = {},
): StoryPackageRollbackCommandV1 {
  return {
    schema_version: STORY_PACKAGE_ROLLBACK_COMMAND_SCHEMA_VERSION,
    target_release_id: overrides.target_release_id ?? demoReleaseId,
    requested_by: overrides.requested_by ?? 'studio.operator',
    requested_at: overrides.requested_at ?? demoAcceptedAt,
    reason: overrides.reason ?? 'Rollback to last stable release.',
  };
}

export function buildDemoStoryPackageHistory(
  overrides: Partial<StoryPackageHistoryV1> = {},
): StoryPackageHistoryV1 {
  const build = buildDemoStoryPackageBuild();
  const release = buildDemoStoryPackageRelease();

  return {
    schema_version: STORY_PACKAGE_HISTORY_SCHEMA_VERSION,
    package_id: overrides.package_id ?? demoStoryPackageId,
    draft: overrides.draft ?? {
      ...fallbackStoryPackageDraft,
      latest_build_id: build.build_id,
      active_release_id: release.release_id,
    },
    builds: overrides.builds ?? [build],
    releases: overrides.releases ?? [release],
    active_release_id: overrides.active_release_id ?? release.release_id,
    generated_at: overrides.generated_at ?? demoAcceptedAt,
  };
}

function resolveDemoPackageLanguageMode(packageId: string): string {
  return (
    demoPackageQueue.find(item => item.package_id === packageId)?.language_mode ??
    demoStoryPackage.language_mode
  );
}

const recentEvents: ReadingEventV1[] = [
  buildEvent({
    eventId: 'c1d3a8c0-05f3-45bd-9a56-72a911200001',
    type: 'session_completed',
    occurredAt: '2026-03-16T19:42:00Z',
    sessionId: 'd1d3a8c0-05f3-45bd-9a56-72a911200001',
    childId: demoChildId,
    packageId: packageLibrary.friendshipTrail.package_id,
    payload: { dwell_ms: 402000 },
  }),
  buildEvent({
    eventId: 'c1d3a8c0-05f3-45bd-9a56-72a911200002',
    type: 'word_revealed_translation',
    occurredAt: '2026-03-16T19:21:00Z',
    sessionId: 'd1d3a8c0-05f3-45bd-9a56-72a911200002',
    childId: demoChildId,
    packageId: packageLibrary.bridgeWords.package_id,
    payload: { word: 'bridge', reveal_count: 1 },
    pageIndex: 0,
  }),
  buildEvent({
    eventId: 'c1d3a8c0-05f3-45bd-9a56-72a911200003',
    type: 'page_replayed_audio',
    occurredAt: '2026-03-15T11:12:00Z',
    sessionId: 'd1d3a8c0-05f3-45bd-9a56-72a911200003',
    childId: demoSecondaryChildId,
    packageId: packageLibrary.moonGarden.package_id,
    payload: { replay_count: 2 },
    pageIndex: 0,
  }),
  buildEvent({
    eventId: 'c1d3a8c0-05f3-45bd-9a56-72a911200004',
    type: 'assist_mode_enabled',
    occurredAt: '2026-03-14T20:08:00Z',
    sessionId: 'd1d3a8c0-05f3-45bd-9a56-72a911200004',
    childId: demoSecondaryChildId,
    packageId: packageLibrary.moonGarden.package_id,
    payload: { assist_mode: 'focus_support' },
  }),
];

export const fallbackCaregiverDashboard: CaregiverDashboardV1 = {
  schema_version: CAREGIVER_DASHBOARD_SCHEMA_VERSION,
  household_id: demoHouseholdId,
  household_name: 'The Rivera household',
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
      name: 'Mina',
      age_label: 'Age 5',
      focus: 'Shared reading and early vocabulary',
      weekly_goal: '4 completed sessions',
      current_package_id: packageLibrary.friendshipTrail.package_id,
    },
    {
      child_id: demoSecondaryChildId,
      name: 'Leo',
      age_label: 'Age 7',
      focus: 'Bilingual assist with predictable pacing',
      weekly_goal: '3 sessions plus 2 calm replays',
      current_package_id: packageLibrary.bridgeWords.package_id,
    },
  ],
  weekly_plan: [
    {
      day: 'Monday',
      mode: 'Co-reading',
      package_id: packageLibrary.friendshipTrail.package_id,
      objective: 'Warm start for the week with one caregiver prompt per page.',
    },
    {
      day: 'Wednesday',
      mode: 'Wind-down',
      package_id: packageLibrary.moonGarden.package_id,
      objective:
        'Use read-to-me mode with low stimulation and a slower page cadence.',
    },
    {
      day: 'Saturday',
      mode: 'Bilingual assist',
      package_id: packageLibrary.bridgeWords.package_id,
      objective:
        'Reveal only three translation words and track the replay count.',
    },
  ],
  progress_metrics: {
    completed_sessions: recentEvents.filter(
      event => event.event_type === 'session_completed'
    ).length,
    translation_reveals: recentEvents.filter(
      event => event.event_type === 'word_revealed_translation'
    ).length,
    audio_replays: recentEvents.filter(
      event => event.event_type === 'page_replayed_audio'
    ).length,
  },
  generated_at: '2026-03-17T12:00:00Z',
};

export function buildPackageMap(
  dashboard: CaregiverDashboardV1
): Record<string, StoryPackageManifestV1> {
  return dashboard.package_queue.reduce<Record<string, StoryPackageManifestV1>>(
    (accumulator, item) => {
      accumulator[item.package_id] = item;
      return accumulator;
    },
    {}
  );
}

export function resolveFeaturedPackage(
  dashboard: CaregiverDashboardV1
): StoryPackageManifestV1 {
  const packageMap = buildPackageMap(dashboard);
  return (
    packageMap[dashboard.featured_package_id] ?? dashboard.package_queue[0]
  );
}

export function resolveChildren(
  dashboard: CaregiverDashboardV1
): ResolvedChildSnapshot[] {
  const packageMap = buildPackageMap(dashboard);

  return dashboard.children.map(child => ({
    ...child,
    currentPackage:
      packageMap[child.current_package_id] ??
      dashboard.package_queue.find(
        candidate => candidate.package_id === child.current_package_id
      ) ??
      dashboard.package_queue[0],
  }));
}

export function resolveWeeklyPlan(
  dashboard: CaregiverDashboardV1
): ResolvedWeeklyPlanItem[] {
  const packageMap = buildPackageMap(dashboard);

  return dashboard.weekly_plan.map(item => ({
    ...item,
    package:
      packageMap[item.package_id] ??
      dashboard.package_queue.find(
        candidate => candidate.package_id === item.package_id
      ) ??
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
  children: resolveChildren(
    fallbackCaregiverDashboard
  ).map<CaregiverChildAssignmentV1>(child => ({
    child_id: child.child_id,
    name: child.name,
    age_label: child.age_label,
    focus: child.focus,
    weekly_goal: child.weekly_goal,
    current_package_id: child.current_package_id,
    current_package: child.currentPackage,
  })),
  planned_session_count: fallbackCaregiverDashboard.weekly_plan.length,
  generated_at: fallbackCaregiverDashboard.generated_at,
};

export const fallbackCaregiverPlan: CaregiverPlanV1 = {
  schema_version: CAREGIVER_PLAN_SCHEMA_VERSION,
  household_id: fallbackCaregiverDashboard.household_id,
  package_queue: fallbackCaregiverDashboard.package_queue,
  weekly_plan: resolveWeeklyPlan(
    fallbackCaregiverDashboard
  ).map<CaregiverPlannedSessionV1>(item => ({
    day: item.day,
    mode: item.mode,
    package_id: item.package_id,
    objective: item.objective,
    package: item.package,
  })),
  generated_at: fallbackCaregiverDashboard.generated_at,
};

export const fallbackCaregiverProgress: CaregiverProgressV1 = {
  schema_version: CAREGIVER_PROGRESS_SCHEMA_VERSION,
  household_id: fallbackCaregiverDashboard.household_id,
  recent_events:
    fallbackCaregiverDashboard.recent_events.map<CaregiverProgressEventV1>(
      event => ({
        event,
        child_name:
          fallbackCaregiverDashboard.children.find(
            child => child.child_id === event.child_id
          )?.name ?? event.child_id,
        package_title:
          fallbackCaregiverDashboard.package_queue.find(
            storyPackage => storyPackage.package_id === event.package_id
          )?.title ?? event.package_id,
      })
    ),
  progress_metrics: fallbackCaregiverDashboard.progress_metrics,
  generated_at: fallbackCaregiverDashboard.generated_at,
};

export const fallbackChildHome: ChildHomeV1 = {
  schema_version: CHILD_HOME_SCHEMA_VERSION,
  child_id: demoChildId,
  household_id: demoHouseholdId,
  child_name: 'Mina',
  focus: 'Shared reading and early vocabulary',
  weekly_goal: '4 completed sessions',
  featured_package_id: demoStoryPackage.package_id,
  current_package_id: demoStoryPackage.package_id,
  package_queue: [...demoPackageQueue],
  support_mode_defaults: ['read_aloud_sync', 'focus_support'],
  generated_at: fallbackCaregiverDashboard.generated_at,
};

export type DemoChildHomeOptions = {
  childId?: string;
  householdId?: string;
  packageId?: string;
  generatedAt?: string;
};

export function buildDemoChildHome(
  options: DemoChildHomeOptions = {}
): ChildHomeV1 {
  const childId = options.childId ?? demoChildId;
  const packageId = options.packageId ?? demoStoryPackageId;
  const currentPackage =
    demoPackageQueue.find(item => item.package_id === packageId) ??
    demoStoryPackage;

  return {
    ...fallbackChildHome,
    child_id: childId,
    household_id: options.householdId ?? demoHouseholdId,
    featured_package_id: currentPackage.package_id,
    current_package_id: currentPackage.package_id,
    package_queue: [
      currentPackage,
      ...demoPackageQueue.filter(
        item => item.package_id !== currentPackage.package_id
      ),
    ],
    generated_at: options.generatedAt ?? fallbackCaregiverDashboard.generated_at,
  };
}

export const fallbackHouseholdOverview = buildHouseholdOverview(
  fallbackCaregiverHousehold
);
export const fallbackChildDomainView = buildChildDomainView(
  fallbackCaregiverChildren
);
export const fallbackPlanDomainView = buildPlanDomainView(
  fallbackCaregiverPlan
);
export const fallbackProgressDomainView = buildProgressDomainView(
  fallbackCaregiverProgress
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
  options: DemoReadingSessionPayloadOptions = {}
): ReadingSessionCreateV2 {
  const packageId = options.packageId ?? demoStoryPackageId;

  return {
    child_id: options.childId ?? demoChildId,
    package_id: packageId,
    started_at: options.startedAt ?? new Date().toISOString(),
    mode: options.mode ?? 'read_to_me',
    language_mode:
      options.languageMode ?? resolveDemoPackageLanguageMode(packageId),
    assist_mode: options.assistMode ?? ['read_aloud_sync'],
  };
}

export type DemoReadingSessionResponseOptions = {
  sessionId?: string;
  childId?: string;
  packageId?: string;
  acceptedAt?: string;
};

export function buildDemoReadingSessionResponse(
  options: DemoReadingSessionResponseOptions = {}
): ReadingSessionResponseV2 {
  return {
    session_id: options.sessionId ?? demoReadingSessionId,
    status: 'accepted',
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
  options: DemoReadingEventBatchRequestOptions = {}
): ReadingEventBatchRequestV2 {
  const childId = options.childId ?? demoChildId;
  const packageId = options.packageId ?? demoStoryPackageId;
  const sessionId = options.sessionId ?? demoReadingSessionId;
  const occurredAt = options.occurredAt ?? new Date().toISOString();
  const appVersion = options.appVersion ?? '2.0.0';
  const languageMode =
    options.languageMode ?? resolveDemoPackageLanguageMode(packageId);

  return {
    events: [
      {
        schema_version: READING_EVENT_SCHEMA_VERSION,
        event_id: 'c1d3a8c0-05f3-45bd-9a56-72a911200101',
        event_type: 'session_started',
        occurred_at: occurredAt,
        session_id: sessionId,
        child_id: childId,
        package_id: packageId,
        page_index: null,
        platform: 'ipadOS',
        surface: 'child-app',
        app_version: appVersion,
        language_mode: languageMode,
        payload: {
          source: 'api-workbench',
        },
      },
      {
        schema_version: READING_EVENT_SCHEMA_VERSION,
        event_id: 'c1d3a8c0-05f3-45bd-9a56-72a911200102',
        event_type: 'page_viewed',
        occurred_at: occurredAt,
        session_id: sessionId,
        child_id: childId,
        package_id: packageId,
        page_index: 0,
        platform: 'ipadOS',
        surface: 'child-app',
        app_version: appVersion,
        language_mode: languageMode,
        payload: {
          dwell_ms: 18000,
          source: 'api-workbench',
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
  options: DemoReadingEventIngestedResponseOptions = {}
): ReadingEventIngestedResponseV2 {
  return {
    status: 'accepted',
    accepted_count: options.acceptedCount ?? 2,
    accepted_at: options.acceptedAt ?? demoAcceptedAt,
    session_ids: options.sessionIds ?? [demoReadingSessionId],
  };
}

export type DemoCaregiverAssignmentCommandOptions = {
  householdId?: string;
  childId?: string;
  packageId?: string;
  requestedAt?: string;
  source?: CaregiverAssignmentCommandV1['source'];
};

export function buildDemoCaregiverAssignmentCommand(
  options: DemoCaregiverAssignmentCommandOptions = {}
): CaregiverAssignmentCommandV1 {
  return {
    schema_version: CAREGIVER_ASSIGNMENT_COMMAND_SCHEMA_VERSION,
    household_id: options.householdId ?? demoHouseholdId,
    child_id: options.childId ?? demoChildId,
    package_id: options.packageId ?? demoStoryPackageId,
    source: options.source ?? 'caregiver-web',
    requested_at: options.requestedAt ?? demoAcceptedAt,
  };
}

export type DemoCaregiverAssignmentResponseOptions = {
  householdId?: string;
  childId?: string;
  packageId?: string;
  previousPackageId?: string;
  acceptedAt?: string;
};

export function buildDemoCaregiverAssignmentResponse(
  options: DemoCaregiverAssignmentResponseOptions = {}
): CaregiverAssignmentResponseV1 {
  const householdId = options.householdId ?? demoHouseholdId;
  const childId = options.childId ?? demoChildId;
  const packageId = options.packageId ?? demoStoryPackageId;
  const currentPackage =
    demoPackageQueue.find(storyPackage => storyPackage.package_id === packageId) ??
    demoStoryPackage;

  return {
    schema_version: CAREGIVER_ASSIGNMENT_RESPONSE_SCHEMA_VERSION,
    status: 'accepted',
    household_id: householdId,
    child_id: childId,
    previous_package_id: options.previousPackageId ?? demoStoryPackageId,
    current_package_id: currentPackage.package_id,
    current_package: currentPackage,
    child_home: buildDemoChildHome({
      childId,
      householdId,
      packageId: currentPackage.package_id,
      generatedAt: options.acceptedAt ?? demoAcceptedAt,
    }),
    accepted_at: options.acceptedAt ?? demoAcceptedAt,
  };
}
