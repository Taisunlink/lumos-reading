# Phase 1: Child Runtime Stable Reading Loop

Updated: 2026-03-31

## Objective

Make the child runtime resilient enough for real reading sessions instead of demo-only use.

## In scope

- Assignment-driven child home shelf
- Local package manifest cache
- Session persistence and cold-start resume
- Buffered reading event queue with retry
- Multi-page API story package fixtures

## Out of scope

- Caregiver assignment UI
- Studio release tooling
- Real object storage authorization
- Live AI generation

## Tasks

- [ ] Add child-home or equivalent assigned-shelf API contract and endpoint
- [ ] Extend shared SDK with child-home lookup semantics
- [ ] Persist runtime state in `apps/child-app`
- [ ] Restore active session state on cold start
- [ ] Queue reading events locally before upload
- [ ] Retry or flush pending reading events on runtime start and phase transitions
- [ ] Upgrade API story package fixtures to multi-page payloads
- [ ] Add contract and behavior tests for the new flow

## Verification

- [ ] `pytest tests/test_caregiver_v2_contracts.py -q`
- [ ] `npm run test:contracts --workspace @lumosreading/sdk`
- [ ] `npm run typecheck --workspace child-app`
- [ ] `npm run build --workspace child-app`

## QC gate

- [ ] Child shelf is not hardcoded to one default package in API mode
- [ ] Active session survives app restart
- [ ] Reading completion is not lost when event upload fails once
- [ ] API mode can exercise a real multi-page package
