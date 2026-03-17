# V2 Active Docs

This directory is the single active documentation set for LumosReading V2.

## Active files

- `01-strategy-review-and-references.md`
  Strategy review, research synthesis, product positioning, market assumptions, and external references.
- `02-v2-architecture-and-migration-blueprint.md`
  Target architecture, domain model, API and event blueprint, migration plan, and delivery roadmap.
- `03-activity-log.md`
  Current execution log, repo baseline, recent milestones, operating decisions, verification history, and next slices.

## Required read order

Before starting work, read in this order:

1. `01-strategy-review-and-references.md`
2. `02-v2-architecture-and-migration-blueprint.md`
3. `03-activity-log.md`
4. `packages/contracts/schemas/README.md`
5. `apps/README.md`
6. `packages/contracts/README.md`

## Governance rules

- `01-*` defines why the product exists, who it is for, and which research-backed principles matter.
- `02-*` defines how the system should be shaped and how the monorepo should evolve.
- `03-*` records what has actually been built, what is currently in flight, and what should happen next.
- Update `03-activity-log.md` before and after every meaningful development session.
- If docs and schema drift apart, update docs first, then schema, then implementation.
