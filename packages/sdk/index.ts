import type {
  CaregiverChildrenV1,
  CaregiverDashboardV1,
  CaregiverHouseholdV1,
  CaregiverPlanV1,
  CaregiverProgressV1,
  ReadingEventBatchRequestV2,
  ReadingEventIngestedResponseV2,
  ReadingSessionCreateV2,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from "@lumosreading/contracts";

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
    async getStoryPackage(packageId: string): Promise<StoryPackageManifestV1> {
      return request<StoryPackageManifestV1>(
        fetchImpl,
        baseUrl,
        `/story-packages/${packageId}`,
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
