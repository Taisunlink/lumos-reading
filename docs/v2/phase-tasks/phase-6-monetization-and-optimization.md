# Phase 6: Monetization and Optimization

Updated: 2026-03-31

## Objective

Close the access control, reporting, and optimization loop required for sustained product use.

## In scope

- Entitlements
- Subscription state
- Access control on package delivery and assignment
- Weekly report improvements
- Experiment-safe operational metrics

## Out of scope

- School LMS integrations
- Social features
- Large-scale recommendations redesign

## Tasks

- [x] Define entitlement, weekly value, and ops metrics contracts
- [x] Add entitlement-aware package access rules in API and SDK
- [x] Surface subscription, locked-package visibility, and weekly value in caregiver-web
- [x] Expand weekly reports with value-oriented metrics
- [x] Add experiment-safe instrumentation for blocked requests, entitled deliveries, and reuse signals
- [x] Add tests for access control and reporting

## Delivered slice

- Household-scoped entitlement contract plus caregiver endpoint
- Child-scoped package delivery endpoint gated by current household access
- Assignment rejection for locked packages with explicit access-denied semantics
- Weekly value report derived from shared reading events
- Studio operations page for access, value, and ops metrics visibility
- Demo fallback alignment so child-home and caregiver plan exclude locked packages while entitlement surfaces still show them
- Read-model fallback alignment so loss of entitlement rebinds current and featured package views to the remaining entitled queue instead of leaking raw package fixtures
- Zero-entitlement guardrails so package-bearing caregiver and child read surfaces return access-lost semantics instead of crashing or emitting invalid empty package payloads

## Verification

- [x] `npm run test:contracts --workspace @lumosreading/sdk`
- [x] `pytest tests/test_story_generation_v2.py -q`
- [x] `pytest tests/test_story_package_release_v2.py -q`
- [x] `pytest tests/test_monetization_v2.py -q`
- [x] `pytest tests/test_caregiver_v2_contracts.py -q`
- [x] `npm run build --workspace caregiver-web`
- [x] `npm run build --workspace studio-web`
- [x] `npm run typecheck --workspace child-app`
- [x] `npm run build --workspace child-app`

## QC gate

- [x] Paid or trial access state is reflected consistently across caregiver, child runtime, and studio surfaces
- [x] Weekly report value is tied to completed reading behavior
- [x] Metrics additions do not bypass shared event and contract semantics
- [x] Previously visible packages that lose entitlement no longer leak through child-home, caregiver household, caregiver children, or caregiver dashboard read models
- [x] Zero-entitlement households no longer crash package-bearing read surfaces or emit contract-invalid empty package queues
