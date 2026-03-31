# V2 Active Docs

This directory is the single active documentation set for LumosReading V2.

## Active files

- `01-strategy-review-and-references.md`
  Strategy review, research synthesis, product positioning, market assumptions, and external references.
- `02-v2-architecture-and-migration-blueprint.md`
  Target architecture, domain model, API and event blueprint, migration plan, and delivery roadmap.
- `03-activity-log.md`
  Current execution log, repo baseline, recent milestones, operating decisions, verification history, and next slices.
- `04-engineering-delivery-plan.md`
  Sequential delivery order, phase gates, QC protocol, and execution rules for the completed core V2 buildout.
- `05-frontend-experience-and-content-delivery-plan.md`
  Follow-on six-phase plan for frontend experience, product copy, content programming, and launch readiness.
- `phase-tasks/`
  Executable task playbooks for the completed core phases and the follow-on frontend/productization phases.

## Required read order

Before starting work, read in this order:

1. `01-strategy-review-and-references.md`
2. `02-v2-architecture-and-migration-blueprint.md`
3. `03-activity-log.md`
4. `04-engineering-delivery-plan.md`
5. `05-frontend-experience-and-content-delivery-plan.md`
6. `packages/contracts/schemas/README.md`
7. `apps/README.md`
8. `packages/contracts/README.md`

## Governance rules

- `01-*` defines why the product exists, who it is for, and which research-backed principles matter.
- `02-*` defines how the system should be shaped and how the monorepo should evolve.
- `03-*` records what has actually been built, what is currently in flight, and what should happen next.
- `04-*` records the completed core engineering execution order.
- `05-*` defines the active follow-on execution order for frontend experience, product copy, and planning-led productization work.
- Update `03-activity-log.md` before and after every meaningful development session.
- If docs and schema drift apart, update docs first, then schema, then implementation.
