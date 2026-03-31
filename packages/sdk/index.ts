import type {
  ChildHomeV1,
  CaregiverAssignmentCommandV1,
  CaregiverAssignmentResponseV1,
  CaregiverChildrenV1,
  CaregiverDashboardV1,
  CaregiverHouseholdV1,
  CaregiverPlanV1,
  CaregiverProgressV1,
  HouseholdEntitlementV1,
  OpsMetricsSnapshotV1,
  ReadingEventBatchRequestV2,
  ReadingEventIngestedResponseV2,
  ReadingSessionCreateV2,
  ReadingSessionResponseV2,
  StoryBriefCommandV1,
  StoryBriefIndexV1,
  StoryBriefV1,
  StoryGenerationJobCommandV1,
  StoryGenerationJobIndexV1,
  StoryGenerationJobV1,
  StoryPackageBuildCommandV1,
  StoryPackageBuildV1,
  StoryPackageDraftIndexV1,
  StoryPackageDraftV1,
  StoryPackageHistoryV1,
  StoryPackageRecallCommandV1,
  StoryPackageReviewCommandV1,
  StoryPackageReleaseCommandV1,
  StoryPackageReleaseV1,
  StoryPackageRollbackCommandV1,
  StoryPackageManifestV1,
  WeeklyValueReportV1,
} from "@lumosreading/contracts";

export * from "./caregiver";
export * from "./demo";
export * from "./generation";
export * from "./monetization";
export * from "./object-storage";
export * from "./application";
export * from "./release";

export const DEFAULT_LUMOS_API_BASE_URL = "http://localhost:8000/api/v2";

type FetchLike = (input: string, init?: RequestInit) => Promise<Response>;

export type LumosApiClientOptions = {
  baseUrl?: string;
  fetch?: FetchLike;
  headers?: HeadersInit;
};

export class LumosApiError extends Error {
  readonly body: string;
  readonly path: string;
  readonly status: number;

  constructor(args: { status: number; path: string; body: string }) {
    super(`Lumos API ${args.status} for ${args.path}: ${args.body || "Unexpected error"}`);
    this.name = "LumosApiError";
    this.status = args.status;
    this.path = args.path;
    this.body = args.body;
  }
}

function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.replace(/\/+$/, "");
}

