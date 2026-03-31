import type {
  SafetyAuditV1,
  StoryPackageBuildCommandV1,
  StoryPackageBuildV1,
  StoryPackageDraftIndexV1,
  StoryPackageHistoryV1,
  StoryPackageManifestV1,
  StoryPackageRecallCommandV1,
  StoryPackageReleaseCommandV1,
  StoryPackageReleaseV1,
  StoryPackageRollbackCommandV1,
} from "@lumosreading/contracts";

export interface StoryPackageReleaseClient {
  listStoryPackageDrafts(): Promise<StoryPackageDraftIndexV1>;
  getStoryPackageHistory(packageId: string): Promise<StoryPackageHistoryV1>;
  triggerStoryPackageBuild(
    packageId: string,
    payload: StoryPackageBuildCommandV1,
  ): Promise<StoryPackageBuildV1>;
  releaseStoryPackageBuild(
    packageId: string,
    payload: StoryPackageReleaseCommandV1,
  ): Promise<StoryPackageReleaseV1>;
  recallStoryPackageRelease(
    packageId: string,
    payload: StoryPackageRecallCommandV1,
  ): Promise<StoryPackageReleaseV1>;
  rollbackStoryPackageRelease(
    packageId: string,
    payload: StoryPackageRollbackCommandV1,
  ): Promise<StoryPackageReleaseV1>;
}

export type StoryPackageDraftCard = {
  draftId: string;
  packageId: string;
  title: string;
  workflowState: string;
  sourceType: string;
  reviewStatus: string;
  auditStatus: string;
  auditSeverity: string;
  findingCount: number;
  releaseChannel: string;
  latestBuildId: string | null;
  activeReleaseId: string | null;
  updatedAt: string;
};

export type StoryPackageHistoryView = {
  draftId: string;
  packageId: string;
  title: string;
  subtitle?: string;
  sourceType: string;
  workflowState: string;
  reviewStatus: string;
  auditStatus: string;
  auditSeverity: string;
  findingCount: number;
  packagePreview: StoryPackageManifestV1;
  audit: SafetyAuditV1;
  operatorNotes: string[];
  builds: StoryPackageBuildV1[];
  releases: StoryPackageReleaseV1[];
  latestBuildId: string | null;
  activeReleaseId: string | null;
  createdAt: string;
  updatedAt: string;
};

export interface StoryPackageReleaseServices {
  listDraftCards(): Promise<StoryPackageDraftCard[]>;
  getHistoryView(packageId: string): Promise<StoryPackageHistoryView>;
  triggerBuild(
    packageId: string,
    payload: StoryPackageBuildCommandV1,
  ): Promise<StoryPackageBuildV1>;
  publishBuild(
    packageId: string,
    payload: StoryPackageReleaseCommandV1,
  ): Promise<StoryPackageReleaseV1>;
  recallRelease(
    packageId: string,
    payload: StoryPackageRecallCommandV1,
  ): Promise<StoryPackageReleaseV1>;
  rollbackRelease(
    packageId: string,
    payload: StoryPackageRollbackCommandV1,
  ): Promise<StoryPackageReleaseV1>;
}

export function buildStoryPackageDraftCards(
  resource: StoryPackageDraftIndexV1,
): StoryPackageDraftCard[] {
  return resource.drafts.map((draft) => ({
    draftId: draft.draft_id,
    packageId: draft.package_id,
    title: draft.package_preview.title,
    workflowState: draft.workflow_state,
    sourceType: draft.source_type,
    reviewStatus: draft.package_preview.safety.review_status,
    auditStatus: draft.safety_audit.audit_status,
    auditSeverity: draft.safety_audit.severity,
    findingCount: draft.safety_audit.findings.length,
    releaseChannel: draft.package_preview.release_channel,
    latestBuildId: draft.latest_build_id ?? null,
    activeReleaseId: draft.active_release_id ?? null,
    updatedAt: draft.updated_at,
  }));
}

export function buildStoryPackageHistoryView(
  resource: StoryPackageHistoryV1,
): StoryPackageHistoryView {
  return {
    draftId: resource.draft.draft_id,
    packageId: resource.package_id,
    title: resource.draft.package_preview.title,
    subtitle: resource.draft.package_preview.subtitle,
    sourceType: resource.draft.source_type,
    workflowState: resource.draft.workflow_state,
    reviewStatus: resource.draft.package_preview.safety.review_status,
    auditStatus: resource.draft.safety_audit.audit_status,
    auditSeverity: resource.draft.safety_audit.severity,
    findingCount: resource.draft.safety_audit.findings.length,
    packagePreview: resource.draft.package_preview,
    audit: resource.draft.safety_audit,
    operatorNotes: resource.draft.operator_notes,
    builds: resource.builds,
    releases: resource.releases,
    latestBuildId: resource.draft.latest_build_id ?? null,
    activeReleaseId: resource.active_release_id ?? null,
    createdAt: resource.draft.created_at,
    updatedAt: resource.draft.updated_at,
  };
}

export function createStoryPackageReleaseServices(
  client: StoryPackageReleaseClient,
): StoryPackageReleaseServices {
  return {
    async listDraftCards() {
      return buildStoryPackageDraftCards(await client.listStoryPackageDrafts());
    },
    async getHistoryView(packageId: string) {
      return buildStoryPackageHistoryView(
        await client.getStoryPackageHistory(packageId),
      );
    },
    async triggerBuild(packageId: string, payload: StoryPackageBuildCommandV1) {
      return client.triggerStoryPackageBuild(packageId, payload);
    },
    async publishBuild(
      packageId: string,
      payload: StoryPackageReleaseCommandV1,
    ) {
      return client.releaseStoryPackageBuild(packageId, payload);
    },
    async recallRelease(
      packageId: string,
      payload: StoryPackageRecallCommandV1,
    ) {
      return client.recallStoryPackageRelease(packageId, payload);
    },
    async rollbackRelease(
      packageId: string,
      payload: StoryPackageRollbackCommandV1,
    ) {
      return client.rollbackStoryPackageRelease(packageId, payload);
    },
  };
}
