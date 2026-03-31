import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import {
  caregiverAssignmentCommandV1Schema,
  caregiverAssignmentResponseV1Schema,
  childHomeV1Schema,
  caregiverChildrenV1Schema,
  caregiverDashboardV1Schema,
  caregiverHouseholdV1Schema,
  caregiverPlanV1Schema,
  caregiverProgressV1Schema,
  householdEntitlementV1Schema,
  opsMetricsSnapshotV1Schema,
  readingEventBatchV2Schema,
  readingEventIngestedResponseV2Schema,
  readingSessionCreateV2Schema,
  readingSessionResponseV2Schema,
  safetyAuditV1Schema,
  storyBriefCommandV1Schema,
  storyBriefIndexV1Schema,
  storyBriefV1Schema,
  storyGenerationJobCommandV1Schema,
  storyGenerationJobIndexV1Schema,
  storyGenerationJobV1Schema,
  storyPackageBuildCommandV1Schema,
  storyPackageBuildV1Schema,
  storyPackageDraftIndexV1Schema,
  storyPackageDraftV1Schema,
  storyPackageHistoryV1Schema,
  storyPackageRecallCommandV1Schema,
  storyPackageReviewCommandV1Schema,
  storyPackageReleaseCommandV1Schema,
  storyPackageReleaseV1Schema,
  storyPackageRollbackCommandV1Schema,
  storyPackageV1Schema,
  weeklyValueReportV1Schema,
} from "@lumosreading/contracts";
import {
  buildDemoCaregiverAssignmentCommand,
  buildDemoCaregiverAssignmentResponse,
  buildDemoReadingEventBatchRequest,
  buildDemoReadingEventIngestedResponse,
  buildDemoReadingSessionPayload,
  buildDemoReadingSessionResponse,
  buildDemoStoryBriefCommand,
  buildDemoStoryGenerationJobCommand,
  buildDemoStoryPackageBuild,
  buildDemoStoryPackageBuildCommand,
  buildDemoStoryPackageHistory,
  buildDemoStoryPackageRecallCommand,
  buildDemoStoryPackageReviewCommand,
  buildDemoStoryPackageRelease,
  buildDemoStoryPackageReleaseCommand,
  buildDemoStoryPackageRollbackCommand,
  demoAcceptedAt,
  demoPackageQueue,
  fallbackChildHome,
  demoReadingSessionId,
  fallbackStoryPackageDraft,
  fallbackStoryPackageDraftIndex,
  demoSafetyAudit,
  demoStoryPackage,
  fallbackCaregiverChildren,
  fallbackCaregiverDashboard,
  fallbackCaregiverHousehold,
  fallbackCaregiverPlan,
  fallbackCaregiverProgress,
  fallbackDraftGenerationJob,
  fallbackHouseholdEntitlement,
  fallbackMediaGenerationJob,
  fallbackOpsMetricsSnapshot,
  fallbackStoryBrief,
  fallbackStoryBriefIndex,
  fallbackStoryGenerationJobIndex,
  fallbackWeeklyValueReport,
} from "./demo";
import { buildStoryPackageHistoryView } from "./release";

type ValidationCase = {
  name: string;
  schema: object;
  payload: unknown;
};

type ValidationResult = {
  checked: string[];
  count: number;
};

