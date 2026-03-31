# LumosReading V2 Frontend Experience And Content Delivery Plan

Updated: 2026-03-31

## Purpose

This document is the follow-on execution plan after the core V2 buildout completed through `Phase 6`.

The previous seven-phase plan established the product skeleton:

- child runtime
- caregiver loop
- package release loop
- studio console
- AI supply chain
- monetization and ops metrics

This plan is about turning that skeleton into a product that is easier to understand, easier to use every day, and easier for a distributed team to keep iterating on from either a local or remote setup.

The work now has to combine three streams in one sequence:

- frontend engineering
- product copy and messaging
- planning for content, conversion, and launch operations

## Delivery principle

The next six phases should not drift back into ad hoc screen polish.

Each phase must produce three kinds of outcome at the same time:

1. a better user-facing flow
2. a clearer product narrative
3. a clearer operational handoff for the next team or location

## Execution rules

- These phases begin only after the completed core V2 foundation plan in `04-engineering-delivery-plan.md`.
- Phases must be released in order. Later phases may start only after the current phase clears QC.
- Parallel work is allowed only inside a phase and only when write scopes do not overlap.
- Every phase must end with:
  - surface-level verification
  - copy and planning review
  - QC review
  - `docs/v2/03-activity-log.md` update
  - git commit
  - git push
- If route structure, user journey meaning, or content programming rules change, update docs before implementation.
- If copy semantics change on shared states such as locked access, review, release, or reading progress, update shared docs in the same phase.

## Collaboration rules For Local And Remote Execution

- Every phase must leave behind one canonical source of truth in the repo, not in chat.
- Every phase must explicitly record:
  - the intended user journey
  - the required copy tone and examples
  - the affected surfaces
  - verification and QC outcome
  - the next recommended slice
- If a phase is only partially complete, mark unfinished tasks in the phase task file instead of describing them informally in commit messages.
- Handoffs should assume the next operator may be in a different time zone and may continue from only the repo plus the activity log.

## Phase Gate Definition

Each frontend/product phase is complete only when all six conditions are true:

1. The intended user journey is coherent on the target surface.
2. The relevant copy and messaging are written and aligned with the flow.
3. The planning deliverables for content, operations, or conversion are captured in repo docs.
4. The affected apps still build or typecheck where applicable.
5. QC review finds no blocking issue.
6. The activity log makes the next handoff obvious.

## Phase Map

| Frontend Phase | Outcome | Primary write scope | Planning deliverables | Can parallelize inside phase | Release gate |
| --- | --- | --- | --- | --- | --- |
| `Frontend Phase 1` | Shared experience baseline and copy system | `docs/v2/*`, shared navigation/layout files, design/copy docs | IA map, tone guide, state inventory | Yes, route inventory vs copy matrix | All active surfaces have one coherent structure and language baseline |
| `Frontend Phase 2` | Child app becomes a stronger daily reading experience | `apps/child-app`, `packages/sdk`, supporting docs | child journey map, reading-state narrative | Yes, home shelf vs session polish | Child can start, continue, and finish reading with a calm and clear flow |
| `Frontend Phase 3` | Caregiver web becomes a true companion surface | `apps/caregiver-web`, `packages/sdk`, supporting docs | caregiver journey map, weekly value narrative | Yes, dashboard vs plan/progress surfaces | Caregiver understands what happened and what to do next |
| `Frontend Phase 4` | Access, trial, and paid conversion become understandable | `apps/caregiver-web`, `apps/child-app`, `apps/api` if needed, docs | trial-to-paid funnel and upgrade messaging | Yes, lock states vs access page vs conversion copy | Locked and paid states are transparent and do not feel arbitrary |
| `Frontend Phase 5` | Studio supports editorial programming and operating clarity | `apps/studio-web`, supporting docs | content programming cadence, campaign and release checklist | Yes, operator views vs programming docs | Operators can plan, review, and release content with less manual coordination |
| `Frontend Phase 6` | Launch readiness, QA, and remote handoff package are complete | all three surfaces plus docs | launch checklist, QA matrix, remote continuation pack | Yes, QA vs launch copy vs rollout docs | The team can continue execution locally or remotely from repo state alone |

## Phase Detail

### Frontend Phase 1

Goal:
- Establish one shared experience language before larger UI changes begin.

Business result:
- Teams stop inventing surface structure, labels, and state language independently.

Required capabilities:
- route and screen inventory
- navigation hierarchy by surface
- shared state language for loading, empty, error, locked, success
- copy tone guide for child, caregiver, and operator audiences
- local/remote handoff template

### Frontend Phase 2

Goal:
- Upgrade the child runtime from functional to emotionally coherent.

Business result:
- The child experience feels calm, readable, and worth reopening daily.

Required capabilities:
- stronger home shelf and continue-reading entry
- clearer reading-session chrome and progress cues
- child-friendly empty and reconnect states
- reading success and completion language
- lightweight journey guidance for session start, pause, and return

### Frontend Phase 3

Goal:
- Make caregiver-web feel like a companion, not just an admin panel.

Business result:
- A caregiver can understand progress, assign the next action, and feel the value of continued use.

Required capabilities:
- improved household overview
- stronger child assignment framing
- clearer weekly value and progress narrative
- recommendation or next-step framing
- caregiver copy for insight, guidance, and trust

### Frontend Phase 4

Goal:
- Turn entitlement and subscription state into understandable user communication.

Business result:
- Trial, locked, and paid moments feel legible and trustworthy rather than arbitrary.

Required capabilities:
- access and membership state design
- lock-state and unavailable-state copy
- upgrade value explanation
- trial timeline and expiry messaging
- conversion-safe CTA and experiment hooks

### Frontend Phase 5

Goal:
- Improve studio-web from an operations console into an editorial programming surface.

Business result:
- The content team can coordinate briefs, reviews, releases, and weekly programming with less off-system coordination.

Required capabilities:
- clearer briefs, packages, releases, and operations navigation
- better operator labels and status language
- programming and release cadence visibility
- campaign and editorial grouping rules
- operator-facing checklist and exception handling language

### Frontend Phase 6

Goal:
- Finish launch-quality polish and make continuation resilient across locations.

Business result:
- The team can keep shipping with fewer hidden assumptions and fewer coordination gaps.

Required capabilities:
- cross-surface QA matrix
- launch copy pack
- release-readiness checklist
- remote continuation instructions
- experiment and metric review package

## QC Protocol

### QC questions

Every frontend/product phase review must answer:

1. Does the resulting flow help the user complete the intended job, or is it just visual polish?
2. Is the copy aligned with the actual state semantics and contract behavior?
3. Are planning outputs concrete enough for another team to continue without verbal context?
4. Are the affected surfaces still technically verifiable?
5. Is the next slice obvious from the repo alone?

### Severity Policy

- `blocking`
  The phase cannot be released as complete.
- `follow-up`
  Acceptable if it does not break the phase gate.
- `note`
  Observation only.

## Commit Discipline

- Prefer one commit per completed frontend/product phase slice.
- Commit message format:
  - `docs(v2): add frontend experience delivery plan`
  - `feat(child-app): polish reading session flow`
  - `feat(caregiver-web): add weekly guidance narrative`
  - `feat(studio-web): add programming workspace`
- Push after each phase gate clears.

## Related Docs

- `docs/v2/01-strategy-review-and-references.md`
- `docs/v2/02-v2-architecture-and-migration-blueprint.md`
- `docs/v2/03-activity-log.md`
- `docs/v2/04-engineering-delivery-plan.md`
- `docs/v2/phase-tasks/`
