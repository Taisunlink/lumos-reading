"use client";

import { useEffect, useState } from "react";
import {
  EmptyState,
  FeedbackBanner,
  MetaPair,
  StatusBadge,
  formatDateTime,
  formatMinutes,
  titleize,
  toneForAuditStatus,
  toneForReleaseStatus,
  toneForReviewStatus,
  toneForSeverity,
  toneForWorkflowState,
} from "@/components/studio-ui";
import { useStudioReleaseBoard } from "@/lib/hooks";

export function StudioPackageWorkspace() {
  const {
    board,
    status,
    error,
    actionState,
    refresh,
    triggerBuild,
    publishBuild,
    recallRelease,
    rollbackRelease,
  } = useStudioReleaseBoard();
  const [selectedPackageId, setSelectedPackageId] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedPackageId || !board.historiesByPackageId[selectedPackageId]) {
      setSelectedPackageId(board.drafts[0]?.packageId ?? null);
    }
  }, [board.drafts, board.historiesByPackageId, selectedPackageId]);

  if (board.drafts.length === 0) {
    return (
      <div className="studio-page">
        <FeedbackBanner
          status={status}
          message="Studio package workspace is empty."
          error={error}
        />
        <EmptyState
          title="No package drafts"
          copy="Phase 4 expects the release API to expose draft cards. The current board is empty."
        />
      </div>
    );
  }

  const selectedDraft =
    board.drafts.find((draft) => draft.packageId === selectedPackageId) ?? board.drafts[0];
  const selectedHistory =
    board.historiesByPackageId[selectedDraft.packageId] ?? board.histories[0];
  const latestBuild =
    selectedHistory.builds.find((build) => build.status === "succeeded") ?? null;
  const activeRelease =
    selectedHistory.releases.find((release) => release.status === "active") ?? null;
  const canPublish =
    latestBuild !== null &&
    selectedHistory.audit.audit_status === "approved" &&
    selectedHistory.audit.resolution.action === "release";
  const isBusy = actionState.status === "running";

  return (
    <div className="studio-page">
      <section className="panel-card">
        <div className="panel-card__header">
          <div>
            <div className="panel-card__eyebrow">Phase 4 package control</div>
            <h2>Build, publish, recall, and rollback from one workspace</h2>
          </div>

          <div className="button-row">
            <button type="button" className="button is-secondary" onClick={refresh} disabled={isBusy}>
              Refresh
            </button>
          </div>
        </div>

        <FeedbackBanner
          status={status}
          message={`Workspace synced ${formatDateTime(board.generatedAt)}.`}
          error={error}
        />
        <FeedbackBanner
          status={actionState.status}
          message={actionState.message}
          error={actionState.error}
        />
      </section>

      <section className="workspace-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <div>
              <div className="panel-card__eyebrow">Draft list</div>
              <h2>Selectable package cards</h2>
            </div>
            <StatusBadge
              label={`${board.drafts.length} packages`}
              tone="is-neutral"
            />
          </div>

          <div className="select-list">
            {board.drafts.map((draft) => (
              <button
                key={draft.packageId}
                type="button"
                className={`select-card${draft.packageId === selectedDraft.packageId ? " is-active" : ""}`}
                onClick={() => setSelectedPackageId(draft.packageId)}
              >
                <div className="list-row__header">
                  <div>
                    <div className="list-row__title">{draft.title}</div>
                    <div className="list-row__copy">{draft.packageId}</div>
                  </div>

                  <div className="status-row">
                    <StatusBadge
                      label={titleize(draft.workflowState)}
                      tone={toneForWorkflowState(draft.workflowState)}
                    />
                  </div>
                </div>

                <div className="status-row">
                  <StatusBadge
                    label={`Review ${titleize(draft.reviewStatus)}`}
                    tone={toneForReviewStatus(draft.reviewStatus)}
                  />
                  <StatusBadge
                    label={`Audit ${titleize(draft.auditStatus)}`}
                    tone={toneForAuditStatus(draft.auditStatus)}
                  />
                  <StatusBadge
                    label={`${draft.findingCount} findings`}
                    tone={draft.findingCount > 0 ? "is-amber" : "is-neutral"}
                  />
                </div>

                <div className="list-row__meta">
                  <span>{draft.sourceType}</span>
                  <span>{draft.releaseChannel}</span>
                  <span>{formatDateTime(draft.updatedAt)}</span>
                </div>
              </button>
            ))}
          </div>
        </article>

        <div className="page-stack">
          <article className="hero-card">
            <div className="hero-card__eyebrow">Package detail</div>
            <h1>{selectedHistory.title}</h1>
            <p className="hero-card__lead">
              {selectedHistory.subtitle ??
                "Use the authoritative release history and audit trail below to decide whether this package should build, publish, recall, or roll back."}
            </p>

            <div className="status-row">
              <StatusBadge
                label={titleize(selectedHistory.workflowState)}
                tone={toneForWorkflowState(selectedHistory.workflowState)}
              />
              <StatusBadge
                label={`Review ${titleize(selectedHistory.reviewStatus)}`}
                tone={toneForReviewStatus(selectedHistory.reviewStatus)}
              />
              <StatusBadge
                label={`Audit ${titleize(selectedHistory.auditStatus)}`}
                tone={toneForAuditStatus(selectedHistory.auditStatus)}
              />
              <StatusBadge
                label={selectedHistory.packagePreview.release_channel}
                tone="is-neutral"
              />
            </div>

            <div className="meta-pairs">
              <MetaPair label="Package id" value={<span className="mono">{selectedHistory.packageId}</span>} />
              <MetaPair label="Source" value={selectedHistory.sourceType} />
              <MetaPair label="Language" value={selectedHistory.packagePreview.language_mode} />
              <MetaPair label="Duration" value={formatMinutes(selectedHistory.packagePreview.estimated_duration_sec)} />
              <MetaPair label="Latest build" value={selectedHistory.latestBuildId ?? "None"} />
              <MetaPair label="Active release" value={selectedHistory.activeReleaseId ?? "None"} />
            </div>

            <div className="button-row">
              <button
                type="button"
                className="button"
                onClick={() =>
                  void triggerBuild(
                    selectedHistory.packageId,
                    `phase4_operator_refresh_${selectedHistory.packagePreview.release_channel}`,
                  )
                }
                disabled={isBusy}
              >
                Build next version
              </button>
              <button
                type="button"
                className="button is-secondary"
                onClick={() =>
                  canPublish && latestBuild
                    ? void publishBuild(
                        selectedHistory.packageId,
                        latestBuild.build_id,
                        "general",
                        `Published via studio ops console from build ${latestBuild.build_version}.`,
                      )
                    : undefined
                }
                disabled={isBusy || !canPublish}
              >
                Publish latest build
              </button>
              <button
                type="button"
                className="button is-danger"
                onClick={() =>
                  activeRelease
                    ? void recallRelease(
                        selectedHistory.packageId,
                        activeRelease.release_id,
                        "Recalled via Phase 4 studio console.",
                      )
                    : undefined
                }
                disabled={isBusy || activeRelease === null}
              >
                Recall active release
              </button>
            </div>
          </article>

          <section className="detail-grid">
            <article className="panel-card">
              <div className="panel-card__header">
                <div>
                  <div className="panel-card__eyebrow">Audit evidence</div>
                  <h2>Review and findings</h2>
                </div>
                <StatusBadge
                  label={titleize(selectedHistory.audit.severity)}
                  tone={toneForSeverity(selectedHistory.audit.severity)}
                />
              </div>

              <div className="meta-pairs">
                <MetaPair
                  label="Audit status"
                  value={
                    <StatusBadge
                      label={titleize(selectedHistory.audit.audit_status)}
                      tone={toneForAuditStatus(selectedHistory.audit.audit_status)}
                    />
                  }
                />
                <MetaPair label="Policy version" value={selectedHistory.audit.policy_version} />
                <MetaPair
                  label="Reviewer"
                  value={`${titleize(selectedHistory.audit.reviewer.reviewer_type)} / ${
                    selectedHistory.audit.reviewer.reviewer_id ?? "unassigned"
                  }`}
                />
                <MetaPair
                  label="Resolution"
                  value={titleize(selectedHistory.audit.resolution.action)}
                />
              </div>

              {selectedHistory.audit.findings.length === 0 ? (
                <div className="note-card">
                  <p>No current audit findings block this package.</p>
                </div>
              ) : (
                <div className="finding-list">
                  {selectedHistory.audit.findings.map((finding) => (
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
                        <span>{finding.page_index == null ? "All pages" : `Page ${finding.page_index}`}</span>
                        <span>{finding.action_required ? "Action required" : "Reviewed"}</span>
                      </div>
                    </article>
                  ))}
                </div>
              )}

              <div className="note-card">
                <p>
                  {selectedHistory.audit.resolution.notes ??
                    "No resolution note was recorded for this audit yet."}
                </p>
              </div>
            </article>

            <article className="panel-card">
              <div className="panel-card__header">
                <div>
                  <div className="panel-card__eyebrow">Operator context</div>
                  <h2>Runtime package and notes</h2>
                </div>
                <StatusBadge
                  label={selectedHistory.packagePreview.difficulty_level}
                  tone="is-neutral"
                />
              </div>

              <div className="meta-pairs">
                <MetaPair label="Story master" value={selectedHistory.packagePreview.story_master_id} />
                <MetaPair label="Variant" value={selectedHistory.packagePreview.story_variant_id} />
                <MetaPair label="Age band" value={selectedHistory.packagePreview.age_band} />
                <MetaPair label="Pages" value={selectedHistory.packagePreview.pages.length} />
              </div>

              <div className="stack-list">
                {selectedHistory.operatorNotes.map((note, index) => (
                  <article key={`${selectedHistory.packageId}-note-${index}`} className="list-row">
                    <div className="list-row__title">Operator note {index + 1}</div>
                    <p>{note}</p>
                  </article>
                ))}
              </div>
            </article>
          </section>

          <section className="detail-grid">
            <article className="panel-card">
              <div className="panel-card__header">
                <div>
                  <div className="panel-card__eyebrow">Build history</div>
                  <h2>Versioned artifacts</h2>
                </div>
                <StatusBadge
                  label={`${selectedHistory.builds.length} builds`}
                  tone="is-neutral"
                />
              </div>

              <div className="timeline">
                {selectedHistory.builds.map((build) => (
                  <article key={build.build_id} className="timeline-item">
                    <div className="timeline-item__title">
                      Build v{build.build_version}
                    </div>
                    <div className="list-row__meta">
                      <span>{titleize(build.status)}</span>
                      <span>{build.build_reason}</span>
                      <span>{formatDateTime(build.requested_at)}</span>
                    </div>
                    <p className="timeline-item__copy mono">{build.manifest_object_key}</p>
                  </article>
                ))}
              </div>
            </article>

            <article className="panel-card">
              <div className="panel-card__header">
                <div>
                  <div className="panel-card__eyebrow">Release history</div>
                  <h2>Publish, recall, and rollback ledger</h2>
                </div>
                <StatusBadge
                  label={`${selectedHistory.releases.length} releases`}
                  tone="is-neutral"
                />
              </div>

              <div className="timeline">
                {selectedHistory.releases.map((release) => (
                  <article key={release.release_id} className="timeline-item">
                    <div className="list-row__header">
                      <div>
                        <div className="timeline-item__title">
                          Release v{release.release_version}
                        </div>
                        <div className="list-row__copy">{release.runtime_lookup_key}</div>
                      </div>
                      <StatusBadge
                        label={titleize(release.status)}
                        tone={toneForReleaseStatus(release.status)}
                      />
                    </div>

                    <div className="list-row__meta">
                      <span>{release.release_channel}</span>
                      <span>{formatDateTime(release.released_at)}</span>
                      <span>{release.rollback_of_release_id ? "rollback" : "direct release"}</span>
                    </div>

                    <p>{release.notes ?? "No operator note recorded."}</p>

                    {release.status !== "recalled" && release.status !== "active" ? (
            <div className="button-row">
                        <button
                          type="button"
                          className="button is-secondary"
                          onClick={() =>
                            void rollbackRelease(
                              selectedHistory.packageId,
                              release.release_id,
                              `Rollback to release ${release.release_version} via studio console.`,
                            )
                          }
                          disabled={isBusy}
                        >
                          Roll back to this release
                        </button>
                      </div>
                    ) : null}
                  </article>
                ))}
            </div>
            <div className="note-card">
              <p>
                Publish is enabled only when the audit status is approved and the audit
                resolution action is release.
              </p>
            </div>
          </article>
          </section>
        </div>
      </section>
    </div>
  );
}
