# LumosReading V2 Engineering Delivery Plan

Updated: 2026-03-31

## Purpose

This document turns the V2 strategy and architecture blueprint into a strict execution order. It exists to stop work from drifting back into PoC-style parallel invention.

The repo should now be delivered through seven sequential phases:

1. `Phase 0` MVP boundary freeze and engineering governance
2. `Phase 1` child runtime stable reading loop
3. `Phase 2` caregiver assignment and feedback loop
4. `Phase 3` package build and release loop
5. `Phase 4` studio minimum operations console
6. `Phase 5` AI content supply chain v1
7. `Phase 6` monetization and optimization

## Execution rules

- Phases must be released in order. Later phases may start only after the current phase passes QC.
- Parallel work is allowed only inside a phase and only when write scopes do not overlap.
- Every phase must end with:
  - code verification
  - QC review
  - `docs/v2/03-activity-log.md` update
  - git commit
  - git push
- Business meaning changes must update `01-*` first.
- Architecture, domain, API, or event meaning changes must update `02-*` first.
- Contract changes must land in `packages/contracts` in the same phase as the implementation.

## Delivery model

### Mainline

- `packages/contracts`
  Shared schema authority
- `packages/sdk`
  Shared application and transport semantics
- `apps/child-app`
  Child runtime
- `apps/caregiver-web`
  Caregiver operating surface
- `apps/studio-web`
  Studio and release surface
- `apps/api`
  Contract-compatible backend bootstrap
- `apps/workers`
  Async job boundary for packaging, review, and generation

### Phase gate definition

Each phase is considered complete only when all five conditions are true:

1. The intended business loop is usable from the user surface.
2. The required contracts are present and validated.
3. The shared SDK or runtime semantics are updated where needed.
4. Verification commands pass.
5. QC review finds no blocking issue.

## Phase map

| Phase | Outcome | Primary write scope | Blocking dependencies | Can parallelize inside phase | Release gate |
| --- | --- | --- | --- | --- | --- |
| `Phase 0` | Freeze scope, create execution docs, define gates | `docs/v2/*` | None | No | Phase plan and task docs committed |
| `Phase 1` | Child app can read assigned packages offline, resume sessions, and buffer events | `apps/child-app`, `packages/sdk`, `apps/api`, `packages/contracts`, `tests` | Phase 0 | Yes, runtime persistence vs API child shelf | Child runtime survives restart and event upload failure |
| `Phase 2` | Caregiver can assign packages and see reading results | `apps/caregiver-web`, `apps/api`, `packages/sdk`, `packages/contracts`, `tests` | Phase 1 | Yes, assignment mutation vs progress views | Caregiver assignment reaches child shelf and completed reading shows up |
| `Phase 3` | Story packages can be built, released, recalled, and resolved through storage semantics | `apps/workers`, `apps/api`, `packages/sdk`, `packages/contracts`, `tests` | Phase 2 | Yes, package jobs vs release APIs | Draft to release to runtime lookup works with versioned package records |
| `Phase 4` | Studio operators can review, publish, and recall content | `apps/studio-web`, `apps/api`, `packages/sdk`, `packages/contracts`, `tests` | Phase 3 | Yes, review console vs release console | No runtime content bypasses review state |
| `Phase 5` | AI-assisted content creation can produce reviewable story package drafts | `apps/workers`, `apps/api`, `apps/studio-web`, `packages/sdk`, `packages/contracts`, `tests` | Phase 4 | Yes, generation orchestration vs review jobs | Brief to generated draft to reviewed package is runnable |
| `Phase 6` | Entitlements, subscriptions, experimentation, and operational metrics close the business loop | `apps/caregiver-web`, `apps/api`, `apps/studio-web`, `packages/sdk`, `packages/contracts`, `tests` | Phase 5 | Yes, entitlements vs reporting | Trial, subscription access, and weekly value loop work together |

## Phase detail

### Phase 0

Goal:
- Freeze MVP scope and execution order.

Business result:
- The team works from one delivery plan instead of competing implementation ideas.

Primary artifacts:
- This file
- `docs/v2/phase-tasks/*`
- `docs/v2/03-activity-log.md`

### Phase 1

Goal:
- Make the child runtime stable enough to survive real usage conditions.

Business result:
- A child can open assigned content, continue reading after interruption, and finish reading even when the network is unstable.

Required capabilities:
- assignment-driven home shelf
- local story package cache
- session persistence and cold-start resume
- buffered event queue with retry
- multi-page API package fixtures for runtime verification

### Phase 2

Goal:
- Let caregivers drive the child shelf and see actual reading outcomes.

Business result:
- A caregiver assigns a package, the child sees it, and the caregiver later sees the result.

Required capabilities:
- child assignment mutations
- caregiver child profile editing
- recent reading status
- weekly progress summary
- shared contract coverage for assignment and report flows

### Phase 3

Goal:
- Turn content from a loose fixture into a releasable runtime asset.

Business result:
- A story moves from draft data into a versioned `StoryPackage` that the runtime can fetch and that operators can roll back.

Required capabilities:
- package source records
- package build jobs
- release records
- recall and rollback controls
- object storage resolution semantics

### Phase 4

Goal:
- Give operators a minimal but authoritative console.

Business result:
- The studio surface becomes the control point for review, release, and recall instead of a read-only contracts probe.

Required capabilities:
- draft list
- package detail
- safety audit status
- publish and recall actions
- release history visibility

### Phase 5

Goal:
- Add AI into the content supply chain without making runtime depend on live generation.

Business result:
- Editors can start from a brief, generate draft content and media, then review and release it as a package.

Required capabilities:
- brief record
- generation job orchestration
- illustration provider selection
- package draft assembly
- review checkpoints and audit artifacts

### Phase 6

Goal:
- Close the commercial and operating loop.

Business result:
- Entitlements, subscriptions, and weekly value reporting support real paid usage.

Required capabilities:
- entitlements domain
- subscription status surface
- access control on assignments and package delivery
- weekly report improvements
- experiment-safe metrics instrumentation

## QC protocol

### QC questions

Every phase review must answer:

1. Does the implemented loop match the phase objective, or did it drift into side work?
2. Are contracts and SDK semantics aligned with the implementation?
3. Does the user-facing flow work under failure conditions relevant to this phase?
4. Are verification commands sufficient for the touched surfaces?
5. Is `docs/v2/03-activity-log.md` updated with completed work, decisions, checks, and next slice?

### Severity policy

- `blocking`
  Phase cannot be released or pushed as complete.
- `follow-up`
  Acceptable within the current phase if it does not break the gate.
- `note`
  Observation only.

## Commit discipline

- Prefer one commit per completed phase slice.
- Commit message format:
  - `docs(v2): freeze phased delivery plan`
  - `feat(child-app): persist runtime shelf and buffered events`
  - `feat(caregiver): add assignment loop and reading feedback`
- Push after each phase gate clears.

## Related docs

- `docs/v2/01-strategy-review-and-references.md`
- `docs/v2/02-v2-architecture-and-migration-blueprint.md`
- `docs/v2/03-activity-log.md`
- `docs/v2/phase-tasks/`
