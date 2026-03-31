# Frontend Phase 4: Access And Conversion

Updated: 2026-03-31

## Objective

Make trial, locked access, and paid value understandable and conversion-safe.

## In Scope

- access and membership surface
- locked and unavailable states
- upgrade messaging
- trial and expiry communication
- experiment hooks for conversion-safe iteration

## Out Of Scope

- Payment processor integration replacement
- School or institutional billing
- Full pricing strategy rewrite

## Tasks

- [ ] Redesign the access and membership surface so trial, entitled, and locked states are legible
- [ ] Define lock-state copy rules for caregiver and child surfaces
- [ ] Write benefit comparison and upgrade explanation copy that focuses on value and transparency
- [ ] Add trial progression, renewal, and expiry communication rules
- [ ] Define experiment-safe CTA areas and measurement points without breaking access semantics
- [ ] Document the trial-to-paid journey and edge cases such as expired and zero-entitlement households

## Expected Outputs

- access surface spec
- lock and upgrade copy matrix
- trial-to-paid journey map
- conversion and experiment checklist

## Verification

- [ ] `npm run build --workspace caregiver-web`
- [ ] `npm run build --workspace child-app` if child locked-state copy or routing changes
- [ ] relevant monetization and contract tests pass if access semantics change

## QC Gate

- [ ] A caregiver can understand why content is available or unavailable
- [ ] Upgrade prompts feel transparent rather than coercive
- [ ] Trial, expired, and zero-entitlement states are handled consistently across surfaces
