"use client";

import Link from "next/link";
import { useState } from "react";
import {
  EmptyState,
  FeedbackBanner,
  MetricCard,
  StatusBadge,
  formatDateTime,
  titleize,
} from "@/components/studio-ui";
import { useStudioGenerationBoard } from "@/lib/hooks";

type BriefFormState = {
  title: string;
  theme: string;
  premise: string;
  languageMode: string;
  ageBand: string;
  desiredPageCount: string;
  sourceOutline: string;
};

const defaultFormState: BriefFormState = {
  title: "New Gentle Prompt",
  theme: "patience",
  premise: "A child practices waiting for a small promise to return.",
  languageMode: "en-US",
  ageBand: "4-6",
  desiredPageCount: "3",
  sourceOutline: "Keep the emotional arc calm and bedtime-friendly.",
};

function toneForBriefStatus(status: string): string {
  switch (status) {
    case "media_ready":
      return "is-green";
    case "draft_ready":
      return "is-sky";
    case "failed":
      return "is-red";
    default:
      return "is-amber";
  }
}

function toneForJobStatus(status: string): string {
  switch (status) {
    case "succeeded":
      return "is-green";
    case "failed":
      return "is-red";
    case "running":
      return "is-sky";
    default:
      return "is-neutral";
  }
}

function toneForProvider(provider: string | null): string {
  return provider === "placeholder" ? "is-amber" : "is-neutral";
}

