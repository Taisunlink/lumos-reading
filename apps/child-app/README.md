# child-app

LumosReading V2 child runtime shell built with Expo and React Native.

## Current scope

- iPad-first child reading shell
- Direct consumption of `@lumosreading/contracts` and `@lumosreading/sdk`
- Default offline-safe demo runtime mode
- Shared `StoryPackage`, `ReadingSession`, and `ReadingEvent` contract usage
- Expo Router flow for `home -> package -> session`
- Multi-page reading session state with typed page progression
- Page asset preload via `expo-asset`
- Read-to-me audio playback via `expo-audio`
- Bundled local demo media so placeholder OSS URLs do not block runtime work

## Commands

```bash
npm install
npm run start --workspace child-app
npm run ios --workspace child-app
npm run web --workspace child-app
npm run typecheck --workspace child-app
```

## Runtime mode

The app defaults to demo mode so the child shell can be developed without relying on localhost API access from a device.

- `EXPO_PUBLIC_RUNTIME_MODE=demo`
  Use demo `StoryPackage` data and local accepted receipts.
- `EXPO_PUBLIC_RUNTIME_MODE=api`
  Use the shared API client and real backend endpoints.

When using API mode, also set:

- `EXPO_PUBLIC_API_BASE_URL`
- `EXPO_PUBLIC_DEFAULT_CHILD_ID` (optional)
- `EXPO_PUBLIC_DEFAULT_STORY_PACKAGE_ID` (optional)

## Current route slices

- `/`
  Child home shelf with featured package and package queue.
- `/packages/[packageId]`
  Story package preview and session handoff.
- `/session/[sessionId]`
  Active reading session shell with page progression, asset preload state, and read-to-me controls.

## Demo runtime media

In demo mode the app resolves package media to bundled local assets inside this workspace:

- `assets/images/icon.png`
- `assets/images/splash-icon.png`
- `assets/audio/demo-page.wav`

This keeps the runtime flow stable while real object storage, signed URLs, and package caching are
still placeholder-backed.

## Read order

Before changing this app, read:

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `docs/v2/03-activity-log.md`
4. `packages/contracts/schemas/README.md`
5. `apps/README.md`
6. `packages/contracts/README.md`
