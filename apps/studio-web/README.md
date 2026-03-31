# studio-web

Phase 4 V2 studio operations console.

## Current goal

- Make `studio-web` the authoritative operator surface for package review, publish, recall, and rollback.
- Reuse shared package release semantics from `@lumosreading/sdk`, not page-local aggregates.
- Keep runtime traceability visible: active runtime content must be explainable through review and release history.

## Current implementation

- Next.js App Router multi-page console with routes for `/`, `/packages`, `/releases`, and `/audits`
- Shared navigation shell and release-domain hooks built on top of `createStoryPackageReleaseServices`
- Consumes the Phase 3 API surface:
  - `GET /api/v2/story-packages`
  - `GET /api/v2/story-packages/{package_id}/history`
  - build / release / recall / rollback commands under `/api/v2/story-packages/{package_id}:*`
- Uses shared release-domain view models so pages receive package preview, audit evidence, operator notes, build history, and release history without rebuilding those semantics locally

## Phase 4 scope

- Draft list
- Package detail
- Safety audit visibility
- Publish and recall actions
- Release history and rollback controls

## Later scope

- AI brief and generation workflow visibility
- Rich editorial editing
- Entitlements and business analytics overlays
