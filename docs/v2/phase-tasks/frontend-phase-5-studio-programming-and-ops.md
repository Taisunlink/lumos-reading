# Frontend Phase 5: Studio Programming And Ops

Updated: 2026-03-31

## Objective

Improve studio-web so editorial and operations teams can plan, review, and release content with clearer programming context.

## In Scope

- briefs, packages, releases, and operations navigation
- editorial and operator-facing labels
- programming and release cadence visibility
- campaign or thematic grouping rules
- operator checklist and exception messaging

## Out Of Scope

- New AI generation model integrations
- Replacing the release domain
- BI warehouse implementation

## Tasks

- [ ] Rework studio navigation and page hierarchy around the operator jobs that happen most often
- [ ] Clarify review, release, recall, and operational metric labels so states are understandable without engineering context
- [ ] Add product-programming context for weekly themes, release groups, or campaign bundles
- [ ] Write operator checklist copy for review, release, rollback, and exception handling
- [ ] Document content programming cadence, release rhythm, and campaign planning assumptions
- [ ] Ensure studio-facing copy remains aligned with actual workflow states and audit gates

## Expected Outputs

- studio IA update
- operator copy pack
- programming cadence doc
- release and exception checklist

## Verification

- [ ] `npm run build --workspace studio-web`
- [ ] relevant API or contract tests pass if operator-facing workflow states change

## QC Gate

- [ ] Operators can understand what needs review, what is ready, and what is blocked
- [ ] Editorial programming can be explained from the repo without side spreadsheets
- [ ] Studio labels and status language match backend workflow semantics
