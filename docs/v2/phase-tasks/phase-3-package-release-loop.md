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

- [ ] Define package draft, package build, and release contracts
- [ ] Create `apps/workers` runtime skeleton and packaging jobs
- [ ] Add API endpoints for draft listing, build trigger, release, recall, and history
- [ ] Add shared SDK client methods for package and release operations
- [ ] Persist package and release state in a repo-local bootstrap store
- [ ] Add tests covering build and release flows

## Verification

- [ ] `pytest tests/test_caregiver_v2_contracts.py -q`
- [ ] package and release API tests pass
- [ ] `npm run test:contracts --workspace @lumosreading/sdk`
- [ ] affected app builds pass

## QC gate

- [ ] Draft to release creates a stable runtime package record
- [ ] Release history is queryable
- [ ] Recall and rollback do not break package lookup semantics
