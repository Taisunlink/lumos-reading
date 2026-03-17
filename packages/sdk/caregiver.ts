import type {
  CaregiverChildrenV1,
  CaregiverHouseholdV1,
  CaregiverPlanV1,
  CaregiverProgressV1,
  ReadingEventV1,
  StoryPackageManifestV1,
} from "@lumosreading/contracts";

function formatMinutesFromMs(milliseconds: number): string {
  const minutes = Math.max(1, Math.round(milliseconds / 60000));
  return `${minutes} min`;
}

export interface CaregiverReadModelClient {
  getCaregiverHousehold(householdId: string): Promise<CaregiverHouseholdV1>;
  getCaregiverChildren(householdId: string): Promise<CaregiverChildrenV1>;
  getCaregiverPlan(householdId: string): Promise<CaregiverPlanV1>;
  getCaregiverProgress(householdId: string): Promise<CaregiverProgressV1>;
}

export type HouseholdOverview = {
  schemaVersion: CaregiverHouseholdV1["schema_version"];
  householdId: string;
  householdName: string;
  featuredPackageId: string;
  featuredPackage: StoryPackageManifestV1;
  packageQueue: StoryPackageManifestV1[];
  childCount: number;
  packageCount: number;
  completedSessions: number;
  translationReveals: number;
  audioReplays: number;
  generatedAt: string;
};

export type ChildAssignment = {
  childId: string;
  name: string;
  ageLabel: string;
  focus: string;
  weeklyGoal: string;
  currentPackageId: string;
  currentPackage: StoryPackageManifestV1;
};

export type ChildSupportSignal = {
  childId: string;
  name: string;
  focus: string;
  ageBand: string;
  releaseChannel: string;
  reviewStatus: string;
};

export type ChildDomainView = {
  schemaVersion: CaregiverChildrenV1["schema_version"];
  householdId: string;
  children: ChildAssignment[];
  supportSignals: ChildSupportSignal[];
  bilingualAssignments: number;
  plannedSessions: number;
  generatedAt: string;
};

export type PlannedSession = {
  day: string;
  mode: string;
  objective: string;
  packageId: string;
  package: StoryPackageManifestV1;
};

export type PlanDomainView = {
  schemaVersion: CaregiverPlanV1["schema_version"];
  householdId: string;
  sessions: PlannedSession[];
  packageQueue: StoryPackageManifestV1[];
  weeklySessions: number;
  totalPlannedMinutes: number;
  scheduledPackageCoverage: number;
  generatedAt: string;
};

export type ProgressTimelineEntry = {
  eventId: string;
  eventType: string;
  occurredAt: string;
  childName: string;
  packageTitle: string;
  surface: string;
  description: string;
};

export type ProgressDomainView = {
  schemaVersion: CaregiverProgressV1["schema_version"];
  householdId: string;
  trackedEvents: number;
  uniqueSessions: number;
  totalDwellMs: number;
  completedSessions: number;
  translationReveals: number;
  audioReplays: number;
  timeline: ProgressTimelineEntry[];
  eventCoverage: Array<{ eventType: string; count: number }>;
  generatedAt: string;
};

export interface CaregiverHouseholdService {
  getOverview(householdId: string): Promise<HouseholdOverview>;
}

export interface CaregiverChildrenService {
  getAssignments(householdId: string): Promise<ChildDomainView>;
}

export interface CaregiverPlanService {
  getWeeklyPlan(householdId: string): Promise<PlanDomainView>;
}

export interface CaregiverProgressService {
  getInsights(householdId: string): Promise<ProgressDomainView>;
}

export interface CaregiverSubdomainServices {
  household: CaregiverHouseholdService;
  children: CaregiverChildrenService;
  plan: CaregiverPlanService;
  progress: CaregiverProgressService;
}

export function buildHouseholdOverview(household: CaregiverHouseholdV1): HouseholdOverview {
  return {
    schemaVersion: household.schema_version,
    householdId: household.household_id,
    householdName: household.household_name,
    featuredPackageId: household.featured_package_id,
    featuredPackage: household.featured_package,
    packageQueue: household.package_queue,
    childCount: household.child_count,
    packageCount: household.package_queue.length,
    completedSessions: household.progress_metrics.completed_sessions,
    translationReveals: household.progress_metrics.translation_reveals,
    audioReplays: household.progress_metrics.audio_replays,
    generatedAt: household.generated_at,
  };
}

export function buildChildDomainView(childrenResource: CaregiverChildrenV1): ChildDomainView {
  const children = childrenResource.children.map((child) => ({
    childId: child.child_id,
    name: child.name,
    ageLabel: child.age_label,
    focus: child.focus,
    weeklyGoal: child.weekly_goal,
    currentPackageId: child.current_package_id,
    currentPackage: child.current_package,
  }));

  return {
    schemaVersion: childrenResource.schema_version,
    householdId: childrenResource.household_id,
    children,
    supportSignals: children.map((child) => ({
      childId: child.childId,
      name: child.name,
      focus: child.focus,
      ageBand: child.currentPackage.age_band,
      releaseChannel: child.currentPackage.release_channel,
      reviewStatus: child.currentPackage.safety.review_status,
    })),
    bilingualAssignments: children.filter((child) =>
      child.currentPackage.tags?.includes("bilingual-assist"),
    ).length,
    plannedSessions: childrenResource.planned_session_count,
    generatedAt: childrenResource.generated_at,
  };
}

