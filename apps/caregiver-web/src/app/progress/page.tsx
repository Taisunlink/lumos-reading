"use client";

import { formatDateTime, formatEventType, formatMinutesFromMs } from "@/lib/format";
import { useProgressDomain } from "@/lib/hooks/use-progress-domain";

export default function ProgressPage() {
  const { progressDomain, status, error } = useProgressDomain();

  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Progress and instrumentation</div>
        <h1>Progress should come from typed events, not from UI assumptions.</h1>
        <p className="hero-card__lead">
          This page is the first caregiver-facing proof that <code>ReadingEventV1</code> can support completion,
          replay, translation, and assist-mode insights without relying on ad hoc frontend state.
        </p>
        <div className="badge-row">
          <span className={`badge ${status === "live" ? "is-green" : status === "loading" ? "is-sky" : "is-warm"}`}>
            {status === "live" ? "live progress service" : status === "loading" ? "syncing progress service" : "fallback progress service"}
          </span>
        </div>
        {error ? <div className="note-card">{error}</div> : null}
        <div className="metrics-grid">
          <article className="metric-card">
            <div className="metric-card__label">Tracked events</div>
            <div className="metric-card__value">{progressDomain.trackedEvents}</div>
            <div className="metric-card__meta">Recent instrumentation entries ready for caregiver reporting.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Unique sessions</div>
            <div className="metric-card__value">{progressDomain.uniqueSessions}</div>
            <div className="metric-card__meta">Session identifiers already survive across multiple event types.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Observed dwell</div>
            <div className="metric-card__value">{formatMinutesFromMs(progressDomain.totalDwellMs)}</div>
            <div className="metric-card__meta">Completed-session payloads can feed reports, reminders, and retention logic.</div>
          </article>
        </div>
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Recent event timeline</h2>
            <span className="panel-card__eyebrow">Derived from shared contract payloads</span>
          </div>
          <div className="timeline">
            {progressDomain.timeline.map((event) => (
              <article key={event.eventId} className="timeline-item">
                <div className="panel-card__header">
                  <span className="timeline-item__title">{formatEventType(event.eventType)}</span>
                  <span className="panel-card__eyebrow">{formatDateTime(event.occurredAt)}</span>
                </div>
                <div className="list-row__meta">
                  <span>{event.childName}</span>
                  <span>{event.packageTitle}</span>
                  <span>{event.surface}</span>
                </div>
                <p>{event.description}</p>
              </article>
            ))}
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Event coverage</h2>
            <span className="panel-card__eyebrow">What the current sample already proves</span>
          </div>
          <div className="stack-list">
            {progressDomain.eventCoverage.map((entry) => (
              <article key={entry.eventType} className="list-row">
                <p className="list-row__title">{formatEventType(entry.eventType)}</p>
                <div className="list-row__meta">
                  <span>{entry.count} event(s)</span>
                  <span className="mono">{entry.eventType}</span>
                </div>
              </article>
            ))}
          </div>
          <div className="note-card">
            Next step: ingest batched events from the child surface and add caregiver-facing rollups instead of keeping
            analytics logic in page components.
          </div>
        </article>
      </section>
    </main>
  );
}
