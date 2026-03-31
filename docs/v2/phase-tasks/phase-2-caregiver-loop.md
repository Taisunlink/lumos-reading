# Phase 2: Caregiver Assignment and Feedback Loop

Updated: 2026-03-31

## Objective

Let caregivers assign content and see the resulting reading activity.

## In scope

- Child assignment mutations
- Caregiver child profile editing where needed
- Recent reading status
- Weekly progress summary grounded in actual events

## Out of scope

- Full subscription flow
- Studio review workflows
- AI brief generation

## Tasks

- [x] Add caregiver assignment contracts and API endpoints
- [x] Add caregiver assignment service methods in `packages/sdk`
- [x] Update caregiver-web to assign packages to children
- [x] Surface recent child reading status and package outcome
- [x] Ensure child-app shelf refreshes assigned packages from caregiver changes
- [x] Add tests for assignment and progress flow
- [x] Persist newly ingested reading events into caregiver progress readbacks

## Verification

- [x] `pytest tests/test_caregiver_v2_contracts.py -q`
- [x] `npm run test:contracts --workspace @lumosreading/sdk`
- [x] `npm run test:runtime-contracts --workspace child-app`
- [x] `npm run build --workspace caregiver-web`
- [x] `npm run typecheck --workspace child-app`
- [x] `npm run build --workspace child-app`

## QC gate

- [x] A caregiver assignment changes the child shelf
- [x] Completed child sessions appear in caregiver progress
- [x] No page invents its own payload shape outside shared contracts
- [x] Child runtime can resync caregiver assignments without a reinstall or cache reset
