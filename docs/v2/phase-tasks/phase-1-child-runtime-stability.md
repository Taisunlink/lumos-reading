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

- [x] Add child-home or equivalent assigned-shelf API contract and endpoint
- [x] Extend shared SDK with child-home lookup semantics
- [x] Persist runtime state in `apps/child-app`
- [x] Restore active session state on cold start
- [x] Queue reading events locally before upload
- [x] Retry or flush pending reading events on runtime start and phase transitions
- [x] Upgrade API story package fixtures to multi-page payloads
- [x] Add contract and behavior tests for the new flow
- [x] Preserve `language_mode` from the selected package in session and event payloads

## Verification

- [x] `pytest tests/test_caregiver_v2_contracts.py -q`
- [x] `npm run test:contracts --workspace @lumosreading/sdk`
- [x] `npm run test:runtime-contracts --workspace child-app`
- [x] `npm run typecheck --workspace child-app`
- [x] `npm run build --workspace child-app`

## QC gate

- [x] Child shelf is not hardcoded to one default package in API mode
- [x] Active session survives app restart
- [x] Reading completion is not lost when event upload fails once
- [x] API mode can exercise a real multi-page package
- [x] Session and event `language_mode` follow the selected package instead of a hardcoded default
