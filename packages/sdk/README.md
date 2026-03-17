# `@lumosreading/sdk`

Shared V2 API client package for LumosReading.

## Scope

- Consume `@lumosreading/contracts` request and response shapes
- Expose a reusable client for `/api/v2`
- Keep transport logic out of app pages and components
- Expose shared caregiver subdomain services so multiple surfaces can consume the same page models
- Expose shared reading application services for story package lookup, reading session creation, and event ingestion
- Expose the placeholder OSS storage contract used by demo and fallback assets

## Current API surface

- `getCaregiverHousehold`
- `getCaregiverChildren`
- `getCaregiverPlan`
- `getCaregiverProgress`
- `getCaregiverDashboard`
- `getStoryPackage`
- `createReadingSession`
- `ingestReadingEvents`

## Shared domain surfaces

- `createCaregiverSubdomainServices`
- `buildHouseholdOverview`
- `buildChildDomainView`
- `buildPlanDomainView`
- `buildProgressDomainView`
- `demoHouseholdId`
- `fallbackHouseholdOverview`
- `fallbackChildDomainView`
- `fallbackPlanDomainView`
- `fallbackProgressDomainView`
- `PlaceholderOssStorageService`
- `createPlaceholderOssStorageService`

## Shared application surfaces

- `createReadingApplicationServices`
- `buildDemoReadingSessionPayload`
- `buildDemoReadingSessionResponse`
- `buildDemoReadingEventBatchRequest`
- `buildDemoReadingEventIngestedResponse`
- `demoStoryPackageId`
- `demoChildId`
- `demoReadingSessionId`

## Self-check

Run `npm run test:contracts --workspace @lumosreading/sdk` to validate SDK demo builders and fallback models against the shared JSON Schemas.

`@lumosreading/contracts` remains the authority for schemas and domain payload types.
