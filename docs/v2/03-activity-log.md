# V2 Activity Log

Updated: 2026-03-31

## Purpose

This log is the mandatory execution journal for LumosReading V2. It exists to keep the repo state, current decisions, completed slices, and next slices visible so work does not drift back into PoC assumptions.

## Working agreement

Before each development session:

1. Read `docs/v2/01-strategy-review-and-references.md`.
2. Read `docs/v2/02-v2-architecture-and-migration-blueprint.md`.
3. Read this file.
4. Read `packages/contracts/schemas/README.md`.
5. Read `apps/README.md`.
6. Read `packages/contracts/README.md`.

After each meaningful development session:

- Update this file with the work completed, decisions made, verification performed, and the next recommended slice.
- If business meaning changed, update `01-*`.
- If architecture, domain, API, or event semantics changed, update `02-*`.
- If shared contract fields changed, update `packages/contracts/schemas/*` in the same change.

## Current repo baseline

- Branch: `master`
- Current working model: contracts-first V2 migration inside the existing monorepo
- Active authority docs: `docs/v2/01-*`, `docs/v2/02-*`, and this file
- Shared contract package: `packages/contracts`
- Shared application package: `packages/sdk`
- Active V2 surfaces: `apps/caregiver-web`, `apps/studio-web`, and `apps/child-app`
- Legacy surfaces still present for migration reference: `apps/web`, `apps/api`, `apps/ai-service`
- Child runtime status: Expo shell is bootstrapped and wired to shared reading contracts plus shared SDK services
- Storage status: placeholder OSS contract exists, real object storage integration is intentionally deferred
- Legacy concept and PoC documents: archived under `docs/archive/`

## Foundations completed

- V2 strategy has been reframed around an iPad-first child reading product, with caregiver and studio surfaces on web.
- Runtime content is now defined as versioned `StoryPackage` distribution payloads instead of unconstrained real-time generation.
- Shared schema authority is in place for caregiver read models, reading session commands, reading event ingestion, story package delivery, and safety audit governance.
- Shared SDK services now provide a single API client, caregiver subdomain services, reading application services, demo payload builders, and a placeholder OSS storage adapter.
- `apps/caregiver-web` and `apps/studio-web` already consume shared contracts and shared application services instead of inventing page-local shapes.
- `apps/child-app` is now bootstrapped as an Expo workspace app and directly consumes shared `StoryPackage`, `ReadingSession`, and `ReadingEvent` application services.
- Contract tests and SDK self-checks already validate the current bootstrap payloads against the shared schemas.
- Legacy docs have been moved under `docs/archive/`, so the repo now has a clean active-docs area.

## Milestone history

- `f81fbbf` `feat(api): add placeholder oss storage adapter`
  Added a stable placeholder object storage interface so apps and shared services can depend on storage semantics before real OSS details are chosen.
- `386d468` `refactor(caregiver-web): split subdomain page services`
  Began separating caregiver page data access away from page-local coupling.
- `20b8172` `feat(caregiver): add subdomain read models and contracts`
  Added explicit caregiver household, child, plan, and progress read models plus formal contracts.
- `872d046` `test(contracts): validate caregiver read models and bootstrap studio shell`
  Added contract validation coverage and started the minimal studio surface.
- `75b9738` `refactor(sdk): share caregiver subdomain services and demo models`
  Moved caregiver shared logic into the SDK and established reusable demo contract payloads.
- `2916f6b` `feat(sdk): share reading application services`
  Added shared application-level services for story package lookup, reading session mutation, and reading event ingestion.
- `18d7f3d` `test(contracts): add runtime command schemas and api coverage`
  Expanded schema coverage to runtime write contracts and API contract tests.
- `6042474` `test(sdk): add demo contract self-check`
  Added SDK self-check validation so demo and fallback payloads are continuously checked against the shared schemas.

## Verification baseline

The following checks have already passed on the current baseline:

- `pytest tests/test_caregiver_v2_contracts.py -q`
- `npm run test:contracts --workspace @lumosreading/sdk`
- `npx tsc -p packages/sdk/tsconfig.json --noEmit`
- `npm run build --workspace caregiver-web`
- `npm run build --workspace studio-web`
- `npm run typecheck --workspace child-app`
- `npm run build --workspace child-app`

## Current V2 decisions

- Contracts-first is the governing development principle.
- The target product surfaces are `child-app`, `caregiver-web`, and `studio-web`.
- The child runtime should eventually be iPad-first native, not a long-term web shell.
- Runtime should consume versioned `StoryPackage` payloads.
- AI should sit primarily in the content supply chain and adaptation workflow, not as the child runtime main loop.
- Shared business and application logic should live in `packages/contracts` or `packages/sdk`, not inside page components.
- Placeholder OSS behavior is acceptable for now as long as app-facing semantics remain stable.

## Known gaps

- Real caregiver-to-child assignment write flows and caregiver-side operating UI are not implemented yet.
- The current FastAPI layer is still a bootstrap/PoC boundary and not the final modular monolith described in `02-*`.
- Real persistence, real object storage, release workflow, and content packaging jobs are not implemented yet.
- Legacy `apps/web` still exists and should continue to be treated as a migration reference, not a target architecture.

## Current focus and next slices

