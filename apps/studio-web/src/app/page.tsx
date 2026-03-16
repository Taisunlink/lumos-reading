"use client";

import {
  CAREGIVER_PLAN_SCHEMA_VERSION,
  CAREGIVER_PROGRESS_SCHEMA_VERSION,
  caregiverPlanV1Schema,
  caregiverProgressV1Schema,
} from "@lumosreading/contracts";
import { useStudioPlan, useStudioProgress } from "@/lib/hooks";

function formatMinutes(seconds: number): string {
  return `${Math.max(1, Math.round(seconds / 60))} min`;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function statusClassName(status: "loading" | "live" | "fallback"): string {
  if (status === "live") {
    return "badge is-live";
  }

  if (status === "loading") {
    return "badge is-loading";
  }

  return "badge is-fallback";
}

export default function StudioHomePage() {
  const { value: plan, status: planStatus, error: planError } = useStudioPlan();
  const { value: progress, status: progressStatus, error: progressError } = useStudioProgress();

  return (
    <main className="studio-shell">
      <div className="studio-stack">
        <section className="hero">
          <div className="eyebrow">Studio Contracts Probe</div>
          <h1>Studio now consumes plan and progress contracts directly.</h1>
          <p>
            This minimal shell is not a CMS yet. It proves a second surface outside caregiver-web can pull the new
            caregiver subdomain read models through <code>@lumosreading/sdk</code> without depending on the aggregate
            dashboard route.
          </p>
          <div className="badge-row">
            <span className="badge">studio preview</span>
            <span className={statusClassName(planStatus)}>
              {planStatus === "live" ? "live plan contract" : planStatus === "loading" ? "syncing plan contract" : "fallback plan contract"}
            </span>
            <span className={statusClassName(progressStatus)}>
              {progressStatus === "live"
                ? "live progress contract"
                : progressStatus === "loading"
                  ? "syncing progress contract"
                  : "fallback progress contract"}
            </span>
          </div>
          <div className="metrics">
            <article className="metric">
              <div className="metric__label">Plan sessions</div>
              <div className="metric__value">{plan.weekly_plan.length}</div>
              <div className="note">Schema: {CAREGIVER_PLAN_SCHEMA_VERSION}</div>
            </article>
            <article className="metric">
              <div className="metric__label">Tracked events</div>
              <div className="metric__value">{progress.recent_events.length}</div>
              <div className="note">Schema: {CAREGIVER_PROGRESS_SCHEMA_VERSION}</div>
            </article>
            <article className="metric">
              <div className="metric__label">Completed sessions</div>
              <div className="metric__value">{progress.progress_metrics.completed_sessions}</div>
              <div className="note">Generated at {formatDateTime(progress.generated_at)}</div>
            </article>
          </div>
          {planError ? <div className="note">{planError}</div> : null}
          {progressError ? <div className="note">{progressError}</div> : null}
        </section>

        <section className="grid">
          <article className="panel">
            <div className="panel__header">
              <h2>Plan Contract Preview</h2>
              <span className="badge">{String(caregiverPlanV1Schema.title ?? CAREGIVER_PLAN_SCHEMA_VERSION)}</span>
            </div>
            <div className="rows">
              {plan.weekly_plan.map((item) => (
                <article key={`${item.day}-${item.package.package_id}`} className="row">
                  <p className="row__title">
                    {item.day}: {item.package.title}
                  </p>
                  <div className="row__meta">
                    <span>{item.mode}</span>
                    <span>{item.package.language_mode}</span>
                    <span>{item.package.difficulty_level}</span>
                    <span>{formatMinutes(item.package.estimated_duration_sec)}</span>
                  </div>
                  <p>{item.objective}</p>
                </article>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel__header">
              <h2>Progress Contract Preview</h2>
              <span className="badge">{String(caregiverProgressV1Schema.title ?? CAREGIVER_PROGRESS_SCHEMA_VERSION)}</span>
            </div>
            <div className="rows">
              {progress.recent_events.map((entry) => (
                <article key={entry.event.event_id} className="row">
                  <p className="row__title">{entry.event.event_type}</p>
                  <div className="row__meta">
                    <span>{entry.child_name}</span>
                    <span>{entry.package_title}</span>
                    <span>{entry.event.surface}</span>
                    <span>{formatDateTime(entry.event.occurred_at)}</span>
                  </div>
                  <p>{JSON.stringify(entry.event.payload)}</p>
                </article>
              ))}
            </div>
          </article>
        </section>
      </div>
    </main>
  );
}
