# Frontend Phase 3: Caregiver Guidance And Growth

Updated: 2026-03-31

## Objective

Turn caregiver-web into a companion surface that explains progress, next steps, and weekly value.

## In Scope

- household overview
- child assignment framing
- plan and progress surfaces
- weekly value narrative
- caregiver guidance copy

## Out Of Scope

- New payment flows
- Studio editorial tooling
- Deep recommendation-model changes

## Tasks

- [ ] Rework the caregiver information hierarchy so household value and child status are visible at a glance
- [ ] Improve package assignment framing so caregivers understand why to assign a title now
- [ ] Rewrite progress and weekly-value surfaces into clearer narratives rather than raw metrics lists
- [ ] Add next-step guidance copy for common caregiver situations such as missed reading, rereads, and weekly completion
- [ ] Document the caregiver journey for first visit, mid-week check-in, and end-of-week reflection
- [ ] Align caregiver copy with actual entitlement, progress, and reading states returned by the platform

## Expected Outputs

- caregiver journey map
- dashboard and progress narrative spec
- caregiver copy pack
- weekly value framing rules

## Verification

- [ ] `npm run build --workspace caregiver-web`
- [ ] `npm run test:contracts --workspace @lumosreading/sdk` if shared caregiver read models or shared copy-driven states change
- [ ] relevant API contract tests pass if new caregiver state handling is introduced

## QC Gate

- [ ] A caregiver can understand what happened this week and what to do next
- [ ] Caregiver copy communicates support and trust, not dashboard noise
- [ ] Household, child, plan, and progress surfaces tell one coherent story
