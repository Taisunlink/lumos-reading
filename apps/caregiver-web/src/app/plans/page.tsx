"use client";

import { formatDurationMinutes } from "@/lib/format";
import { useCaregiverDashboard } from "@/lib/hooks/use-caregiver-dashboard";
import {
  demoHouseholdId,
  fallbackCaregiverDashboard,
  resolveWeeklyPlan,
} from "@/lib/page-models";

const planningGuardrails = [
  "Mix one anchor package with one low-stimulation fallback instead of flooding the queue.",
  "Use bilingual support selectively and review translation reveal events before increasing difficulty.",
  "Keep distribution package-based so offline and rollback behavior stays predictable on the child surface.",
];

export default function PlansPage() {
  const { dashboard, status, error } = useCaregiverDashboard(
    demoHouseholdId,
    fallbackCaregiverDashboard,
  );
  const resolvedPlan = resolveWeeklyPlan(dashboard);
  const totalPlannedMinutes = resolvedPlan.reduce(
    (sum, item) => sum + Math.round(item.package.estimated_duration_sec / 60),
    0,
  );

  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Weekly reading plan</div>
        <h1>Planning is a packaging problem first and a recommendation problem second.</h1>
        <p className="hero-card__lead">
          The caregiver surface needs to turn package inventory into a steady household cadence, with clear purpose
          for each session and minimal cognitive load for the parent.
        </p>
        <div className="badge-row">
          <span className={`badge ${status === "live" ? "is-green" : status === "loading" ? "is-sky" : "is-warm"}`}>
            {status === "live" ? "live dashboard" : status === "loading" ? "syncing dashboard" : "fallback dashboard"}
          </span>
        </div>
        {error ? <div className="note-card">{error}</div> : null}
        <div className="metrics-grid">
          <article className="metric-card">
            <div className="metric-card__label">Weekly sessions</div>
            <div className="metric-card__value">{resolvedPlan.length}</div>
            <div className="metric-card__meta">Scheduled moments already mapped into the plan.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Planned reading time</div>
            <div className="metric-card__value">{totalPlannedMinutes} min</div>
            <div className="metric-card__meta">A lightweight target that can later sync to reminders and subscriptions.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Queue coverage</div>
            <div className="metric-card__value">{dashboard.package_queue.length}</div>
            <div className="metric-card__meta">Packages currently available for rotation or escalation.</div>
          </article>
        </div>
      </section>

      <section className="card-grid">
        {resolvedPlan.map((item) => (
          <article key={`${item.day}-${item.package.package_id}`} className="panel-card">
            <div className="panel-card__header">
              <div>
                <h2>{item.day}</h2>
                <p className="panel-card__eyebrow">{item.mode}</p>
              </div>
              <span className="badge is-warm">{item.package.language_mode}</span>
            </div>
            <p>{item.objective}</p>
            <div className="meta-pairs">
              <div className="meta-pair">
                <span className="meta-pair__label">Package</span>
                <span className="meta-pair__value">{item.package.title}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Age band</span>
                <span className="meta-pair__value">{item.package.age_band}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Duration</span>
                <span className="meta-pair__value">{formatDurationMinutes(item.package.estimated_duration_sec)}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Safety</span>
                <span className="meta-pair__value">{item.package.safety.review_status}</span>
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Package queue</h2>
            <span className="panel-card__eyebrow">What distribution can safely deliver</span>
          </div>
          <div className="stack-list">
            {dashboard.package_queue.map((item) => (
              <article key={item.package_id} className="list-row">
                <p className="list-row__title">{item.title}</p>
                <div className="list-row__meta">
                  <span>{item.language_mode}</span>
                  <span>{item.difficulty_level}</span>
                  <span>{formatDurationMinutes(item.estimated_duration_sec)}</span>
                </div>
              </article>
            ))}
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Planning guardrails</h2>
            <span className="panel-card__eyebrow">Rules worth encoding later</span>
          </div>
          <ul className="clean-list">
            {planningGuardrails.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
