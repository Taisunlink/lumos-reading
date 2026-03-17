# Documentation Governance

This repository now follows a V2 active-docs governance model.

## Authority model

- `docs/v2/` is the only active product and architecture authority.
- `packages/contracts/schemas/` is the formal shared contract authority.
- `docs/archive/` stores legacy PoC, historical planning, and non-authoritative reference material.

## Required session start order

Before starting any development session, read in this order:

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `docs/v2/03-activity-log.md`
4. `packages/contracts/schemas/README.md`
5. `apps/README.md`
6. `packages/contracts/README.md`

## Required session close workflow

- Update `docs/v2/03-activity-log.md` after each meaningful development session.
- If product strategy, target user, market position, or research assumptions change, update `docs/v2/01-*` first.
- If architecture, domain model, API semantics, event semantics, or migration rules change, update `docs/v2/02-*` first.
- If shared fields or payload shapes change, update the matching files in `packages/contracts/schemas/` in the same change.
- Do not use archived PoC documents as implementation authority.

## Archive policy

- `docs/archive/legacy-docs/` keeps historical concept, product, methodology, and implementation documents.
- `docs/archive/root-docs/` keeps legacy root-level reports, phase summaries, and temporary execution guides.
- Archived files can be mined for ideas or migration clues, but they do not define V2 behavior.