function buildValidationCases(): ValidationCase[] {
  return [
    {
      name: "caregiver-assignment-command.v1 demo request",
      schema: caregiverAssignmentCommandV1Schema,
      payload: buildDemoCaregiverAssignmentCommand({
        requestedAt: demoAcceptedAt,
      }),
    },
    {
      name: "caregiver-assignment-response.v1 demo response",
      schema: caregiverAssignmentResponseV1Schema,
      payload: buildDemoCaregiverAssignmentResponse({
        acceptedAt: demoAcceptedAt,
      }),
    },
    {
      name: "child-home.v1 fallback child home",
      schema: childHomeV1Schema,
      payload: fallbackChildHome,
    },
    {
      name: "story-package.v1 demo story package",
      schema: storyPackageV1Schema,
      payload: demoStoryPackage,
    },
    {
      name: "caregiver-household.v1 fallback household",
      schema: caregiverHouseholdV1Schema,
      payload: fallbackCaregiverHousehold,
    },
    {
      name: "caregiver-children.v1 fallback children",
      schema: caregiverChildrenV1Schema,
      payload: fallbackCaregiverChildren,
    },
    {
      name: "caregiver-plan.v1 fallback plan",
      schema: caregiverPlanV1Schema,
      payload: fallbackCaregiverPlan,
    },
    {
      name: "caregiver-progress.v1 fallback progress",
      schema: caregiverProgressV1Schema,
      payload: fallbackCaregiverProgress,
    },
    {
      name: "caregiver-dashboard.v1 fallback dashboard",
      schema: caregiverDashboardV1Schema,
      payload: fallbackCaregiverDashboard,
    },
    {
      name: "household-entitlement.v1 fallback entitlement",
      schema: householdEntitlementV1Schema,
      payload: fallbackHouseholdEntitlement,
    },
    {
      name: "weekly-value-report.v1 fallback weekly value",
      schema: weeklyValueReportV1Schema,
      payload: fallbackWeeklyValueReport,
    },
    {
      name: "ops-metrics-snapshot.v1 fallback ops metrics",
      schema: opsMetricsSnapshotV1Schema,
      payload: fallbackOpsMetricsSnapshot,
    },
    {
      name: "reading-session-create.v2 demo request",
      schema: readingSessionCreateV2Schema,
      payload: buildDemoReadingSessionPayload({
        startedAt: demoAcceptedAt,
      }),
    },
    {
      name: "reading-session-response.v2 demo response",
      schema: readingSessionResponseV2Schema,
      payload: buildDemoReadingSessionResponse({
        acceptedAt: demoAcceptedAt,
      }),
    },
    {
      name: "reading-event-batch.v2 demo batch request",
      schema: readingEventBatchV2Schema,
      payload: buildDemoReadingEventBatchRequest({
        occurredAt: demoAcceptedAt,
        sessionId: demoReadingSessionId,
      }),
    },
    {
      name: "reading-event-ingested-response.v2 demo response",
      schema: readingEventIngestedResponseV2Schema,
      payload: buildDemoReadingEventIngestedResponse({
        acceptedAt: demoAcceptedAt,
        sessionIds: [demoReadingSessionId],
      }),
    },
    {
      name: "safety-audit.v1 demo audit",
      schema: safetyAuditV1Schema,
      payload: demoSafetyAudit,
    },
    {
      name: "story-brief-command.v1 demo command",
      schema: storyBriefCommandV1Schema,
      payload: buildDemoStoryBriefCommand(),
    },
    {
      name: "story-brief.v1 fallback brief",
      schema: storyBriefV1Schema,
      payload: fallbackStoryBrief,
    },
    {
      name: "story-brief-index.v1 fallback brief index",
      schema: storyBriefIndexV1Schema,
      payload: fallbackStoryBriefIndex,
    },
    {
      name: "story-generation-job-command.v1 demo command",
      schema: storyGenerationJobCommandV1Schema,
      payload: buildDemoStoryGenerationJobCommand(),
    },
    {
      name: "story-generation-job.v1 fallback draft job",
      schema: storyGenerationJobV1Schema,
      payload: fallbackDraftGenerationJob,
    },
    {
      name: "story-generation-job.v1 fallback media job",
      schema: storyGenerationJobV1Schema,
      payload: fallbackMediaGenerationJob,
    },
    {
      name: "story-generation-job-index.v1 fallback job index",
      schema: storyGenerationJobIndexV1Schema,
      payload: fallbackStoryGenerationJobIndex,
    },
    {
      name: "story-package-draft.v1 fallback draft",
      schema: storyPackageDraftV1Schema,
      payload: fallbackStoryPackageDraft,
    },
    {
      name: "story-package-draft-index.v1 fallback draft index",
      schema: storyPackageDraftIndexV1Schema,
      payload: fallbackStoryPackageDraftIndex,
    },
    {
      name: "story-package-build-command.v1 demo command",
      schema: storyPackageBuildCommandV1Schema,
      payload: buildDemoStoryPackageBuildCommand(),
    },
    {
      name: "story-package-build.v1 demo build",
      schema: storyPackageBuildV1Schema,
      payload: buildDemoStoryPackageBuild(),
    },
    {
      name: "story-package-release-command.v1 demo command",
      schema: storyPackageReleaseCommandV1Schema,
      payload: buildDemoStoryPackageReleaseCommand(),
    },
    {
      name: "story-package-release.v1 demo release",
      schema: storyPackageReleaseV1Schema,
      payload: buildDemoStoryPackageRelease(),
    },
    {
      name: "story-package-recall-command.v1 demo command",
      schema: storyPackageRecallCommandV1Schema,
      payload: buildDemoStoryPackageRecallCommand(),
    },
    {
      name: "story-package-review-command.v1 demo command",
      schema: storyPackageReviewCommandV1Schema,
      payload: buildDemoStoryPackageReviewCommand(),
    },
    {
      name: "story-package-rollback-command.v1 demo command",
      schema: storyPackageRollbackCommandV1Schema,
      payload: buildDemoStoryPackageRollbackCommand(),
    },
    {
      name: "story-package-history.v1 demo history",
      schema: storyPackageHistoryV1Schema,
      payload: buildDemoStoryPackageHistory(),
    },
  ];
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

export function validateDemoContractsOrThrow(): ValidationResult {
  const ajv = new Ajv2020({
    allErrors: true,
    strict: false,
  });
  addFormats(ajv);
  ajv.addSchema(
    childHomeV1Schema,
    "https://schemas.lumosreading.local/child-home.v1.schema.json",
  );
  ajv.addSchema(
    householdEntitlementV1Schema,
    "https://schemas.lumosreading.local/household-entitlement.v1.schema.json",
  );
  ajv.addSchema(
    opsMetricsSnapshotV1Schema,
    "https://schemas.lumosreading.local/ops-metrics-snapshot.v1.schema.json",
  );
  ajv.addSchema(
    storyPackageV1Schema,
    "https://schemas.lumosreading.local/story-package.v1.schema.json",
  );
  ajv.addSchema(
    weeklyValueReportV1Schema,
    "https://schemas.lumosreading.local/weekly-value-report.v1.schema.json",
  );
  ajv.addSchema(
    safetyAuditV1Schema,
    "https://schemas.lumosreading.local/safety-audit.v1.schema.json",
  );
  ajv.addSchema(
    storyBriefV1Schema,
    "https://schemas.lumosreading.local/story-brief.v1.schema.json",
  );
  ajv.addSchema(
    storyGenerationJobV1Schema,
    "https://schemas.lumosreading.local/story-generation-job.v1.schema.json",
  );
  ajv.addSchema(
    storyPackageDraftV1Schema,
    "https://schemas.lumosreading.local/story-package-draft.v1.schema.json",
  );
  ajv.addSchema(
    storyPackageBuildV1Schema,
    "https://schemas.lumosreading.local/story-package-build.v1.schema.json",
  );
  ajv.addSchema(
    storyPackageReleaseV1Schema,
    "https://schemas.lumosreading.local/story-package-release.v1.schema.json",
  );

  const cases = buildValidationCases();
  const checked: string[] = [];

  for (const validationCase of cases) {
    const validate = ajv.compile(validationCase.schema);
    const valid = validate(validationCase.payload);

    if (!valid) {
      const details = ajv.errorsText(validate.errors, {
        separator: "\n",
      });
      throw new Error(`SDK demo contract validation failed for ${validationCase.name}\n${details}`);
    }

    checked.push(validationCase.name);
  }

  const englishPackage = demoPackageQueue.find(
    storyPackage => storyPackage.language_mode === "en-US",
  );

  assert(englishPackage, "Expected at least one English demo package.");

  const englishSessionPayload = buildDemoReadingSessionPayload({
    packageId: englishPackage.package_id,
    startedAt: demoAcceptedAt,
  });
  assert(
    englishSessionPayload.language_mode === "en-US",
    "Demo session payload should inherit language_mode from the selected package.",
  );

  const englishEventBatch = buildDemoReadingEventBatchRequest({
    packageId: englishPackage.package_id,
    occurredAt: demoAcceptedAt,
    sessionId: demoReadingSessionId,
  });
  assert(
    englishEventBatch.events.every(event => event.language_mode === "en-US"),
    "Demo reading events should inherit language_mode from the selected package.",
  );

  const englishProgressEvent = fallbackCaregiverProgress.recent_events.find(
    item => item.event.package_id === englishPackage.package_id,
  );
  assert(
    englishProgressEvent?.event.language_mode === "en-US",
    "Demo caregiver progress should preserve package language metadata for English packages.",
  );
  assert(
    !fallbackChildHome.package_queue.some(
      storyPackage => storyPackage.package_id === "99999999-9999-9999-9999-999999999999",
    ),
    "Fallback child home should exclude locked packages from the visible queue.",
  );
  assert(
    fallbackHouseholdEntitlement.locked_package_count === 1,
    "Fallback entitlement should preserve one locked package for Phase 6 surfaces.",
  );

  const storyPackageHistoryView = buildStoryPackageHistoryView(
    buildDemoStoryPackageHistory(),
  );
  assert(
    storyPackageHistoryView.operatorNotes.length > 0,
    "Release history view should preserve operator notes for studio surfaces.",
  );
  assert(
    storyPackageHistoryView.audit.audit_status === "approved",
    "Release history view should preserve audit status for studio surfaces.",
  );
  assert(
    storyPackageHistoryView.packagePreview.title.length > 0,
    "Release history view should preserve package preview details for studio surfaces.",
  );

  return {
    checked: [
      ...checked,
      "demo english session payload inherits package language",
      "demo english event batch inherits package language",
      "demo caregiver progress preserves english language metadata",
      "fallback child home excludes locked packages",
      "fallback entitlement preserves locked package count",
      "release history view preserves operator notes",
      "release history view preserves audit status",
      "release history view preserves package preview detail",
    ],
    count: checked.length + 8,
  };
}

const isDirectRun = process.argv[1]?.endsWith("self-check.ts");

if (isDirectRun) {
  const result = validateDemoContractsOrThrow();
  console.log(JSON.stringify(result, null, 2));
}