export function buildPlanDomainView(planResource: CaregiverPlanV1): PlanDomainView {
  const sessions = planResource.weekly_plan.map((item) => ({
    day: item.day,
    mode: item.mode,
    objective: item.objective,
    packageId: item.package_id,
    package: item.package,
  }));

  return {
    schemaVersion: planResource.schema_version,
    householdId: planResource.household_id,
    sessions,
    packageQueue: planResource.package_queue,
    weeklySessions: sessions.length,
    totalPlannedMinutes: sessions.reduce(
      (sum, item) => sum + Math.max(1, Math.round(item.package.estimated_duration_sec / 60)),
      0,
    ),
    scheduledPackageCoverage: new Set(sessions.map((item) => item.package.package_id)).size,
    generatedAt: planResource.generated_at,
  };
}

function getNumericPayloadField(event: ReadingEventV1, field: string): number | null {
  const value = event.payload[field];
  return typeof value === "number" ? value : null;
}

function getStringPayloadField(event: ReadingEventV1, field: string): string | null {
  const value = event.payload[field];
  return typeof value === "string" ? value : null;
}

function describeEvent(event: ReadingEventV1): string {
  if (event.event_type === "session_completed") {
    const dwellMs = getNumericPayloadField(event, "dwell_ms");
    return dwellMs === null
      ? "Completed session with no dwell payload."
      : `Completed in ${formatMinutesFromMs(dwellMs)}.`;
  }

  if (event.event_type === "word_revealed_translation") {
    const word = getStringPayloadField(event, "word") ?? "Unknown word";
    const revealCount = getNumericPayloadField(event, "reveal_count") ?? 0;
    return `${word} translation revealed ${revealCount} time(s).`;
  }

  if (event.event_type === "page_replayed_audio") {
    const replayCount = getNumericPayloadField(event, "replay_count") ?? 0;
    return `Audio replayed ${replayCount} time(s) on the same page.`;
  }

  if (event.event_type === "assist_mode_enabled") {
    const assistMode = getStringPayloadField(event, "assist_mode") ?? "unknown";
    return `Assist mode enabled: ${assistMode}.`;
  }

  return "Typed reading event recorded.";
}

export function buildProgressDomainView(progressResource: CaregiverProgressV1): ProgressDomainView {
  const eventTypeCounts = progressResource.recent_events.reduce<Record<string, number>>(
    (accumulator, entry) => {
      accumulator[entry.event.event_type] = (accumulator[entry.event.event_type] ?? 0) + 1;
      return accumulator;
    },
    {},
  );

  return {
    schemaVersion: progressResource.schema_version,
    householdId: progressResource.household_id,
    trackedEvents: progressResource.recent_events.length,
    uniqueSessions: new Set(progressResource.recent_events.map((entry) => entry.event.session_id))
      .size,
    totalDwellMs: progressResource.recent_events.reduce(
      (sum, entry) => sum + (getNumericPayloadField(entry.event, "dwell_ms") ?? 0),
      0,
    ),
    completedSessions: progressResource.progress_metrics.completed_sessions,
    translationReveals: progressResource.progress_metrics.translation_reveals,
    audioReplays: progressResource.progress_metrics.audio_replays,
    timeline: progressResource.recent_events.map((entry) => ({
      eventId: entry.event.event_id,
      eventType: entry.event.event_type,
      occurredAt: entry.event.occurred_at,
      childName: entry.child_name,
      packageTitle: entry.package_title,
      surface: entry.event.surface,
      description: describeEvent(entry.event),
    })),
    eventCoverage: Object.entries(eventTypeCounts)
      .sort((left, right) => right[1] - left[1])
      .map(([eventType, count]) => ({ eventType, count })),
    generatedAt: progressResource.generated_at,
  };
}

export function createCaregiverSubdomainServices(
  client: CaregiverReadModelClient,
): CaregiverSubdomainServices {
  return {
    household: {
      async getOverview(householdId: string) {
        return buildHouseholdOverview(await client.getCaregiverHousehold(householdId));
      },
    },
    children: {
      async getAssignments(householdId: string) {
        return buildChildDomainView(await client.getCaregiverChildren(householdId));
      },
    },
    plan: {
      async getWeeklyPlan(householdId: string) {
        return buildPlanDomainView(await client.getCaregiverPlan(householdId));
      },
    },
    progress: {
      async getInsights(householdId: string) {
        return buildProgressDomainView(await client.getCaregiverProgress(householdId));
      },
    },
  };
}
