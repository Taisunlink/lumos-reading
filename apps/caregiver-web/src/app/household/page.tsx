"use client";

import {
  CAREGIVER_DASHBOARD_SCHEMA_VERSION,
  READING_EVENT_SCHEMA_VERSION,
  SAFETY_AUDIT_SCHEMA_VERSION,
  STORY_PACKAGE_SCHEMA_VERSION,
  caregiverDashboardV1Schema,
  readingEventV1Schema,
  safetyAuditV1Schema,
  storyPackageV1Schema,
} from "@lumosreading/contracts";
import { ApiWorkbench } from "@/components/api-workbench";
import { ConnectedPackagePanel } from "@/components/connected-package-panel";
import { useHouseholdOverview } from "@/lib/hooks/use-household-overview";
import { startupOrder } from "@/lib/page-models";

const contractCards = [
  {
    name: "Caregiver Dashboard",
    version: CAREGIVER_DASHBOARD_SCHEMA_VERSION,
    title: String(caregiverDashboardV1Schema.title ?? ""),
    requiredCount: Array.isArray(caregiverDashboardV1Schema.required)
      ? caregiverDashboardV1Schema.required.length
      : 0,
    tone: "soft-card--sky",
  },
  {
    name: "Story Package",
    version: STORY_PACKAGE_SCHEMA_VERSION,
    title: String(storyPackageV1Schema.title ?? ""),
    requiredCount: Array.isArray(storyPackageV1Schema.required)
      ? storyPackageV1Schema.required.length
      : 0,
    tone: "soft-card--warm",
  },
  {
    name: "Reading Event",
    version: READING_EVENT_SCHEMA_VERSION,
    title: String(readingEventV1Schema.title ?? ""),
    requiredCount: Array.isArray(readingEventV1Schema.required)
      ? readingEventV1Schema.required.length
      : 0,
    tone: "soft-card--green",
  },
  {
    name: "Safety Audit",
    version: SAFETY_AUDIT_SCHEMA_VERSION,
    title: String(safetyAuditV1Schema.title ?? ""),
    requiredCount: Array.isArray(safetyAuditV1Schema.required)
      ? safetyAuditV1Schema.required.length
      : 0,
    tone: "soft-card--ink",
  },
];

const operatingLanes = [
  {
    name: "Household Service",
    status: "Now",
    description: "The household route owns featured package selection, queue visibility, and operator startup checks.",
    tone: "is-green",
  },
  {
    name: "Child Service",
    status: "Live",
    description: "Assignments and support signals are split into a dedicated child domain page model.",
    tone: "is-sky",
  },
  {
    name: "Plan + Progress",
    status: "Live",
    description: "Weekly cadence and event analytics now resolve through their own subdomain hooks, not raw page access.",
    tone: "is-warm",
  },
];

export default function HouseholdPage() {
  const { overview, status, error } = useHouseholdOverview();

  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Household operating surface</div>
        <h1>Run the caregiver loop from a household domain, not from a demo dashboard blob.</h1>
        <p className="hero-card__lead">
          This route is now the contracts-first operating entrypoint for caregiver planning. The layout hydrates one
          shared dashboard source, then each page consumes a subdomain service model instead of reading aggregate
          payload fields directly.
        </p>
        <div className="badge-row">
          <span className="badge is-warm">desktop first</span>
          <span className="badge is-green">ipad child app next</span>
          <span className="badge is-sky">placeholder oss aligned</span>
          <span className={`badge ${status === "live" ? "is-green" : status === "loading" ? "is-sky" : "is-warm"}`}>
            {status === "live" ? "live household model" : status === "loading" ? "syncing household model" : "fallback household model"}
          </span>
        </div>
        {error ? <div className="note-card">{error}</div> : null}
        <div className="metrics-grid">
          <article className="metric-card">
            <div className="metric-card__label">Household</div>
            <div className="metric-card__value">{overview.householdName}</div>
            <div className="metric-card__meta">Current contracts-first pilot household identifier: {overview.householdId}</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Children in household</div>
            <div className="metric-card__value">{overview.childCount}</div>
            <div className="metric-card__meta">Profiles already tied to a current package assignment.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Package queue</div>
            <div className="metric-card__value">{overview.packageCount}</div>
            <div className="metric-card__meta">Versioned packages staged for plan construction and distribution.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Completed / reveal</div>
            <div className="metric-card__value">
              {overview.completedSessions} / {overview.translationReveals}
            </div>
            <div className="metric-card__meta">Session completions and bilingual reveal demand from typed events.</div>
          </article>
        </div>
      </section>

      <section className="card-grid">
        {operatingLanes.map((lane) => (
          <article key={lane.name} className="soft-card">
            <div className="panel-card__header">
              <strong className="list-row__title">{lane.name}</strong>
              <span className={`badge ${lane.tone}`.trim()}>{lane.status}</span>
            </div>
            <p>{lane.description}</p>
          </article>
        ))}
      </section>

      <section className="split-grid">
        <ConnectedPackagePanel overview={overview} status={status} error={error} />

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Shared contracts</h2>
            <span className="panel-card__eyebrow">Directly from shared package</span>
          </div>
          <div className="stack-list">
            {contractCards.map((card) => (
              <article key={card.name} className={`soft-card ${card.tone}`}>
                <p className="list-row__title">{card.name}</p>
                <div className="list-row__meta">
                  <span className="mono">{card.version}</span>
                  <span>{card.title}</span>
                </div>
                <p className="metric-card__meta">Required fields: {card.requiredCount}</p>
              </article>
            ))}
          </div>
        </article>
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <h2>API workbench</h2>
            <span className="panel-card__eyebrow">Manual validation against /api/v2</span>
          </div>
          <ApiWorkbench />
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Operating order</h2>
            <span className="panel-card__eyebrow">Session bootstrap</span>
          </div>
          <div className="stack-list">
            {startupOrder.map((item, index) => (
              <article key={item} className="list-row">
                <p className="list-row__title">
                  {index + 1}. <code>{item}</code>
                </p>
              </article>
            ))}
          </div>
          <div className="note-card">
            Extend contracts and <code>/api/v2</code> first. Keep page logic reading from subdomain hooks instead of
            stitching aggregate fields in the route component.
          </div>
        </article>
      </section>
    </main>
  );
}