- Execute the sequential seven-phase delivery plan defined in `docs/v2/04-engineering-delivery-plan.md`.
- Complete Phase 2 next: caregiver assignment mutations, caregiver-web assignment UI, and child-home refresh semantics.
- Replace bootstrap fallback/demo responses with real backend module implementations behind the same contracts.
- Continue reducing legacy `apps/web` responsibility until it can be retired from the V2 main path.

## Session update: 2026-03-31 Phase 0

- Re-read the V2 strategy, architecture blueprint, schema governance, apps governance, and activity log before starting execution.
- Confirmed the repo baseline is still aligned with the active V2 direction and that `master` is in sync with `origin/master` at the start of the session.
- Added `docs/v2/04-engineering-delivery-plan.md` as the authoritative sequential delivery plan for seven execution phases.
- Added `docs/v2/phase-tasks/` with one executable task playbook per phase from Phase 0 through Phase 6.
- Updated `docs/v2/README.md` so the new delivery plan and phase task docs are part of the active V2 documentation set.
- Locked the operating rule for the remainder of this execution run: each phase must implement code, pass QC, update this log, then commit and push before the next phase is considered complete.
- Ran Phase 0 QC against the new delivery plan, phase task docs, active docs index, and activity log; no blocking findings were identified.
- Recorded follow-up notes from QC: keep verification commands explicit per phase, treat later entitlement work as new contract scope, and continue logging phase gate outcomes directly in this file.
- Set the next recommended slice to Phase 1 child runtime stability, with emphasis on assignment-driven shelf loading, local persistence, buffered reading event delivery, and cold-start session recovery.

## Session update: 2026-03-31 Phase 1

- Completed the assignment-driven child shelf contract and API path around `child-home.v1`, so the child runtime now loads a real package queue instead of assuming one default package.
- Extended the shared SDK and child runtime bootstrap path to load child-home, persist home packages, cache package manifests locally, and resume a session snapshot after cold start.
- Added buffered event outbox persistence in `apps/child-app`, plus serialized queue writes and single-flight flush behavior so event retries do not clear unrelated buffered events.
- Added offline session fallback handling so a reading session can start and continue buffering telemetry even when the session create call fails once.
- Added runtime-specific self-check coverage in `apps/child-app` and extended SDK/API contract checks to cover English package language propagation.
- Closed a QC-blocking data correctness issue: `ReadingSessionCreateV2.language_mode` and `ReadingEventV1.language_mode` now inherit from the selected package rather than being hardcoded to `zh-CN`.
- Aligned demo progress payloads and API progress fixtures so English packages now preserve `en-US` metadata through caregiver-facing telemetry surfaces.
- Verification passed for Phase 1 with `pytest tests/test_caregiver_v2_contracts.py -q`, `npm run test:contracts --workspace @lumosreading/sdk`, `npm run test:runtime-contracts --workspace child-app`, `npm run typecheck --workspace child-app`, and `npm run build --workspace child-app`.
- Phase 1 QC gate is cleared after the language metadata blocker and event outbox concurrency blocker were both resolved; the next recommended slice is Phase 2 caregiver assignment loop delivery.

## Session update: 2026-03-17

- Reconfirmed the V2 authority documents and current contracts-first repo direction.
- Added this mandatory activity log as part of the active documentation set.
- Rewrote `docs/README.md`, `docs/v2/README.md`, and `apps/README.md` into clean governance entrypoints.
- Wired the activity log into the official read-before-work order across docs and contracts.
- Preserved the current baseline as the starting point for subsequent business-logic slices.
- Bootstrapped `apps/child-app` with Expo SDK 55 and React Native, using the official monorepo-compatible app foundation.
- Replaced the Expo tutorial screens with a child runtime shell that loads a shared `StoryPackage`, starts a shared reading session, and ingests shared reading events.
- Added runtime-mode switching so the child app can default to demo mode and optionally use the shared API client with `EXPO_PUBLIC_*` environment variables.
- Removed unused Expo template tutorial components and assets so the child app workspace now reflects product structure rather than scaffold leftovers.
- Verified the child app with `npm run typecheck --workspace child-app` and `npm run build --workspace child-app`.
- Added a runtime provider plus routed `home -> package -> session` flow so the child app now has a real internal navigation model instead of a single bootstrap page.
- Added dynamic package preview and session screens that reuse the shared reading contracts and keep activity history inside the child runtime context.
- Installed `expo-asset` and `expo-audio` in `apps/child-app` so runtime media can be preloaded and played through the official Expo SDK 55 path.
- Added a bundled local demo audio asset under `apps/child-app/assets/audio/` so demo mode no longer depends on placeholder OSS media URLs to exercise playback.
- Expanded shared SDK demo packages from single-page placeholders into multi-page `StoryPackage` payloads, while keeping the same shared `story-package.v1` contract.
- Extended `apps/child-app/src/lib/runtime.ts` with runtime page resolution, bundled media fallback selection, and typed asset preload helpers.
- Reworked the child runtime provider so page progression, preload state, audio playback control, and runtime event ingestion now live in one shared session-state layer.
- Rebuilt the session route into a true reading surface with page turns, preload visibility, read-to-me controls, vocabulary reveal, and session completion on top of the shared runtime provider.
- Re-verified the new slice with `npm run typecheck --workspace child-app`, `npm run build --workspace child-app`, `npm run test:contracts --workspace @lumosreading/sdk`, and `npx tsc -p packages/sdk/tsconfig.json --noEmit`.
