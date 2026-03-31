import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import {
  childHomeV1Schema,
  caregiverChildrenV1Schema,
  caregiverDashboardV1Schema,
  caregiverHouseholdV1Schema,
  caregiverPlanV1Schema,
  caregiverProgressV1Schema,
  readingEventBatchV2Schema,
  readingEventIngestedResponseV2Schema,
  readingSessionCreateV2Schema,
  readingSessionResponseV2Schema,
  storyPackageV1Schema,
} from "@lumosreading/contracts";
import {
  buildDemoReadingEventBatchRequest,
  buildDemoReadingEventIngestedResponse,
  buildDemoReadingSessionPayload,
  buildDemoReadingSessionResponse,
  demoAcceptedAt,
  demoPackageQueue,
  fallbackChildHome,
  demoReadingSessionId,
  demoStoryPackage,
  fallbackCaregiverChildren,
  fallbackCaregiverDashboard,
  fallbackCaregiverHousehold,
  fallbackCaregiverPlan,
  fallbackCaregiverProgress,
} from "./demo";

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
    storyPackageV1Schema,
    "https://schemas.lumosreading.local/story-package.v1.schema.json",
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

  return {
    checked: [
      ...checked,
      "demo english session payload inherits package language",
      "demo english event batch inherits package language",
      "demo caregiver progress preserves english language metadata",
    ],
    count: checked.length + 3,
  };
}

const isDirectRun = process.argv[1]?.endsWith("self-check.ts");

if (isDirectRun) {
  const result = validateDemoContractsOrThrow();
  console.log(JSON.stringify(result, null, 2));
}
