# `@lumosreading/sdk`

Shared V2 API client package for LumosReading.

## Scope

- Consume `@lumosreading/contracts` request and response shapes
- Expose a reusable client for `/api/v2`
- Keep transport logic out of app pages and components
- Expose shared caregiver subdomain services so multiple surfaces can consume the same page models
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

`@lumosreading/contracts` remains the authority for schemas and domain payload types.