export function StudioBriefBoard() {
  const {
    board,
    status,
    error,
    actionState,
    refresh,
    createBrief,
    generateDraft,
    generateMedia,
  } = useStudioGenerationBoard();
  const [formState, setFormState] = useState<BriefFormState>(defaultFormState);
  const [providerByBriefId, setProviderByBriefId] = useState<Record<string, "qwen" | "vertex" | "openai" | "placeholder">>({});
  const isBusy = actionState.status === "running";
  const draftReadyCount = board.briefs.filter((brief) => brief.status === "draft_ready").length;
  const mediaReadyCount = board.briefs.filter((brief) => brief.status === "media_ready").length;

  async function submitBrief() {
    const created = await createBrief({
      title: formState.title,
      theme: formState.theme,
      premise: formState.premise,
      languageMode: formState.languageMode,
      ageBand: formState.ageBand,
      desiredPageCount: Number(formState.desiredPageCount),
      sourceOutline: formState.sourceOutline,
    });

    if (created) {
      setFormState(defaultFormState);
    }
  }

  return (
    <div className="studio-page">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Phase 5 AI supply chain</div>
        <h1>Briefs become reviewable drafts before they ever touch runtime release.</h1>
        <p className="hero-card__lead">
          This board keeps AI on the backstage path: create a brief, assemble a draft, generate
          media with provider fallback, then move to package review and release.
        </p>

        <div className="button-row">
          <button type="button" className="button" onClick={refresh} disabled={isBusy}>
            Refresh briefs
          </button>
          <Link href="/packages" className="button is-secondary">
            Open package workspace
          </Link>
        </div>

        <FeedbackBanner
          status={status}
          message={`Generation board synced ${formatDateTime(board.generatedAt)}.`}
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
          label="Brief backlog"
          value={board.briefs.length}
          meta="Editorial requests currently tracked through the AI supply chain"
        />
        <MetricCard
          label="Draft-ready briefs"
          value={draftReadyCount}
          meta="Briefs with text assembled and waiting on media or review"
        />
        <MetricCard
          label="Media-ready briefs"
          value={mediaReadyCount}
          meta="Briefs that already have generated asset keys and reviewable package drafts"
        />
      </section>

      <section className="workspace-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <div>
              <div className="panel-card__eyebrow">Create brief</div>
              <h2>Editorial intake</h2>
            </div>
          </div>

          <div className="stack-list">
            <label>
              <span className="panel-card__eyebrow">Title</span>
              <input
                value={formState.title}
                onChange={(event) =>
                  setFormState((current) => ({ ...current, title: event.target.value }))
                }
              />
            </label>
            <label>
              <span className="panel-card__eyebrow">Theme</span>
              <input
                value={formState.theme}
                onChange={(event) =>
                  setFormState((current) => ({ ...current, theme: event.target.value }))
                }
              />
            </label>
            <label>
              <span className="panel-card__eyebrow">Premise</span>
              <textarea
                rows={4}
                value={formState.premise}
                onChange={(event) =>
                  setFormState((current) => ({ ...current, premise: event.target.value }))
                }
              />
            </label>
            <label>
              <span className="panel-card__eyebrow">Source outline</span>
              <textarea
                rows={4}
                value={formState.sourceOutline}
                onChange={(event) =>
                  setFormState((current) => ({ ...current, sourceOutline: event.target.value }))
                }
              />
            </label>
            <div className="detail-grid">
              <label>
                <span className="panel-card__eyebrow">Language</span>
                <select
                  value={formState.languageMode}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, languageMode: event.target.value }))
                  }
                >
                  <option value="en-US">en-US</option>
                  <option value="zh-CN">zh-CN</option>
                </select>
              </label>
              <label>
                <span className="panel-card__eyebrow">Age band</span>
                <select
                  value={formState.ageBand}
                  onChange={(event) =>
                    setFormState((current) => ({ ...current, ageBand: event.target.value }))
                  }
                >
                  <option value="4-6">4-6</option>
                  <option value="6-8">6-8</option>
                </select>
              </label>
            </div>
            <label>
              <span className="panel-card__eyebrow">Page count</span>
              <select
                value={formState.desiredPageCount}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    desiredPageCount: event.target.value,
                  }))
                }
              >
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
              </select>
            </label>
            <div className="button-row">
              <button
                type="button"
                className="button"
                onClick={() => void submitBrief()}
                disabled={
                  isBusy ||
                  !formState.title.trim() ||
                  !formState.theme.trim() ||
                  !formState.premise.trim()
                }
              >
                Create brief
              </button>
            </div>
          </div>
        </article>

        <div className="page-stack">
          <article className="panel-card">
            <div className="panel-card__header">
              <div>
                <div className="panel-card__eyebrow">Brief queue</div>
                <h2>Generation stages</h2>
              </div>
              <StatusBadge
                label={`${board.briefs.length} briefs`}
                tone="is-neutral"
              />
            </div>

            {board.briefs.length === 0 ? (
              <EmptyState
                title="No briefs yet"
                copy="Create the first editorial brief to start the AI supply chain."
              />
            ) : (
              <div className="stack-list">
                {board.briefs.map((brief) => (
                  <article key={brief.briefId} className="list-row">
                    <div className="list-row__header">
                      <div>
                        <div className="list-row__title">{brief.title}</div>
                        <div className="list-row__copy">{brief.premise}</div>
                      </div>

                      <div className="status-row">
                        <StatusBadge
                          label={titleize(brief.status)}
                          tone={toneForBriefStatus(brief.status)}
                        />
                        <StatusBadge
                          label={brief.languageMode}
                          tone="is-neutral"
                        />
                      </div>
                    </div>

                    <div className="list-row__meta">
                      <span>{brief.theme}</span>
                      <span>{brief.ageBand}</span>
                      <span>{brief.desiredPageCount} pages</span>
                      <span>{formatDateTime(brief.updatedAt)}</span>
                    </div>

                    <div className="meta-pairs">
                      <div className="meta-pair">
                        <div className="meta-pair__label">Package id</div>
                        <div className="meta-pair__value mono">{brief.packageId}</div>
                      </div>
                      <div className="meta-pair">
                        <div className="meta-pair__label">Latest job</div>
                        <div className="meta-pair__value">{brief.latestJobId ?? "None"}</div>
                      </div>
                    </div>

                    {brief.latestFailureReason ? (
                      <div className="note-card">
                        <p>{brief.latestFailureReason}</p>
                      </div>
                    ) : null}

                    <div className="button-row">
                      <button
                        type="button"
                        className="button"
                        onClick={() => void generateDraft(brief.briefId)}
                        disabled={isBusy || brief.status === "media_ready"}
                      >
                        Generate draft
                      </button>
                      <select
                        value={providerByBriefId[brief.briefId] ?? "qwen"}
                        onChange={(event) =>
                          setProviderByBriefId((current) => ({
                            ...current,
                            [brief.briefId]: event.target.value as
                              | "qwen"
                              | "vertex"
                              | "openai"
                              | "placeholder",
                          }))
                        }
                      >
                        <option value="qwen">Prefer qwen</option>
                        <option value="vertex">Prefer vertex</option>
                        <option value="openai">Prefer openai</option>
                        <option value="placeholder">Force placeholder</option>
                      </select>
                      <button
                        type="button"
                        className="button is-secondary"
                        onClick={() =>
                          void generateMedia(
                            brief.briefId,
                            providerByBriefId[brief.briefId] ?? "qwen",
                          )
                        }
                        disabled={isBusy || brief.status === "draft_requested"}
                      >
                        Generate media
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </article>

          <article className="panel-card">
            <div className="panel-card__header">
              <div>
                <div className="panel-card__eyebrow">Generation jobs</div>
                <h2>Provider fallback and asset output</h2>
              </div>
              <StatusBadge
                label={`${board.jobs.length} jobs`}
                tone="is-neutral"
              />
            </div>

            {board.jobs.length === 0 ? (
              <EmptyState
                title="No generation jobs"
                copy="Jobs will appear here once the first draft or media request runs."
              />
            ) : (
              <div className="timeline">
                {board.jobs.map((job) => (
                  <article key={job.jobId} className="timeline-item">
                    <div className="list-row__header">
                      <div>
                        <div className="timeline-item__title">
                          {titleize(job.jobType)} / {job.packageId}
                        </div>
                        <div className="list-row__copy">{job.briefId}</div>
                      </div>

                      <div className="status-row">
                        <StatusBadge
                          label={titleize(job.status)}
                          tone={toneForJobStatus(job.status)}
                        />
                        {job.selectedProvider ? (
                          <StatusBadge
                            label={job.selectedProvider}
                            tone={toneForProvider(job.selectedProvider)}
                          />
                        ) : null}
                      </div>
                    </div>

                    <div className="list-row__meta">
                      <span>{job.generatedAssetCount} asset keys</span>
                      <span>{formatDateTime(job.updatedAt)}</span>
                    </div>

                    {job.failureReason ? <p>{job.failureReason}</p> : null}
                  </article>
                ))}
              </div>
            )}
          </article>
        </div>
      </section>
    </div>
  );
}