async function request<T>(
  fetchImpl: FetchLike,
  baseUrl: string,
  path: string,
  defaultHeaders?: HeadersInit,
  init?: RequestInit,
): Promise<T> {
  const headers = new Headers(defaultHeaders);
  headers.set("Accept", "application/json");

  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (init?.headers) {
    const initHeaders = new Headers(init.headers);
    initHeaders.forEach((value, key) => {
      headers.set(key, value);
    });
  }

  const response = await fetchImpl(`${baseUrl}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    throw new LumosApiError({
      status: response.status,
      path,
      body: await response.text(),
    });
  }

  return (await response.json()) as T;
}

export function createLumosApiClient(options: LumosApiClientOptions = {}) {
  const fetchImpl = options.fetch ?? fetch;
  const baseUrl = normalizeBaseUrl(options.baseUrl ?? DEFAULT_LUMOS_API_BASE_URL);

  return {
    baseUrl,
    async getCaregiverHousehold(householdId: string): Promise<CaregiverHouseholdV1> {
      return request<CaregiverHouseholdV1>(
        fetchImpl,
        baseUrl,
        `/caregiver/households/${householdId}`,
        options.headers,
      );
    },
    async getCaregiverChildren(householdId: string): Promise<CaregiverChildrenV1> {
      return request<CaregiverChildrenV1>(
        fetchImpl,
        baseUrl,
        `/caregiver/households/${householdId}/children`,
        options.headers,
      );
    },
    async assignCaregiverPackage(
      payload: CaregiverAssignmentCommandV1,
    ): Promise<CaregiverAssignmentResponseV1> {
      return request<CaregiverAssignmentResponseV1>(
        fetchImpl,
        baseUrl,
        `/caregiver/households/${payload.household_id}/children/${payload.child_id}/assignment`,
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async getCaregiverPlan(householdId: string): Promise<CaregiverPlanV1> {
      return request<CaregiverPlanV1>(
        fetchImpl,
        baseUrl,
        `/caregiver/households/${householdId}/plan`,
        options.headers,
      );
    },
    async getCaregiverProgress(householdId: string): Promise<CaregiverProgressV1> {
      return request<CaregiverProgressV1>(
        fetchImpl,
        baseUrl,
        `/caregiver/households/${householdId}/progress`,
        options.headers,
      );
    },
    async getCaregiverDashboard(householdId: string): Promise<CaregiverDashboardV1> {
      return request<CaregiverDashboardV1>(
        fetchImpl,
        baseUrl,
        `/caregiver/households/${householdId}/dashboard`,
        options.headers,
      );
    },
    async getHouseholdEntitlement(householdId: string): Promise<HouseholdEntitlementV1> {
      return request<HouseholdEntitlementV1>(
        fetchImpl,
        baseUrl,
        `/caregiver/households/${householdId}/entitlement`,
        options.headers,
      );
    },
    async getWeeklyValueReport(householdId: string): Promise<WeeklyValueReportV1> {
      return request<WeeklyValueReportV1>(
        fetchImpl,
        baseUrl,
        `/caregiver/households/${householdId}/weekly-value`,
        options.headers,
      );
    },
    async getOpsMetricsSnapshot(): Promise<OpsMetricsSnapshotV1> {
      return request<OpsMetricsSnapshotV1>(
        fetchImpl,
        baseUrl,
        "/ops/metrics",
        options.headers,
      );
    },
    async getChildHome(childId: string): Promise<ChildHomeV1> {
      return request<ChildHomeV1>(
        fetchImpl,
        baseUrl,
        `/child-home/${childId}`,
        options.headers,
      );
    },
    async getChildScopedStoryPackage(
      childId: string,
      packageId: string,
    ): Promise<StoryPackageManifestV1> {
      return request<StoryPackageManifestV1>(
        fetchImpl,
        baseUrl,
        `/child-home/${childId}/packages/${packageId}`,
        options.headers,
      );
    },
    async getStoryPackage(packageId: string): Promise<StoryPackageManifestV1> {
      return request<StoryPackageManifestV1>(
        fetchImpl,
        baseUrl,
        `/story-packages/${packageId}`,
        options.headers,
      );
    },
    async listStoryPackageDrafts(): Promise<StoryPackageDraftIndexV1> {
      return request<StoryPackageDraftIndexV1>(
        fetchImpl,
        baseUrl,
        "/story-packages",
        options.headers,
      );
    },
    async getStoryPackageHistory(packageId: string): Promise<StoryPackageHistoryV1> {
      return request<StoryPackageHistoryV1>(
        fetchImpl,
        baseUrl,
        `/story-packages/${packageId}/history`,
        options.headers,
      );
    },
    async triggerStoryPackageBuild(
      packageId: string,
      payload: StoryPackageBuildCommandV1,
    ): Promise<StoryPackageBuildV1> {
      return request<StoryPackageBuildV1>(
        fetchImpl,
        baseUrl,
        `/story-packages/${packageId}:build`,
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async releaseStoryPackageBuild(
      packageId: string,
      payload: StoryPackageReleaseCommandV1,
    ): Promise<StoryPackageReleaseV1> {
      return request<StoryPackageReleaseV1>(
        fetchImpl,
        baseUrl,
        `/story-packages/${packageId}:release`,
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async recallStoryPackageRelease(
      packageId: string,
      payload: StoryPackageRecallCommandV1,
    ): Promise<StoryPackageReleaseV1> {
      return request<StoryPackageReleaseV1>(
        fetchImpl,
        baseUrl,
        `/story-packages/${packageId}:recall`,
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async rollbackStoryPackageRelease(
      packageId: string,
      payload: StoryPackageRollbackCommandV1,
    ): Promise<StoryPackageReleaseV1> {
      return request<StoryPackageReleaseV1>(
        fetchImpl,
        baseUrl,
        `/story-packages/${packageId}:rollback`,
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async reviewStoryPackage(
      packageId: string,
      payload: StoryPackageReviewCommandV1,
    ): Promise<StoryPackageDraftV1> {
      return request<StoryPackageDraftV1>(
        fetchImpl,
        baseUrl,
        `/story-packages/${packageId}:review`,
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async listStoryBriefs(): Promise<StoryBriefIndexV1> {
      return request<StoryBriefIndexV1>(
        fetchImpl,
        baseUrl,
        "/story-briefs",
        options.headers,
      );
    },
    async createStoryBrief(payload: StoryBriefCommandV1): Promise<StoryBriefV1> {
      return request<StoryBriefV1>(
        fetchImpl,
        baseUrl,
        "/story-briefs",
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async generateStoryBriefDraft(
      briefId: string,
      payload: StoryGenerationJobCommandV1,
    ): Promise<StoryGenerationJobV1> {
      return request<StoryGenerationJobV1>(
        fetchImpl,
        baseUrl,
        `/story-briefs/${briefId}:generate-draft`,
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async generateStoryBriefMedia(
      briefId: string,
      payload: StoryGenerationJobCommandV1,
    ): Promise<StoryGenerationJobV1> {
      return request<StoryGenerationJobV1>(
        fetchImpl,
        baseUrl,
        `/story-briefs/${briefId}:generate-media`,
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async listStoryGenerationJobs(): Promise<StoryGenerationJobIndexV1> {
      return request<StoryGenerationJobIndexV1>(
        fetchImpl,
        baseUrl,
        "/story-generation-jobs",
        options.headers,
      );
    },
    async createReadingSession(
      payload: ReadingSessionCreateV2,
    ): Promise<ReadingSessionResponseV2> {
      return request<ReadingSessionResponseV2>(
        fetchImpl,
        baseUrl,
        "/reading-sessions",
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
    async ingestReadingEvents(
      payload: ReadingEventBatchRequestV2,
    ): Promise<ReadingEventIngestedResponseV2> {
      return request<ReadingEventIngestedResponseV2>(
        fetchImpl,
        baseUrl,
        "/reading-events:batch",
        options.headers,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );
    },
  };
}

export type LumosApiClient = ReturnType<typeof createLumosApiClient>;
