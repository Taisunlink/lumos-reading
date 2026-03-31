"use client";

import { useAccessDomain } from "@/lib/hooks/use-access-domain";

function formatDate(value?: string | null): string {
  if (!value) {
    return "Not set";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function AccessPage() {
  const { accessDomain, valueDomain, status, error, refresh } = useAccessDomain();

  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Commercial access loop</div>
        <h1>Subscription state, package access, and weekly value need to tell one story.</h1>
        <p className="hero-card__lead">
          This page is the Phase 6 caregiver proof that package visibility, household access, and
          value reporting now resolve from shared contracts instead of page-local assumptions.
        </p>
        <div className="badge-row">
          <span className={`badge ${status === "live" ? "is-green" : status === "loading" ? "is-sky" : "is-warm"}`}>
            {status === "live" ? "live access services" : status === "loading" ? "syncing access services" : "fallback access services"}
          </span>
          <span className="badge is-sky">{accessDomain.planName}</span>
          <span className="badge is-green">{accessDomain.subscriptionStatus}</span>
        </div>
        {error ? <div className="note-card">{error}</div> : null}
        <div className="button-row">
          <button type="button" className="button" onClick={refresh}>
            Refresh access state
          </button>
        </div>
        <div className="metrics-grid">
          <article className="metric-card">
            <div className="metric-card__label">Entitled packages</div>
            <div className="metric-card__value">{accessDomain.entitledPackageCount}</div>
            <div className="metric-card__meta">Packages the child surface can currently receive.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Locked packages</div>
            <div className="metric-card__value">{accessDomain.lockedPackageCount}</div>
            <div className="metric-card__meta">Premium items still visible to the caregiver but blocked from delivery.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Weekly value score</div>
            <div className="metric-card__value">{valueDomain.valueScore}</div>
            <div className="metric-card__meta">A simple cross-surface signal derived from completed reading behavior.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Finished reading time</div>
            <div className="metric-card__value">{valueDomain.totalReadingMinutes} min</div>
            <div className="metric-card__meta">Completed-session dwell converted into a caregiver-readable weekly number.</div>
          </article>
        </div>
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <div>
              <h2>Subscription and access state</h2>
              <p className="panel-card__eyebrow">One household-scoped source of truth</p>
            </div>
          </div>
          <div className="meta-pairs">
            <div className="meta-pair">
              <span className="meta-pair__label">Plan</span>
              <span className="meta-pair__value">{accessDomain.planName}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Access state</span>
              <span className="meta-pair__value">{accessDomain.accessState}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Billing interval</span>
              <span className="meta-pair__value">{accessDomain.billingInterval}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Trial ends</span>
              <span className="meta-pair__value">{formatDate(accessDomain.trialEndsAt)}</span>
            </div>
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <div>
              <h2>Weekly value</h2>
              <p className="panel-card__eyebrow">Derived from typed reading events</p>
            </div>
          </div>
          <div className="meta-pairs">
            <div className="meta-pair">
              <span className="meta-pair__label">Completed sessions</span>
              <span className="meta-pair__value">{valueDomain.completedSessions}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Distinct packages completed</span>
              <span className="meta-pair__value">{valueDomain.distinctPackagesCompleted}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Reread sessions</span>
              <span className="meta-pair__value">{valueDomain.rereadSessions}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Prompt completions</span>
              <span className="meta-pair__value">{valueDomain.caregiverPromptCompletions}</span>
            </div>
          </div>
        </article>
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Accessible now</h2>
            <span className="panel-card__eyebrow">Visible in plan and child delivery</span>
          </div>
          <div className="stack-list">
            {accessDomain.accessiblePackages.map((storyPackage) => (
              <article key={storyPackage.packageId} className="list-row">
                <p className="list-row__title">{storyPackage.title}</p>
                <div className="list-row__meta">
                  <span>{storyPackage.languageMode}</span>
                  <span>{storyPackage.ageBand}</span>
                  <span>{storyPackage.entitlementSource}</span>
                </div>
                <p className="metric-card__meta">{storyPackage.reason}</p>
              </article>
            ))}
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Locked until upgrade</h2>
            <span className="panel-card__eyebrow">Still explainable to the caregiver</span>
          </div>
          <div className="stack-list">
            {accessDomain.lockedPackages.map((storyPackage) => (
              <article key={storyPackage.packageId} className="list-row">
                <p className="list-row__title">{storyPackage.title}</p>
                <div className="list-row__meta">
                  <span>{storyPackage.languageMode}</span>
                  <span>{storyPackage.ageBand}</span>
                  <span>{storyPackage.entitlementSource}</span>
                </div>
                <p className="metric-card__meta">{storyPackage.reason}</p>
              </article>
            ))}
          </div>
        </article>
      </section>

      <article className="panel-card">
        <div className="panel-card__header">
          <h2>Value highlights</h2>
          <span className="panel-card__eyebrow">
            {formatDate(valueDomain.periodStart)} to {formatDate(valueDomain.periodEnd)}
          </span>
        </div>
        <div className="card-grid">
          {valueDomain.highlights.map((highlight) => (
            <article key={highlight.code} className="soft-card">
              <p className="list-row__title">{highlight.title}</p>
              <div className="list-row__meta">
                <span className="mono">{highlight.code}</span>
              </div>
              <p>{highlight.detail}</p>
            </article>
          ))}
        </div>
      </article>
    </main>
  );
}
