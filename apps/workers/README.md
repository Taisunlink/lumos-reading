# workers

V2 worker boundary for packaging, generation, and review jobs.

## Current scope

- Story package build helpers
- AI brief-to-draft orchestration stubs
- Media generation provider adapters
- Safety scan and release-job handoff

## Phase 3 baseline

- `jobs/story_package.py`
  Pure packaging helper that rewrites runtime asset URLs into versioned object-storage paths.
- The API currently executes the Phase 3 build loop synchronously against the same helper.
- Later phases can move the same job contract behind a real queue without changing release semantics.
