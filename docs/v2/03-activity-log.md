# V2 Activity Log

Updated: 2026-03-17

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
- Active V2 surfaces: `apps/caregiver-web` and `apps/studio-web`
- Legacy surfaces still present for migration reference: `apps/web`, `apps/api`, `apps/ai-service`
- Child runtime status: `apps/child-app` is still not bootstrapped
- Storage status: placeholder OSS contract exists, real object storage integration is intentionally deferred
- Legacy concept and PoC documents: archived under `docs/archive/`

## Foundations completed

- V2 strategy has been reframed around an iPad-first child reading product, with caregiver and studio surfaces on web.
- Runtime content is now defined as versioned `StoryPackage` distribution payloads instead of unconstrained real-time generation.
- Shared schema authority is in place for caregiver read models, reading session commands, reading event ingestion, story package delivery, and safety audit governance.
- Shared SDK services now provide a single API client, caregiver subdomain services, reading application services, demo payload builders, and a placeholder OSS storage adapter.
- `apps/caregiver-web` and `apps/studio-web` already consume shared contracts and shared application services instead of inventing page-local shapes.
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

## Current V2 decisions

- Contracts-first is the governing development principle.
- The target product surfaces are `child-app`, `caregiver-web`, and `studio-web`.
- The child runtime should eventually be iPad-first native, not a long-term web shell.
- Runtime should consume versioned `StoryPackage` payloads.
- AI should sit primarily in the content supply chain and adaptation workflow, not as the child runtime main loop.
- Shared business and application logic should live in `packages/contracts` or `packages/sdk`, not inside page components.
- Placeholder OSS behavior is acceptable for now as long as app-facing semantics remain stable.

## Known gaps

- `apps/child-app` does not exist yet.
- The current FastAPI layer is still a bootstrap/PoC boundary and not the final modular monolith described in `02-*`.
- Real persistence, real object storage, release workflow, and content packaging jobs are not implemented yet.
- Legacy `apps/web` still exists and should continue to be treated as a migration reference, not a target architecture.

## Current focus and next slices

- Keep extracting shared logic out of app-local code into `packages/contracts` and `packages/sdk`.
- Build the eventual child runtime on top of the existing `StoryPackage`, reading session, and reading event contracts.
- Replace bootstrap fallback/demo responses with real backend module implementations behind the same contracts.
- Continue reducing legacy `apps/web` responsibility until it can be retired from the V2 main path.

## Session update: 2026-03-17

- Reconfirmed the V2 authority documents and current contracts-first repo direction.
- Added this mandatory activity log as part of the active documentation set.
- Rewrote `docs/README.md`, `docs/v2/README.md`, and `apps/README.md` into clean governance entrypoints.
- Wired the activity log into the official read-before-work order across docs and contracts.
- Preserved the current baseline as the starting point for subsequent business-logic slices.
