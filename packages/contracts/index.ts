import caregiverDashboardSchema from "./schemas/caregiver-dashboard.v1.schema.json";
import caregiverChildrenSchema from "./schemas/caregiver-children.v1.schema.json";
import caregiverHouseholdSchema from "./schemas/caregiver-household.v1.schema.json";
import caregiverPlanSchema from "./schemas/caregiver-plan.v1.schema.json";
import caregiverProgressSchema from "./schemas/caregiver-progress.v1.schema.json";
import childHomeSchema from "./schemas/child-home.v1.schema.json";
import readingEventBatchSchema from "./schemas/reading-event-batch.v2.schema.json";
import readingEventIngestedResponseSchema from "./schemas/reading-event-ingested-response.v2.schema.json";
import readingEventSchema from "./schemas/reading-event.v1.schema.json";
import readingSessionCreateSchema from "./schemas/reading-session-create.v2.schema.json";
import readingSessionResponseSchema from "./schemas/reading-session-response.v2.schema.json";
import safetyAuditSchema from "./schemas/safety-audit.v1.schema.json";
import storyPackageSchema from "./schemas/story-package.v1.schema.json";

export const CAREGIVER_DASHBOARD_SCHEMA_VERSION = "caregiver-dashboard.v1" as const;
export const CAREGIVER_HOUSEHOLD_SCHEMA_VERSION = "caregiver-household.v1" as const;
export const CAREGIVER_CHILDREN_SCHEMA_VERSION = "caregiver-children.v1" as const;
export const CAREGIVER_PLAN_SCHEMA_VERSION = "caregiver-plan.v1" as const;
export const CAREGIVER_PROGRESS_SCHEMA_VERSION = "caregiver-progress.v1" as const;
export const CHILD_HOME_SCHEMA_VERSION = "child-home.v1" as const;
export const STORY_PACKAGE_SCHEMA_VERSION = "story-package.v1" as const;
export const READING_EVENT_SCHEMA_VERSION = "reading-event.v1" as const;
export const READING_SESSION_CREATE_SCHEMA_VERSION = "reading-session-create.v2" as const;
export const READING_SESSION_RESPONSE_SCHEMA_VERSION = "reading-session-response.v2" as const;
export const READING_EVENT_BATCH_SCHEMA_VERSION = "reading-event-batch.v2" as const;
export const READING_EVENT_INGESTED_RESPONSE_SCHEMA_VERSION =
  "reading-event-ingested-response.v2" as const;
export const SAFETY_AUDIT_SCHEMA_VERSION = "safety-audit.v1" as const;

export const caregiverDashboardV1Schema = caregiverDashboardSchema;
export const caregiverHouseholdV1Schema = caregiverHouseholdSchema;
export const caregiverChildrenV1Schema = caregiverChildrenSchema;
export const caregiverPlanV1Schema = caregiverPlanSchema;
export const caregiverProgressV1Schema = caregiverProgressSchema;
export const childHomeV1Schema = childHomeSchema;
export const storyPackageV1Schema = storyPackageSchema;
export const readingEventV1Schema = readingEventSchema;
export const readingSessionCreateV2Schema = readingSessionCreateSchema;
export const readingSessionResponseV2Schema = readingSessionResponseSchema;
export const readingEventBatchV2Schema = readingEventBatchSchema;
export const readingEventIngestedResponseV2Schema = readingEventIngestedResponseSchema;
export const safetyAuditV1Schema = safetyAuditSchema;

export type LanguageTag = string;
export type Surface = "child-app" | "caregiver-web" | "studio-web";
export type Platform = "ipadOS" | "ios" | "android" | "web" | "desktop-web" | "unknown";

export type ReleaseChannel = "general" | "pilot" | "experimental" | "internal";
export type StoryPackageReviewStatus = "approved" | "limited_release" | "recalled";

export interface StoryPackageSafetyV1 {
  review_status: StoryPackageReviewStatus;
  reviewed_at?: string | null;
  review_policy_version?: string;
}

export interface StoryPackageTextRunV1 {
  text: string;
  lang: LanguageTag;
  tts_timing?: number[];
}

export interface StoryPackageMediaV1 {
  image_url?: string;
  audio_url?: string;
  thumbnail_url?: string;
}

export interface StoryPackageOverlayV1 {
  vocabulary?: string[];
  caregiver_prompt_ids?: string[];
  interaction_ids?: string[];
}

export interface StoryPackagePageV1 {
  page_index: number;
  text_runs: StoryPackageTextRunV1[];
  media?: StoryPackageMediaV1;
  overlays?: StoryPackageOverlayV1;
}

export interface StoryPackageManifestV1 {
  schema_version: typeof STORY_PACKAGE_SCHEMA_VERSION;
  package_id: string;
  story_master_id: string;
  story_variant_id: string;
  title: string;
  subtitle?: string;
  language_mode: LanguageTag;
  difficulty_level: string;
  age_band: string;
  estimated_duration_sec: number;
  release_channel: ReleaseChannel;
  cover_image_url?: string;
  tags?: string[];
  safety: StoryPackageSafetyV1;
  pages: StoryPackagePageV1[];
}

export type ReadingEventType =
  | "session_started"
  | "session_completed"
  | "page_viewed"
  | "page_replayed_audio"
  | "word_revealed_translation"
  | "caregiver_prompt_opened"
  | "caregiver_prompt_completed"
  | "mode_changed"
  | "assist_mode_enabled"
  | "content_reported";

