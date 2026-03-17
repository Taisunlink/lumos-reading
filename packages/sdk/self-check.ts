import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import {
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

export function validateDemoContractsOrThrow(): ValidationResult {
  const ajv = new Ajv2020({
    allErrors: true,
    strict: false,
  });
  addFormats(ajv);

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

  return {
    checked,
    count: checked.length,
  };
}

const isDirectRun = process.argv[1]?.endsWith("self-check.ts");

if (isDirectRun) {
  const result = validateDemoContractsOrThrow();
  console.log(JSON.stringify(result, null, 2));
}
