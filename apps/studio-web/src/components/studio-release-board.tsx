"use client";

import {
  FeedbackBanner,
  MetricCard,
  StatusBadge,
  formatDateTime,
  titleize,
  toneForAuditStatus,
  toneForReleaseStatus,
  toneForReviewStatus,
} from "@/components/studio-ui";
import {
  summarizeStudioReleaseBoard,
  useStudioReleaseBoard,
} from "@/lib/hooks";

export function StudioReleaseBoard() {
  const {
    board,
    status,
    error,
    actionState,
    refresh,
    recallRelease,
    rollbackRelease,
  } = useStudioReleaseBoard();
  const summary = summarizeStudioReleaseBoard(board);
  const releaseRows = board.histories
    .flatMap((history) =>
      history.releases.map((release) => ({
        history,
        build:
          history.builds.find((build) => build.build_id === release.build_id) ?? null,
        release,
      })),
    )
    .sort(
      (left, right) =>
        Date.parse(right.release.released_at) - Date.parse(left.release.released_at),
    );
  const isBusy = actionState.status === "running";

  return (
    <div className="studio-page">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Release control</div>
        <h1>Every runtime package resolves through a release ledger.</h1>
        <p className="hero-card__lead">
          This page shows active, recalled, and superseded releases with the audit state that
          justified them. Rollback is only offered for non-recalled history.
        </p>
        <div className="button-row">
          <button type="button" className="button" onClick={refresh} disabled={isBusy}>
            Refresh release board
          </button>
        </div>
        <FeedbackBanner
          status={status}
          message={`Release board synced ${formatDateTime(board.generatedAt)}.`}
          error={error}
        />
        <FeedbackBanner
          status={actionState.status}
          message={actionState.message}
          error={actionState.error}
        />
      </section>

      <section className="metrics-grid">
        <MetricCard
          label="Active releases"
          value={summary.activeReleaseCount}
          meta="Current runtime resolution targets"
        />
        <MetricCard
          label="Superseded releases"
          value={summary.supersededReleaseCount}
          meta="Rollback candidates still visible to operators"
        />
        <MetricCard
          label="Recalled releases"
          value={summary.recalledReleaseCount}
          meta="Blocked from rollback by Phase 3 release rules"
        />
      </section>

      <article className="panel-card">
        <div className="panel-card__header">
          <div>
            <div className="panel-card__eyebrow">Release history</div>
            <h2>Ledger by runtime publication event</h2>
          </div>
          <StatusBadge
            label={`${releaseRows.length} release records`}
            tone="is-neutral"
          />
        </div>

        <div className="timeline">
          {releaseRows.map(({ history, build, release }) => (
            <article key={release.release_id} className="timeline-item">
              <div className="list-row__header">
                <div>
                  <div className="timeline-item__title">
                    {history.title} / release v{release.release_version}
                  </div>
                  <div className="list-row__copy mono">{release.runtime_lookup_key}</div>
                </div>

                <div className="status-row">
                  <StatusBadge
                    label={titleize(release.status)}
                    tone={toneForReleaseStatus(release.status)}
                  />
                  <StatusBadge
                    label={titleize(history.reviewStatus)}
                    tone={toneForReviewStatus(history.reviewStatus)}
                  />
                  <StatusBadge
                    label={titleize(history.auditStatus)}
                    tone={toneForAuditStatus(history.auditStatus)}
                  />
                </div>
              </div>

              <div className="list-row__meta">
                <span>{release.release_channel}</span>
                <span>{formatDateTime(release.released_at)}</span>
                <span>
                  {build
                    ? `Build v${build.build_version} / ${build.build_reason}`
                    : `Build ${release.build_id}`}
                </span>
              </div>

              <p>{release.notes ?? "No release note recorded."}</p>

              <div className="button-row">
                {release.status === "active" ? (
                  <button
                    type="button"
                    className="button is-danger"
                    onClick={() =>
                      void recallRelease(
                        history.packageId,
                        release.release_id,
                        `Recalled release ${release.release_version} from studio release board.`,
                      )
                    }
                    disabled={isBusy}
                  >
                    Recall active release
                  </button>
                ) : null}
                {release.status === "superseded" ? (
                  <button
                    type="button"
                    className="button is-secondary"
                    onClick={() =>
                      void rollbackRelease(
                        history.packageId,
                        release.release_id,
                        `Rollback to release ${release.release_version} from studio release board.`,
                      )
                    }
                    disabled={isBusy}
                  >
                    Roll back to this release
                  </button>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      </article>
    </div>
  );
}
