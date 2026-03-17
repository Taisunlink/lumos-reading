# `@lumosreading/contracts`

Shared contract package for LumosReading V2.

## Purpose

This package carries the formal shared contracts used across apps and services. It has higher authority than temporary prompts, mocks, or page-local data shapes.

## Governed contracts

- `CaregiverDashboard v1`
- `CaregiverHousehold v1`
- `CaregiverChildren v1`
- `CaregiverPlan v1`
- `CaregiverProgress v1`
- `StoryPackage v1`
- `ReadingEvent v1`
- `ReadingSessionCreate v2`
- `ReadingSessionResponse v2`
- `ReadingEventBatch v2`
- `ReadingEventIngestedResponse v2`
- `SafetyAudit v1`

## Package outputs

- Raw JSON Schema files
- Matching TypeScript types and schema constants

## Read order

Before starting V2 work, read in this order:

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `packages/contracts/schemas/README.md`
4. `apps/README.md`
5. This file

## Change rules

- If business meaning changes, update `docs/v2/01-*` first.
- If architecture, domain model, API, or event semantics change, update `docs/v2/02-*` first.
- If contract fields change, update the matching schema in the same change.
- Runtime objects must not bypass the schema package with silent field additions.
- Existing schema versions must not be silently mutated when the change is breaking.

## Current schema files

- `schemas/caregiver-household.v1.schema.json`
- `schemas/caregiver-children.v1.schema.json`
- `schemas/caregiver-plan.v1.schema.json`
- `schemas/caregiver-progress.v1.schema.json`
- `schemas/caregiver-dashboard.v1.schema.json`
- `schemas/story-package.v1.schema.json`
- `schemas/reading-event.v1.schema.json`
- `schemas/reading-session-create.v2.schema.json`
- `schemas/reading-session-response.v2.schema.json`
- `schemas/reading-event-batch.v2.schema.json`
- `schemas/reading-event-ingested-response.v2.schema.json`
- `schemas/safety-audit.v1.schema.json`
