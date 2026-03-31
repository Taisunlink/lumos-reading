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

- [ ] Add caregiver assignment contracts and API endpoints
- [ ] Add caregiver assignment service methods in `packages/sdk`
- [ ] Update caregiver-web to assign packages to children
- [ ] Surface recent child reading status and package outcome
- [ ] Ensure child-app shelf refreshes assigned packages from caregiver changes
- [ ] Add tests for assignment and progress flow

## Verification

- [ ] `pytest tests/test_caregiver_v2_contracts.py -q`
- [ ] `npm run test:contracts --workspace @lumosreading/sdk`
- [ ] `npm run build --workspace caregiver-web`
- [ ] `npm run build --workspace child-app`

## QC gate

- [ ] A caregiver assignment changes the child shelf
- [ ] Completed child sessions appear in caregiver progress
- [ ] No page invents its own payload shape outside shared contracts
