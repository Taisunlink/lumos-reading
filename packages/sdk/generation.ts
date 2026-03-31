import type {
  StoryBriefCommandV1,
  StoryBriefIndexV1,
  StoryBriefV1,
  StoryGenerationJobCommandV1,
  StoryGenerationJobIndexV1,
  StoryGenerationJobV1,
} from "@lumosreading/contracts";

export interface StoryGenerationClient {
  listStoryBriefs(): Promise<StoryBriefIndexV1>;
  createStoryBrief(payload: StoryBriefCommandV1): Promise<StoryBriefV1>;
  generateStoryBriefDraft(
    briefId: string,
    payload: StoryGenerationJobCommandV1,
  ): Promise<StoryGenerationJobV1>;
  generateStoryBriefMedia(
    briefId: string,
    payload: StoryGenerationJobCommandV1,
  ): Promise<StoryGenerationJobV1>;
  listStoryGenerationJobs(): Promise<StoryGenerationJobIndexV1>;
}

export type StoryBriefCard = {
  briefId: string;
  packageId: string;
  title: string;
  theme: string;
  premise: string;
  languageMode: string;
  ageBand: string;
  desiredPageCount: number;
  status: string;
  latestJobId: string | null;
  latestFailureReason: string | null;
  updatedAt: string;
};

export type StoryGenerationJobCard = {
  jobId: string;
  briefId: string;
  packageId: string;
  jobType: string;
  status: string;
  selectedProvider: string | null;
  failureReason: string | null;
  generatedAssetCount: number;
  updatedAt: string;
};

export interface StoryGenerationServices {
  listBriefCards(): Promise<StoryBriefCard[]>;
  createBrief(payload: StoryBriefCommandV1): Promise<StoryBriefV1>;
  generateDraft(
    briefId: string,
    payload: StoryGenerationJobCommandV1,
  ): Promise<StoryGenerationJobV1>;
  generateMedia(
    briefId: string,
    payload: StoryGenerationJobCommandV1,
  ): Promise<StoryGenerationJobV1>;
  listJobCards(): Promise<StoryGenerationJobCard[]>;
}

export function buildStoryBriefCards(resource: StoryBriefIndexV1): StoryBriefCard[] {
  return resource.briefs.map((brief) => ({
    briefId: brief.brief_id,
    packageId: brief.package_id,
    title: brief.title,
    theme: brief.theme,
    premise: brief.premise,
    languageMode: brief.language_mode,
    ageBand: brief.age_band,
    desiredPageCount: brief.desired_page_count,
    status: brief.status,
    latestJobId: brief.latest_job_id ?? null,
    latestFailureReason: brief.latest_failure_reason ?? null,
    updatedAt: brief.updated_at,
  }));
}

export function buildStoryGenerationJobCards(
  resource: StoryGenerationJobIndexV1,
): StoryGenerationJobCard[] {
  return resource.jobs.map((job) => ({
    jobId: job.job_id,
    briefId: job.brief_id,
    packageId: job.package_id,
    jobType: job.job_type,
    status: job.status,
    selectedProvider: job.selected_provider ?? null,
    failureReason: job.failure_reason ?? null,
    generatedAssetCount: job.generated_asset_keys?.length ?? 0,
    updatedAt: job.completed_at ?? job.requested_at,
  }));
}

export function createStoryGenerationServices(
  client: StoryGenerationClient,
): StoryGenerationServices {
  return {
    async listBriefCards() {
      return buildStoryBriefCards(await client.listStoryBriefs());
    },
    async createBrief(payload) {
      return client.createStoryBrief(payload);
    },
    async generateDraft(briefId, payload) {
      return client.generateStoryBriefDraft(briefId, payload);
    },
    async generateMedia(briefId, payload) {
      return client.generateStoryBriefMedia(briefId, payload);
    },
    async listJobCards() {
      return buildStoryGenerationJobCards(await client.listStoryGenerationJobs());
    },
  };
}
