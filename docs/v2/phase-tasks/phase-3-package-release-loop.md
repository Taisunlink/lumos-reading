# Phase 3: Package Build and Release Loop

Updated: 2026-03-31

## Objective

Create a versioned build and release path for `StoryPackage` artifacts.

## In scope

- Package source records
- Build job records
- Release records
- Recall and rollback actions
- Stable object storage resolution semantics

## Out of scope

- Full editorial UI
- Advanced search and recommendation
- Fine-tuned model hosting

## Tasks

- [x] Define package draft, package build, and release contracts
- [x] Create `apps/workers` runtime skeleton and packaging jobs
- [x] Add API endpoints for draft listing, build trigger, release, recall, rollback, and history
- [x] Add shared SDK client methods for package and release operations
- [x] Persist package and release state in a repo-local bootstrap seed/runtime store
- [x] Add tests covering build and release flows

## Verification

- [x] `pytest tests/test_caregiver_v2_contracts.py -q`
- [x] `pytest tests/test_story_package_release_v2.py -q`
- [x] `npm run test:contracts --workspace @lumosreading/sdk`
- [x] `npm run build --workspace studio-web`
- [x] `npm run build --workspace caregiver-web`
- [x] `npm run build --workspace child-app`

## QC gate

- [x] Draft to release creates a stable runtime package record
- [x] Release history is queryable
- [x] Recall and rollback do not break package lookup semantics
