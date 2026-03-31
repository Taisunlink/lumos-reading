"use client";

import {
  FeedbackBanner,
  MetricCard,
  StatusBadge,
  formatDateTime,
  titleize,
  toneForResourceStatus,
} from "@/components/studio-ui";
import { useStudioOperationsBoard } from "@/lib/hooks";

export function StudioOperations() {
  const { board, status, error, refresh } = useStudioOperationsBoard();

  return (
    <div className="studio-page">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Phase 6 operations loop</div>
        <h1>Access state, weekly value, and ops metrics now close the business loop.</h1>
        <p className="hero-card__lead">
          The studio surface can now inspect household access state, package lock coverage, and
          operating signals without bypassing the shared caregiver and child runtime contracts.
        </p>

        <div className="status-row">
          <StatusBadge
            label={status === "live" ? "Live data" : status === "loading" ? "Loading" : "Fallback data"}
            tone={toneForResourceStatus(status)}
          />
          <StatusBadge
            label={`${board.access.entitledPackageCount} entitled packages`}
            tone="is-green"
          />
          <StatusBadge
            label={`${board.access.lockedPackageCount} locked packages`}
            tone={board.access.lockedPackageCount > 0 ? "is-amber" : "is-neutral"}
          />
          <StatusBadge
            label={`Value score ${board.weeklyValue.valueScore}`}
            tone="is-sky"
          />
        </div>

        <div className="button-row">
          <button type="button" className="button" onClick={refresh}>
            Refresh operations board
          </button>
        </div>

        <FeedbackBanner
          status={status}
          message={`Board snapshot generated ${formatDateTime(board.generatedAt)}.`}
          error={error}
        />
      </section>

      <section className="metrics-grid">
        <MetricCard
          label="Households in scope"
          value={board.ops.householdsInScope}
          meta="Current demo households visible to operations."
        />
        <MetricCard
          label="Trial households"
          value={board.ops.householdsInTrial}
          meta="Households currently operating on trial access."
        />
        <MetricCard
          label="Blocked requests"
          value={board.ops.blockedPackageRequests}
          meta="Package assignment or delivery requests rejected by entitlement checks."
        />
        <MetricCard
          label="Entitled deliveries"
          value={board.ops.entitledPackageDeliveries}
          meta="Child-scoped package deliveries that passed the current access policy."
        />
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <div>
              <div className="panel-card__eyebrow">Household access mirror</div>
              <h2>{board.access.planName}</h2>
            </div>
            <StatusBadge
              label={titleize(board.access.subscriptionStatus)}
              tone="is-green"
            />
          </div>

          <div className="meta-pairs">
            <div className="meta-pair">
              <span className="meta-pair__label">Access state</span>
              <span className="meta-pair__value">{titleize(board.access.accessState)}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Billing interval</span>
              <span className="meta-pair__value">{titleize(board.access.billingInterval)}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Trial ends</span>
              <span className="meta-pair__value">{formatDateTime(board.access.trialEndsAt)}</span>
            </div>
            <div className="meta-pair">
              <span className="meta-pair__label">Generated at</span>
              <span className="meta-pair__value">{formatDateTime(board.access.generatedAt)}</span>
            </div>
          </div>

          <div className="stack-list">
            {board.access.lockedPackages.map((storyPackage) => (
              <article key={storyPackage.packageId} className="signal-card">
                <div className="signal-card__title">{storyPackage.title}</div>
                <p>{storyPackage.reason}</p>
                <div className="status-row">
                  <StatusBadge label={storyPackage.languageMode} tone="is-neutral" />
                  <StatusBadge label={titleize(storyPackage.entitlementSource)} tone="is-amber" />
                </div>
              </article>
            ))}
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <div>
              <div className="panel-card__eyebrow">Weekly value mirror</div>
              <h2>Caregiver-visible outcome</h2>
            </div>
            <StatusBadge
              label={`${board.weeklyValue.totalReadingMinutes} min finished reading`}
              tone="is-sky"
            />
          </div>

          <div className="metrics-grid">
            <MetricCard
              label="Completed sessions"
              value={board.weeklyValue.completedSessions}
            />
            <MetricCard
              label="Distinct packages"
              value={board.weeklyValue.distinctPackagesCompleted}
            />
            <MetricCard
              label="Reread sessions"
              value={board.weeklyValue.rereadSessions}
            />
            <MetricCard
              label="Prompt completions"
              value={board.weeklyValue.caregiverPromptCompletions}
            />
          </div>

          <div className="timeline">
            {board.weeklyValue.highlights.map((highlight) => (
              <article key={highlight.code} className="timeline-item">
                <div className="timeline-item__title">{highlight.title}</div>
                <div className="list-row__meta">
                  <span className="mono">{highlight.code}</span>
                  <span>{formatDateTime(board.weeklyValue.periodStart)}</span>
                  <span>{formatDateTime(board.weeklyValue.periodEnd)}</span>
                </div>
                <p className="timeline-item__copy">{highlight.detail}</p>
              </article>
            ))}
          </div>
        </article>
      </section>

      <article className="panel-card">
        <div className="panel-card__header">
          <div>
            <div className="panel-card__eyebrow">Ops summary</div>
            <h2>Experiment-safe instrumentation</h2>
          </div>
        </div>

        <div className="metrics-grid">
          <MetricCard
            label="Completed sessions"
            value={board.ops.completedSessions}
            meta="Still derived from the shared reading event flow."
          />
          <MetricCard
            label="Reuse signals"
            value={board.ops.reuseSignals}
            meta="Audio replays and reread behavior available for retention work."
          />
          <MetricCard
            label="Average weekly value"
            value={board.ops.averageWeeklyValueScore}
            meta="Commercial loop stays grounded in reading outcomes, not vanity traffic."
          />
          <MetricCard
            label="Paid households"
            value={board.ops.householdsWithPaidAccess}
            meta="Kept explicit even when the demo baseline is still trial-led."
          />
        </div>
      </article>
    </div>
  );
}
