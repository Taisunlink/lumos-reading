# V2 Schemas

These files are the authoritative shared schemas for LumosReading V2.

## Current schema set

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

## Scope

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
