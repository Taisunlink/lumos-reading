# Phase 5: AI Content Supply Chain V1

Updated: 2026-03-31

## Objective

Introduce AI-assisted draft generation and media generation as backstage tooling.

## In scope

- Brief records
- Generation jobs
- Illustration provider selection
- Draft assembly
- Review checkpoints

## Out of scope

- Live child-facing generation
- Self-hosted GPU production
- Fine-tune infrastructure

## Tasks

- [x] Define brief and generation job contracts
- [x] Reuse and normalize current illustration provider abstractions
- [x] Create worker jobs for brief to draft and draft to media generation
- [x] Persist generation outputs as reviewable package drafts
- [x] Surface generated draft state in studio-web
- [x] Add provider fallback and failure reporting
- [x] Add tests for generation orchestration without requiring live provider credentials

## Verification

- [x] worker tests pass
  Verified through `pytest tests/test_story_generation_v2.py -q` and deterministic helper coverage in `apps/workers/jobs/story_generation.py`.
- [x] package draft APIs pass
  Verified through `pytest tests/test_story_generation_v2.py -q` and `pytest tests/test_story_package_release_v2.py -q`.
- [x] `npm run build --workspace studio-web`
- [x] relevant Python tests pass
  Verified through `pytest tests/test_story_generation_v2.py -q`, `pytest tests/test_story_package_release_v2.py -q`, and `pytest tests/test_caregiver_v2_contracts.py -q`.

## QC gate

- [x] AI output enters the system only as draft or reviewable content
- [x] Provider failures do not corrupt package records
- [x] Runtime still consumes only approved released packages

## Delivery notes

- Phase 5 extends the repo-local release store instead of introducing a second generation-only store.
- Generated package drafts now share the same review, build, and release lifecycle as editorial drafts.
- Media generation records provider attempts and falls back to `placeholder` when live credentials are unavailable, so CI and local contract tests stay deterministic.
