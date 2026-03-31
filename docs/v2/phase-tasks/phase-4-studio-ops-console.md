# Phase 4: Studio Minimum Operations Console

Updated: 2026-03-31

## Objective

Turn studio-web into the operator surface for review and release control.

## In scope

- Draft list
- Package detail
- Safety audit status
- Publish and recall actions
- Release history visibility

## Out of scope

- Rich collaborative editor
- Enterprise permissions model
- Advanced analytics dashboard

## Tasks

- [x] Add studio-web navigation for drafts, releases, and audits
- [x] Display package draft state from Phase 3 APIs
- [x] Display safety audit findings and review status
- [x] Wire publish and recall actions
- [x] Add release history and operator notes visibility
- [x] Add build verification for studio-web
- [x] Enforce approved-audit release gating in the backend and studio publish and rollback surfaces

## Verification

- [x] `npm run build --workspace studio-web`
- [x] package and audit API tests pass
- [x] contract checks pass for any touched schema
- [x] `npm run build --workspace caregiver-web`

## QC gate

- [x] Operators can see which package is draft, released, or recalled
- [x] Runtime-visible packages can be traced back to a review state
- [x] Studio does not rely on page-local mocked aggregates

## Implementation notes

- `studio-web` now consumes shared release-domain hooks and shared SDK view models instead of caregiver page models.
- Publish and rollback are backend-gated and UI-gated by `safety_audit.audit_status == approved` plus `resolution.action == release`.
- Accepted follow-up: local seed/runtime data still skews toward approved/released samples, so later phases should add richer pending/rejected AI-draft fixtures.
