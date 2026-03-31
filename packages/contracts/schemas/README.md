# V2 Schemas

These files are the authoritative shared schemas for LumosReading V2.

## Current schema set

- `caregiver-assignment-command.v1.schema.json`
- `caregiver-assignment-response.v1.schema.json`
- `caregiver-household.v1.schema.json`
- `caregiver-children.v1.schema.json`
- `caregiver-plan.v1.schema.json`
- `caregiver-progress.v1.schema.json`
- `caregiver-dashboard.v1.schema.json`
- `child-home.v1.schema.json`
- `story-package.v1.schema.json`
- `reading-event.v1.schema.json`
- `reading-session-create.v2.schema.json`
- `reading-session-response.v2.schema.json`
- `reading-event-batch.v2.schema.json`
- `reading-event-ingested-response.v2.schema.json`
- `safety-audit.v1.schema.json`
- `story-package-build-command.v1.schema.json`
- `story-package-build.v1.schema.json`
- `story-package-draft-index.v1.schema.json`
- `story-package-draft.v1.schema.json`
- `story-package-history.v1.schema.json`
- `story-package-recall-command.v1.schema.json`
- `story-package-release-command.v1.schema.json`
- `story-package-release.v1.schema.json`
- `story-package-rollback-command.v1.schema.json`

## Scope

- `CaregiverAssignmentCommand v1`
  Write contract for updating a child's currently assigned reading package from the caregiver surface.
- `CaregiverAssignmentResponse v1`
  Response contract for an accepted caregiver assignment update with the updated child assignment context.
- `CaregiverHousehold v1`
  Read model for the household operating surface, featured package selection, queue visibility, and top-level caregiver metrics.
- `CaregiverChildren v1`
  Read model for caregiver child assignments with embedded current package context.
- `CaregiverPlan v1`
  Read model for caregiver weekly plan entries with embedded package payloads.
- `CaregiverProgress v1`
  Read model for caregiver progress review with typed events plus child and package labels.
- `CaregiverDashboard v1`
  Aggregate compatibility view for the caregiver surface.
- `ChildHome v1`
  Child-facing assigned shelf contract that provides featured package selection and the runtime shelf.
- `StoryPackage v1`
  Runtime distribution and cache contract for child-facing story packages.
- `ReadingEvent v1`
  Typed reading event contract for analytics, progress, and recommendation inputs.
- `ReadingSessionCreate v2`
  Write contract for creating a reading session receipt.
- `ReadingSessionResponse v2`
  Response contract for accepted reading session creation.
- `ReadingEventBatch v2`
  Write contract for batched reading event ingestion.
- `ReadingEventIngestedResponse v2`
  Response contract for accepted reading event ingestion.
- `SafetyAudit v1`
  Audit and governance contract for review, recall, and compliance workflows.
- `StoryPackageDraft v1`
  Studio-facing package draft record with preview manifest, review state, and release pointers.
- `StoryPackageDraftIndex v1`
  Studio-facing list contract for package draft visibility and operator refresh state.
- `StoryPackageBuildCommand v1`
  Write contract for triggering a versioned story package build.
- `StoryPackageBuild v1`
  Build job and output contract for versioned runtime package artifacts.
- `StoryPackageReleaseCommand v1`
  Write contract for promoting a specific build into runtime lookup.
- `StoryPackageRelease v1`
  Release record contract for active, recalled, and superseded runtime states.
- `StoryPackageRecallCommand v1`
  Write contract for recalling an active release without breaking lookup fallback semantics.
- `StoryPackageRollbackCommand v1`
  Write contract for promoting a prior release back into the active runtime path.
- `StoryPackageHistory v1`
  Query contract for one package's draft, build history, release history, and current active release.

## Design rules

- Schemas are authoritative over temporary frontend or backend types.
- Schemas are authoritative over ad hoc agent output formats.
- Breaking changes require a new versioned schema.
- Runtime surfaces should only consume approved, versioned content and request contracts.

## Related docs

- `docs/v2/01-strategy-review-and-references.md`
- `docs/v2/02-v2-architecture-and-migration-blueprint.md`
- `docs/v2/03-activity-log.md`

## Required read order

Before changing schemas or any contract-consuming surface, read in this order:

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `docs/v2/03-activity-log.md`
4. This file
5. `apps/README.md`
6. `packages/contracts/README.md`
