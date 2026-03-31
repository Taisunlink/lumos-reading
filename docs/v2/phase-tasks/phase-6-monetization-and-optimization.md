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

- [ ] Define entitlement and subscription contracts
- [ ] Add entitlement-aware package access rules in API and SDK
- [ ] Surface subscription and access state in caregiver-web
- [ ] Expand weekly reports with value-oriented metrics
- [ ] Add experiment-safe instrumentation for retention and reuse signals
- [ ] Add tests for access control and reporting

## Verification

- [ ] contract tests pass
- [ ] relevant API tests pass
- [ ] `npm run build --workspace caregiver-web`
- [ ] affected app builds pass

## QC gate

- [ ] Paid access state is reflected consistently across surfaces
- [ ] Weekly report value is tied to completed reading behavior
- [ ] Metrics additions do not bypass shared event and contract semantics
