# studio-web

Minimal V2 Studio / CMS / Ops Web shell.

## Current goal

- Prove that a second surface outside `caregiver-web` can consume shared subdomain read models
- Directly consume `CaregiverPlanV1` and `CaregiverProgressV1`
- Keep the shell lightweight while the full Studio domain is still being designed

## Current implementation

- Next.js App Router minimal shell
- Consumes `@lumosreading/contracts` and shared subdomain services from `@lumosreading/sdk`
- Calls `/api/v2/caregiver/households/{householdId}/plan`
- Calls `/api/v2/caregiver/households/{householdId}/progress`
- Reuses the shared placeholder OSS contract instead of hardcoding asset URLs inside the app

## Later scope

- Topic, variant, audit, publish, rollback
- Safety review and experiment configuration
- Content supply chain visibility
