# Frontend Phase 1: Experience Foundation

Updated: 2026-03-31

## Objective

Create one shared experience baseline across child, caregiver, and studio surfaces before larger UI polish begins.

## In Scope

- Screen and route inventory
- Navigation hierarchy by surface
- Shared state inventory for loading, empty, error, locked, success
- Product copy tone guide
- Local and remote handoff format

## Out Of Scope

- Full redesign of any surface
- New backend capabilities
- Final launch assets

## Tasks

- [ ] Audit all active child, caregiver, and studio routes and record page purpose plus primary CTA
- [ ] Define a canonical navigation hierarchy for each active surface
- [ ] Define shared state language for loading, empty, error, locked, success, and completion moments
- [ ] Write a copy tone guide for child-facing, caregiver-facing, and operator-facing language
- [ ] Create a screen ownership and handoff template so a remote teammate can continue work from repo docs alone
- [ ] Update active docs so the new frontend/productization plan becomes part of the required read order

## Expected Outputs

- route inventory table
- experience language baseline
- copy style guide
- handoff template

## Verification

- [ ] `docs/v2/05-frontend-experience-and-content-delivery-plan.md` is aligned with the phase task files
- [ ] `docs/v2/README.md`, `docs/v2/phase-tasks/README.md`, and `docs/v2/03-activity-log.md` are updated
- [ ] affected app builds pass if navigation or shared layout code changes

## QC Gate

- [ ] Every active route has a documented purpose, owner, and primary CTA
- [ ] Shared state language is consistent across all three audiences
- [ ] The repo contains enough handoff detail for local or remote continuation without extra verbal context
