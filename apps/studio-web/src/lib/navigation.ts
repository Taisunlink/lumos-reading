export const studioNavItems = [
  {
    href: "/",
    label: "Overview",
    description: "Live release-state overview, queue health, and operator handoff context.",
  },
  {
    href: "/packages",
    label: "Packages",
    description: "Draft cards, package detail, build trigger, and publish controls.",
  },
  {
    href: "/briefs",
    label: "Briefs",
    description: "Editorial briefs, AI generation jobs, and provider fallback visibility.",
  },
  {
    href: "/releases",
    label: "Releases",
    description: "Active, recalled, and superseded release history with rollback controls.",
  },
  {
    href: "/audits",
    label: "Audits",
    description: "Safety findings, review status, and traceability back to runtime packages.",
  },
  {
    href: "/operations",
    label: "Operations",
    description: "Access state, weekly value, and trial-to-paid operating metrics.",
  },
] as const;
