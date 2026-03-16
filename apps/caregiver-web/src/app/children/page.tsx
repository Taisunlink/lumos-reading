"use client";

import { formatDurationMinutes } from "@/lib/format";
import { useChildDomain } from "@/lib/hooks/use-child-domain";

const supportPatterns = [
  "Keep the primary reading language stable and reveal translation support only on demand.",
  "Assign predictable calm packages for wind-down sessions instead of reusing the same challenge package every night.",
  "Treat caregiver prompts as guided co-reading scaffolds, not extra screen tasks for the child.",
];

export default function ChildrenPage() {
  const { childDomain, status, error } = useChildDomain();
  const { children, supportSignals, bilingualAssignments, plannedSessions } = childDomain;

  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Child profiles and package fit</div>
        <h1>Assignments stay tied to developmental goals, not just to content inventory.</h1>
        <p className="hero-card__lead">
          Each child card reflects the current package assignment, support focus, and the weekly target that the
          caregiver surface should help manage.
        </p>
        <div className="badge-row">
          <span className={`badge ${status === "live" ? "is-green" : status === "loading" ? "is-sky" : "is-warm"}`}>
            {status === "live" ? "live child service" : status === "loading" ? "syncing child service" : "fallback child service"}
          </span>
        </div>
        {error ? <div className="note-card">{error}</div> : null}
        <div className="metrics-grid">
          <article className="metric-card">
            <div className="metric-card__label">Active children</div>
            <div className="metric-card__value">{children.length}</div>
            <div className="metric-card__meta">Profiles with an assigned package and weekly goal.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Bilingual assignments</div>
            <div className="metric-card__value">{bilingualAssignments}</div>
            <div className="metric-card__meta">Profiles currently using a package tagged for translation assistance.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Planned sessions</div>
            <div className="metric-card__value">{plannedSessions}</div>
            <div className="metric-card__meta">Weekly plan entries already mapped to household needs.</div>
          </article>
        </div>
      </section>

      <section className="card-grid">
        {children.map((child) => (
          <article key={child.childId} className="panel-card">
            <div className="panel-card__header">
              <div>
                <h2>{child.name}</h2>
                <p className="panel-card__eyebrow">{child.ageLabel}</p>
              </div>
              <span className="badge is-green">{child.currentPackage.language_mode}</span>
            </div>

            <p>{child.focus}</p>

            <div className="badge-row">
              {child.currentPackage.tags?.map((tag) => (
                <span key={tag} className="badge">
                  {tag}
                </span>
              ))}
            </div>

            <div className="meta-pairs">
              <div className="meta-pair">
                <span className="meta-pair__label">Weekly goal</span>
                <span className="meta-pair__value">{child.weeklyGoal}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Package</span>
                <span className="meta-pair__value">{child.currentPackage.title}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Difficulty</span>
                <span className="meta-pair__value">{child.currentPackage.difficulty_level}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Expected session</span>
                <span className="meta-pair__value">
                  {formatDurationMinutes(child.currentPackage.estimated_duration_sec)}
                </span>
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Assignment heuristics</h2>
            <span className="panel-card__eyebrow">Business logic before UI polish</span>
          </div>
          <ul className="clean-list">
            {supportPatterns.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Current support signals</h2>
            <span className="panel-card__eyebrow">What the caregiver should monitor</span>
          </div>
          <div className="stack-list">
            {supportSignals.map((signal) => (
              <article key={signal.childId} className="list-row">
                <p className="list-row__title">{signal.name}</p>
                <div className="list-row__meta">
                  <span>{signal.focus}</span>
                </div>
                <div className="badge-row">
                  <span className="badge is-sky">{signal.ageBand}</span>
                  <span className="badge">{signal.releaseChannel}</span>
                  <span className="badge is-green">{signal.reviewStatus}</span>
                </div>
              </article>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}
