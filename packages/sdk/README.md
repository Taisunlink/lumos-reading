# `@lumosreading/sdk`

Shared V2 API client package for LumosReading.

## Scope

- Consume `@lumosreading/contracts` request and response shapes
- Expose a reusable client for `/api/v2`
- Keep transport logic out of app pages and components

## Current API surface

- `getCaregiverHousehold`
- `getCaregiverChildren`
- `getCaregiverPlan`
- `getCaregiverProgress`
- `getCaregiverDashboard`
- `getStoryPackage`
- `createReadingSession`
- `ingestReadingEvents`

`@lumosreading/contracts` remains the authority for schemas and domain payload types.
