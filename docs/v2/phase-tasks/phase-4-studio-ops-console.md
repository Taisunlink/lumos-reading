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

- [ ] Add studio-web navigation for drafts, releases, and audits
- [ ] Display package draft state from Phase 3 APIs
- [ ] Display safety audit findings and review status
- [ ] Wire publish and recall actions
- [ ] Add release history and operator notes visibility
- [ ] Add build verification for studio-web

## Verification

- [ ] `npm run build --workspace studio-web`
- [ ] package and audit API tests pass
- [ ] contract checks pass for any touched schema

## QC gate

- [ ] Operators can see which package is draft, released, or recalled
- [ ] Runtime-visible packages can be traced back to a review state
- [ ] Studio does not rely on page-local mocked aggregates
