# `@lumosreading/contracts`

Shared contract package for LumosReading V2.

## Purpose

This package carries the formal shared contracts used across apps and services. It has higher authority than temporary prompts, mocks, or page-local data shapes.

## Governed contracts

- `CaregiverAssignmentCommand v1`
- `CaregiverAssignmentResponse v1`
- `CaregiverDashboard v1`
- `ChildHome v1`
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
- `StoryPackageDraft v1`
- `StoryPackageDraftIndex v1`
- `StoryPackageBuildCommand v1`
- `StoryPackageBuild v1`
- `StoryPackageReleaseCommand v1`
- `StoryPackageRelease v1`
- `StoryPackageRecallCommand v1`
- `StoryPackageRollbackCommand v1`
- `StoryPackageHistory v1`

## Package outputs

- Raw JSON Schema files
- Matching TypeScript types and schema constants

## Read order

Before starting V2 work, read in this order:

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `docs/v2/03-activity-log.md`
4. `packages/contracts/schemas/README.md`
5. `apps/README.md`
6. This file

## Change rules

- If business meaning changes, update `docs/v2/01-*` first.
- If architecture, domain model, API, or event semantics change, update `docs/v2/02-*` first.
- Update `docs/v2/03-activity-log.md` before and after each meaningful development session.
- If contract fields change, update the matching schema in the same change.
- Runtime objects must not bypass the schema package with silent field additions.
- Existing schema versions must not be silently mutated when the change is breaking.

## Current schema files

- `schemas/caregiver-assignment-command.v1.schema.json`
- `schemas/caregiver-assignment-response.v1.schema.json`
- `schemas/caregiver-household.v1.schema.json`
- `schemas/caregiver-children.v1.schema.json`
- `schemas/caregiver-plan.v1.schema.json`
- `schemas/caregiver-progress.v1.schema.json`
- `schemas/caregiver-dashboard.v1.schema.json`
- `schemas/child-home.v1.schema.json`
- `schemas/story-package.v1.schema.json`
- `schemas/reading-event.v1.schema.json`
- `schemas/reading-session-create.v2.schema.json`
- `schemas/reading-session-response.v2.schema.json`
- `schemas/reading-event-batch.v2.schema.json`
- `schemas/reading-event-ingested-response.v2.schema.json`
- `schemas/safety-audit.v1.schema.json`
- `schemas/story-package-build-command.v1.schema.json`
- `schemas/story-package-build.v1.schema.json`
- `schemas/story-package-draft-index.v1.schema.json`
- `schemas/story-package-draft.v1.schema.json`
- `schemas/story-package-history.v1.schema.json`
- `schemas/story-package-recall-command.v1.schema.json`
- `schemas/story-package-release-command.v1.schema.json`
- `schemas/story-package-release.v1.schema.json`
- `schemas/story-package-rollback-command.v1.schema.json`
