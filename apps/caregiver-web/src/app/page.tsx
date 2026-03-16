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
import { useCaregiverDashboard } from "@/lib/hooks/use-caregiver-dashboard";
import { demoHouseholdId, fallbackCaregiverDashboard, startupOrder } from "@/lib/page-models";

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
    name: "Caregiver Web",
    status: "Now",
    description: "Selection, planning, progress review, and contract validation sit here first.",
    tone: "is-green",
  },
  {
    name: "Child App",
    status: "Next",
    description: "The iPad-first reading surface will consume versioned story packages instead of live generation.",
    tone: "is-sky",
  },
  {
    name: "Studio Web",
    status: "Later",
    description: "Editorial, review, release, rollback, and experimentation live on a separate operating surface.",
    tone: "",
  },
];

export default function CaregiverHomePage() {
  const { dashboard, status, error } = useCaregiverDashboard(
    demoHouseholdId,
    fallbackCaregiverDashboard,
  );

  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Contracts-first caregiver surface</div>
        <h1>Plan the household reading loop before the child app ships.</h1>
        <p className="hero-card__lead">
          This shell is the new working entrypoint for V2. It consumes{" "}
          <code>@lumosreading/contracts</code>, speaks to <code>/api/v2</code>, and treats{" "}
          <code>apps/web</code> as reference-only legacy material.
        </p>
        <div className="badge-row">
          <span className="badge is-warm">desktop first</span>
          <span className="badge is-green">ipad child app next</span>
          <span className="badge is-sky">distribution over live generation</span>
          <span className={`badge ${status === "live" ? "is-green" : status === "loading" ? "is-sky" : "is-warm"}`}>
            {status === "live" ? "live dashboard" : status === "loading" ? "syncing dashboard" : "fallback dashboard"}
          </span>
        </div>
        {error ? <div className="note-card">{error}</div> : null}
        <div className="metrics-grid">
          <article className="metric-card">
            <div className="metric-card__label">Children in household</div>
            <div className="metric-card__value">{dashboard.children.length}</div>
            <div className="metric-card__meta">Profiles already tied to a current package assignment.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Package queue</div>
            <div className="metric-card__value">{dashboard.package_queue.length}</div>
            <div className="metric-card__meta">Versioned packages staged for plan construction and distribution.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Completed sessions</div>
            <div className="metric-card__value">{dashboard.progress_metrics.completed_sessions}</div>
            <div className="metric-card__meta">Reading outcomes sourced from typed event payloads.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Translation reveals</div>
            <div className="metric-card__value">{dashboard.progress_metrics.translation_reveals}</div>
            <div className="metric-card__meta">A quick proxy for bilingual assistance demand.</div>
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
        <ConnectedPackagePanel dashboard={dashboard} status={status} error={error} />

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
            Extend contracts and <code>/api/v2</code> first. Do not route new feature work back into{" "}
            <code>apps/web</code>.
          </div>
        </article>
      </section>
    </main>
  );
}
