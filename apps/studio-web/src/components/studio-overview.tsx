"use client";

import Link from "next/link";
import {
  FeedbackBanner,
  MetricCard,
  StatusBadge,
  formatDateTime,
  titleize,
  toneForAuditStatus,
  toneForReleaseStatus,
  toneForResourceStatus,
  toneForReviewStatus,
  toneForWorkflowState,
} from "@/components/studio-ui";
import {
  summarizeStudioReleaseBoard,
  useStudioReleaseBoard,
} from "@/lib/hooks";

export function StudioOverview() {
  const { board, status, error, refresh } = useStudioReleaseBoard();
  const summary = summarizeStudioReleaseBoard(board);
  const attentionPackages = board.histories.filter(
    (history) =>
      history.findingCount > 0 ||
      history.activeReleaseId === null ||
      history.reviewStatus !== "approved",
  );

  return (
    <div className="studio-page">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Phase 4 ops console</div>
        <h1>Studio now controls review visibility, release state, and runtime traceability.</h1>
        <p className="hero-card__lead">
          The console reads shared package release views instead of page-local aggregates.
          Operators can see what is draft, built, active, recalled, and which runtime package
          is backed by which review state.
        </p>

        <div className="status-row">
          <StatusBadge
            label={status === "live" ? "Live data" : status === "loading" ? "Loading" : "Fallback data"}
            tone={toneForResourceStatus(status)}
          />
          <StatusBadge
            label={`${summary.activeReleaseCount} active releases`}
            tone="is-green"
          />
          <StatusBadge
            label={`${summary.packagesWithFindings} packages with findings`}
            tone={summary.packagesWithFindings > 0 ? "is-amber" : "is-green"}
          />
          <StatusBadge
            label={`${summary.packagesWithoutActiveRelease} packages without active runtime release`}
            tone={summary.packagesWithoutActiveRelease > 0 ? "is-amber" : "is-neutral"}
          />
        </div>

        <div className="button-row">
          <button type="button" className="button" onClick={refresh}>
            Refresh board
          </button>
          <Link href="/briefs" className="button is-secondary">
            Open briefs board
          </Link>
          <Link href="/packages" className="button is-secondary">
            Open package workspace
          </Link>
          <Link href="/releases" className="button is-secondary">
            Open release history
          </Link>
        </div>

        <FeedbackBanner
          status={status}
          message={`Board snapshot generated ${formatDateTime(board.generatedAt)}.`}
          error={error}
        />
      </section>

      <section className="metrics-grid">
        <MetricCard
          label="Packages in scope"
          value={summary.packageCount}
          meta="Draft cards exposed through shared release-domain services"
        />
        <MetricCard
          label="Active runtime releases"
          value={summary.activeReleaseCount}
          meta="Packages currently resolvable through the runtime lookup path"
        />
        <MetricCard
          label="Recalled releases"
          value={summary.recalledReleaseCount}
          meta="Historical releases preserved for audit and rollback decisions"
        />
        <MetricCard
          label="Audit findings"
          value={summary.totalFindings}
          meta="Release trace still shows review evidence even when findings exist"
        />
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <div>
              <div className="panel-card__eyebrow">Queue health</div>
              <h2>Package state at a glance</h2>
            </div>
            <Link href="/packages" className="inline-link">
              Review packages
            </Link>
          </div>

          <div className="stack-list">
            {board.histories.map((history) => {
              const activeRelease = history.releases.find((release) => release.status === "active");

              return (
                <article key={history.packageId} className="list-row">
                  <div className="list-row__header">
                    <div>
                      <h3 className="list-row__title">{history.title}</h3>
                      <p className="list-row__copy">
                        {history.subtitle ?? history.packagePreview.story_variant_id}
                      </p>
                    </div>

                    <div className="status-row">
                      <StatusBadge
                        label={titleize(history.workflowState)}
                        tone={toneForWorkflowState(history.workflowState)}
                      />
                      <StatusBadge
                        label={`Review ${titleize(history.reviewStatus)}`}
                        tone={toneForReviewStatus(history.reviewStatus)}
                      />
                      <StatusBadge
                        label={`Audit ${titleize(history.auditStatus)}`}
                        tone={toneForAuditStatus(history.auditStatus)}
                      />
                    </div>
                  </div>

                  <div className="list-row__meta">
                    <span>{history.packagePreview.language_mode}</span>
                    <span>{history.packagePreview.release_channel}</span>
                    <span>{formatDateTime(history.updatedAt)}</span>
                    <span>
                      {activeRelease
                        ? `Runtime on release v${activeRelease.release_version}`
                        : "No active runtime release"}
                    </span>
                  </div>
                </article>
              );
            })}
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <div>
              <div className="panel-card__eyebrow">Operator handoff</div>
              <h2>Attention points</h2>
            </div>
            <Link href="/audits" className="inline-link">
              Open audits
            </Link>
          </div>

          {attentionPackages.length === 0 ? (
            <div className="note-card">
              <p>
                No package is currently blocked by missing runtime release, recalled review state,
                or outstanding findings.
              </p>
            </div>
          ) : (
            <div className="stack-list">
              {attentionPackages.map((history) => (
                <article key={history.packageId} className="signal-card">
                  <div className="signal-card__title">{history.title}</div>
                  <p>
                    {history.activeReleaseId === null
                      ? "No active runtime release."
                      : history.findingCount > 0
                        ? `${history.findingCount} audit findings remain visible.`
                        : `Review status is ${titleize(history.reviewStatus)}.`}
                  </p>
                  <div className="status-row">
                    <StatusBadge
                      label={`Audit ${titleize(history.auditStatus)}`}
                      tone={toneForAuditStatus(history.auditStatus)}
                    />
                    <StatusBadge
                      label={`${history.findingCount} findings`}
                      tone={history.findingCount > 0 ? "is-amber" : "is-neutral"}
                    />
                  </div>
                </article>
              ))}
            </div>
          )}
        </article>
      </section>

      <article className="panel-card">
        <div className="panel-card__header">
          <div>
            <div className="panel-card__eyebrow">Runtime map</div>
            <h2>Release to review traceability</h2>
          </div>
          <Link href="/releases" className="inline-link">
            Full release history
          </Link>
        </div>

        <div className="timeline">
          {board.histories.map((history) => {
            const activeRelease = history.releases.find((release) => release.status === "active");

            return (
              <article key={history.packageId} className="timeline-item">
                <div className="timeline-item__title">{history.title}</div>
                <div className="list-row__meta">
                  <span>
                    {activeRelease
                      ? `Release v${activeRelease.release_version}`
                      : "No active release"}
                  </span>
                  <span>{history.audit.policy_version}</span>
                  <span>{titleize(history.audit.reviewer.reviewer_type)}</span>
                  <span>{formatDateTime(history.audit.reviewed_at)}</span>
                </div>
                <div className="status-row">
                  <StatusBadge
                    label={titleize(history.reviewStatus)}
                    tone={toneForReviewStatus(history.reviewStatus)}
                  />
                  <StatusBadge
                    label={titleize(history.auditStatus)}
                    tone={toneForAuditStatus(history.auditStatus)}
                  />
                  {activeRelease ? (
                    <StatusBadge
                      label={titleize(activeRelease.status)}
                      tone={toneForReleaseStatus(activeRelease.status)}
                    />
                  ) : null}
                </div>
                <p className="timeline-item__copy">
                  {activeRelease
                    ? `${activeRelease.runtime_lookup_key} points to build ${activeRelease.build_id}.`
                    : "This package has review evidence but is not currently routed to runtime."}
                </p>
              </article>
            );
          })}
        </div>
      </article>
    </div>
  );
}