export interface ReadingEventV1 {
  schema_version: typeof READING_EVENT_SCHEMA_VERSION;
  event_id: string;
  event_type: ReadingEventType;
  occurred_at: string;
  session_id: string;
  child_id: string;
  package_id: string;
  page_index?: number | null;
  platform: Platform;
  surface: Surface;
  app_version: string;
  language_mode?: LanguageTag;
  payload: Record<string, unknown>;
}

export interface CaregiverChildSummaryV1 {
  child_id: string;
  name: string;
  age_label: string;
  focus: string;
  weekly_goal: string;
  current_package_id: string;
}

export interface CaregiverWeeklyPlanItemV1 {
  day: string;
  mode: string;
  package_id: string;
  objective: string;
}

export interface CaregiverProgressMetricsV1 {
  completed_sessions: number;
  translation_reveals: number;
  audio_replays: number;
}

export interface CaregiverChildAssignmentV1 extends CaregiverChildSummaryV1 {
  current_package: StoryPackageManifestV1;
}

export interface CaregiverPlannedSessionV1 extends CaregiverWeeklyPlanItemV1 {
  package: StoryPackageManifestV1;
}

export interface CaregiverProgressEventV1 {
  event: ReadingEventV1;
  child_name: string;
  package_title: string;
}

export interface CaregiverHouseholdV1 {
  schema_version: typeof CAREGIVER_HOUSEHOLD_SCHEMA_VERSION;
  household_id: string;
  household_name: string;
  featured_package_id: string;
  featured_package: StoryPackageManifestV1;
  package_queue: StoryPackageManifestV1[];
  child_count: number;
  progress_metrics: CaregiverProgressMetricsV1;
  generated_at: string;
}

export interface CaregiverChildrenV1 {
  schema_version: typeof CAREGIVER_CHILDREN_SCHEMA_VERSION;
  household_id: string;
  children: CaregiverChildAssignmentV1[];
  planned_session_count: number;
  generated_at: string;
}

export interface CaregiverPlanV1 {
  schema_version: typeof CAREGIVER_PLAN_SCHEMA_VERSION;
  household_id: string;
  package_queue: StoryPackageManifestV1[];
  weekly_plan: CaregiverPlannedSessionV1[];
  generated_at: string;
}

export interface CaregiverProgressV1 {
  schema_version: typeof CAREGIVER_PROGRESS_SCHEMA_VERSION;
  household_id: string;
  recent_events: CaregiverProgressEventV1[];
  progress_metrics: CaregiverProgressMetricsV1;
  generated_at: string;
}

export interface CaregiverDashboardV1 {
  schema_version: typeof CAREGIVER_DASHBOARD_SCHEMA_VERSION;
  household_id: string;
  household_name: string;
  featured_package_id: string;
  package_queue: StoryPackageManifestV1[];
  recent_events: ReadingEventV1[];
  children: CaregiverChildSummaryV1[];
  weekly_plan: CaregiverWeeklyPlanItemV1[];
  progress_metrics: CaregiverProgressMetricsV1;
  generated_at: string;
}

export interface ChildHomeV1 {
  schema_version: typeof CHILD_HOME_SCHEMA_VERSION;
  child_id: string;
  household_id: string;
  child_name: string;
  focus: string;
  weekly_goal: string;
  featured_package_id: string;
  current_package_id: string;
  package_queue: StoryPackageManifestV1[];
  support_mode_defaults: string[];
  generated_at: string;
}

export interface ReadingSessionCreateV2 {
  child_id: string;
  package_id: string;
  started_at: string;
  mode: string;
  language_mode: LanguageTag;
  assist_mode: string[];
}

export interface ReadingSessionResponseV2 {
  session_id: string;
  status: "accepted";
  accepted_at: string;
  child_id: string;
  package_id: string;
}

export interface ReadingEventBatchRequestV2 {
  events: ReadingEventV1[];
}

export interface ReadingEventIngestedResponseV2 {
  status: "accepted";
  accepted_count: number;
  accepted_at: string;
  session_ids: string[];
}

export type SafetyAuditTargetType =
  | "story_master"
  | "story_variant"
  | "story_package"
  | "user_report";

export type SafetyAuditSource =
  | "pre_release"
  | "post_release_report"
  | "scheduled_review"
  | "incident_response";

export type SafetyAuditStatus =
  | "pending"
  | "in_review"
  | "approved"
  | "needs_revision"
  | "rejected"
  | "recalled"
  | "escalated";

export type SafetySeverity = "low" | "medium" | "high" | "critical";
export type ReviewerType = "system" | "human" | "hybrid";
export type ResolutionAction = "none" | "revise" | "block" | "release" | "recall" | "escalate";

export interface SafetyAuditFindingV1 {
  code: string;
  title: string;
  description: string;
  severity: SafetySeverity;
  page_index?: number | null;
  action_required: boolean;
}

export interface SafetyAuditReviewerV1 {
  reviewer_type: ReviewerType;
  reviewer_id?: string | null;
}

export interface SafetyAuditResolutionV1 {
  action: ResolutionAction;
  notes?: string;
  resolved_at?: string | null;
}

export interface SafetyAuditV1 {
  schema_version: typeof SAFETY_AUDIT_SCHEMA_VERSION;
  audit_id: string;
  target_type: SafetyAuditTargetType;
  target_id: string;
  audit_source: SafetyAuditSource;
  audit_status: SafetyAuditStatus;
  severity: SafetySeverity;
  policy_version: string;
  findings: SafetyAuditFindingV1[];
  reviewer: SafetyAuditReviewerV1;
  created_at: string;
  reviewed_at?: string | null;
  resolution: SafetyAuditResolutionV1;
}
