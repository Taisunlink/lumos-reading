# Phase 5: AI Content Supply Chain V1

Updated: 2026-03-31

## Objective

Introduce AI-assisted draft generation and media generation as backstage tooling.

## In scope

- Brief records
- Generation jobs
- Illustration provider selection
- Draft assembly
- Review checkpoints

## Out of scope

- Live child-facing generation
- Self-hosted GPU production
- Fine-tune infrastructure

## Tasks

- [ ] Define brief and generation job contracts
- [ ] Reuse and normalize current illustration provider abstractions
- [ ] Create worker jobs for brief to draft and draft to media generation
- [ ] Persist generation outputs as reviewable package drafts
- [ ] Surface generated draft state in studio-web
- [ ] Add provider fallback and failure reporting
- [ ] Add tests for generation orchestration without requiring live provider credentials

## Verification

- [ ] worker tests pass
- [ ] package draft APIs pass
- [ ] `npm run build --workspace studio-web`
- [ ] relevant Python tests pass

## QC gate

- [ ] AI output enters the system only as draft or reviewable content
- [ ] Provider failures do not corrupt package records
- [ ] Runtime still consumes only approved released packages
