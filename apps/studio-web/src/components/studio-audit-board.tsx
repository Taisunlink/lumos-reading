"use client";

import {
  EmptyState,
  FeedbackBanner,
  MetricCard,
  StatusBadge,
  formatDateTime,
  titleize,
  toneForAuditStatus,
  toneForReleaseStatus,
  toneForReviewStatus,
  toneForSeverity,
} from "@/components/studio-ui";
import {
  summarizeStudioReleaseBoard,
  useStudioReleaseBoard,
} from "@/lib/hooks";

export function StudioAuditBoard() {
  const { board, status, error, refresh } = useStudioReleaseBoard();
  const summary = summarizeStudioReleaseBoard(board);

  return (
    <div className="studio-page">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Audit traceability</div>
        <h1>Runtime content can be traced back to a recorded review state.</h1>
        <p className="hero-card__lead">
          Audit records, findings, reviewer identity, and runtime release linkage are exposed from
          the shared release-domain history view, not rebuilt inside page components.
        </p>
        <div className="button-row">
          <button type="button" className="button" onClick={refresh}>
            Refresh audit board
          </button>
        </div>
        <FeedbackBanner
          status={status}
          message={`Audit board synced ${formatDateTime(board.generatedAt)}.`}
          error={error}
        />
      </section>

      <section className="metrics-grid">
        <MetricCard
          label="Audits in scope"
          value={summary.packageCount}
          meta="One authoritative audit trail per package draft"
        />
        <MetricCard
          label="Packages with findings"
          value={summary.packagesWithFindings}
          meta="Findings remain visible even after release"
        />
        <MetricCard
          label="Runtime releases with review"
          value={summary.activeReleaseCount}
          meta="Each active runtime package has matching review metadata"
        />
      </section>

      {board.histories.length === 0 ? (
        <EmptyState
          title="No audit records"
          copy="The Phase 4 audit board expects package history views with audit evidence."
        />
      ) : (
        <div className="audit-grid">
          {board.histories.map((history) => {
            const activeRelease =
              history.releases.find((release) => release.status === "active") ?? null;

            return (
              <article key={history.packageId} className="panel-card">
                <div className="panel-card__header">
                  <div>
                    <div className="panel-card__eyebrow">{history.title}</div>
                    <h2>Review evidence and runtime linkage</h2>
                  </div>

                  <div className="status-row">
                    <StatusBadge
                      label={titleize(history.audit.audit_status)}
                      tone={toneForAuditStatus(history.audit.audit_status)}
                    />
                    <StatusBadge
                      label={titleize(history.audit.severity)}
                      tone={toneForSeverity(history.audit.severity)}
                    />
                  </div>
                </div>

                <div className="meta-pairs">
                  <div className="meta-pair">
                    <div className="meta-pair__label">Review status</div>
                    <div className="meta-pair__value">
                      <StatusBadge
                        label={titleize(history.reviewStatus)}
                        tone={toneForReviewStatus(history.reviewStatus)}
                      />
                    </div>
                  </div>
                  <div className="meta-pair">
                    <div className="meta-pair__label">Reviewer</div>
                    <div className="meta-pair__value">
                      {titleize(history.audit.reviewer.reviewer_type)}
                      {" / "}
                      {history.audit.reviewer.reviewer_id ?? "unassigned"}
                    </div>
                  </div>
                  <div className="meta-pair">
                    <div className="meta-pair__label">Policy</div>
                    <div className="meta-pair__value">{history.audit.policy_version}</div>
                  </div>
                  <div className="meta-pair">
                    <div className="meta-pair__label">Runtime</div>
                    <div className="meta-pair__value">
                      {activeRelease ? (
                        <StatusBadge
                          label={`Release v${activeRelease.release_version}`}
                          tone={toneForReleaseStatus(activeRelease.status)}
                        />
                      ) : (
                        "No active release"
                      )}
                    </div>
                  </div>
                </div>

                <div className="note-card">
                  <p>
                    {activeRelease
                      ? `${activeRelease.runtime_lookup_key} is linked to audit ${history.audit.audit_id} reviewed ${formatDateTime(history.audit.reviewed_at)}.`
                      : `Audit ${history.audit.audit_id} exists, but no active runtime release is attached right now.`}
                  </p>
                </div>

                {history.audit.findings.length === 0 ? (
                  <div className="note-card">
                    <p>No findings were recorded for this review pass.</p>
                  </div>
                ) : (
                  <div className="finding-list">
                    {history.audit.findings.map((finding) => (
                      <article key={finding.code} className="finding-card">
                        <div className="list-row__header">
                          <div>
                            <div className="list-row__title">{finding.title}</div>
                            <div className="list-row__copy">{finding.code}</div>
                          </div>
                          <StatusBadge
                            label={titleize(finding.severity)}
                            tone={toneForSeverity(finding.severity)}
                          />
                        </div>
                        <p>{finding.description}</p>
                        <div className="list-row__meta">
                          <span>
                            {finding.page_index == null ? "All pages" : `Page ${finding.page_index}`}
                          </span>
                          <span>{finding.action_required ? "Action required" : "Reviewed"}</span>
                        </div>
                      </article>
                    ))}
                  </div>
                )}

                <div className="stack-list">
                  {history.operatorNotes.map((note, index) => (
                    <article key={`${history.packageId}-audit-note-${index}`} className="list-row">
                      <div className="list-row__title">Operator note {index + 1}</div>
                      <p>{note}</p>
                    </article>
                  ))}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
