# Apps

This directory contains both remaining legacy PoC apps and the V2 target surfaces.

## Current V2 surfaces

- `caregiver-web/`
  Active caregiver-facing web surface. It already consumes `@lumosreading/contracts` and `@lumosreading/sdk`.
- `studio-web/`
  Active minimal studio and operations shell. It already consumes shared contracts and shared application services.
- `child-app/`
  Bootstrapped Expo and React Native child runtime shell. It already consumes shared reading contracts and shared application services.
- `workers/`
  Planned async jobs boundary for packaging, TTS, safety review, release, and other offline workflows.

## Current bootstrap and legacy surfaces

- `api/`
  Current FastAPI bootstrap layer used for contract coverage and migration scaffolding. It is not yet the final V2 modular monolith.
- `web/`
  Legacy demo reader. It should be treated as a migration reference, not as the V2 target app.
- `ai-service/`
  Legacy AI orchestration and experimentation area. Keep useful supply-chain logic and quality ideas, but do not treat it as child runtime authority.

## Required read order

Before starting any app work, read in this order:

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `docs/v2/03-activity-log.md`
4. `packages/contracts/schemas/README.md`
5. This file
6. `packages/contracts/README.md`

## Working rules

- New business capabilities should land in V2 surfaces or shared packages.
- Shared payloads and versioned schemas belong in `packages/contracts`.
- Shared API access and application/service composition belong in `packages/sdk` unless a more specific shared package is introduced.
- Legacy app code may inform migration, but it must not define the target design.
