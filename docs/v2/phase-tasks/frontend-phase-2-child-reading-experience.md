# Frontend Phase 2: Child Reading Experience

Updated: 2026-03-31

## Objective

Upgrade the child runtime from technically stable to emotionally coherent and habit-friendly.

## In Scope

- child home shelf
- continue reading flow
- reading session chrome and transitions
- child-friendly empty, reconnect, and completion states
- child-facing microcopy for start, pause, return, and finish

## Out Of Scope

- New content generation capabilities
- Paid conversion surfaces
- Studio workflow redesign

## Tasks

- [ ] Redesign the child home hierarchy so continue reading and next recommended package are obvious
- [ ] Improve reading session structure, progress cues, and return-to-reading behavior
- [ ] Define and implement child-friendly offline, reconnect, and no-content states
- [ ] Add completion and celebration language that supports calm repeat use rather than pressure
- [ ] Document the child journey for first open, interrupted session, resume, and session completion
- [ ] Verify that runtime copy remains consistent with actual API and contract states

## Expected Outputs

- improved child journey map
- polished home and session surface
- child-facing copy inventory
- state behavior notes for interruption and recovery

## Verification

- [ ] `npm run typecheck --workspace child-app`
- [ ] `npm run build --workspace child-app`
- [ ] `npm run test:contracts --workspace @lumosreading/sdk` if shared runtime payloads or copy-driven state semantics change

## QC Gate

- [ ] A child can start, continue, and complete reading with a clear and low-friction flow
- [ ] Child-facing copy is short, warm, and non-instructional in tone
- [ ] Offline and interrupted states degrade cleanly instead of feeling like failure screens
