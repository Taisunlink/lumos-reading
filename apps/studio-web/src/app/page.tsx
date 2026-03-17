"use client";

import {
  caregiverPlanV1Schema,
  caregiverProgressV1Schema,
} from "@lumosreading/contracts";
import {
  createPlaceholderOssStorageService,
} from "@lumosreading/sdk";
import { useStudioPlan, useStudioProgress } from "@/lib/hooks";

function formatMinutes(seconds: number): string {
  return `${Math.max(1, Math.round(seconds / 60))} min`;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function statusClassName(status: "loading" | "live" | "fallback"): string {
  if (status === "live") {
    return "badge is-live";
  }

  if (status === "loading") {
    return "badge is-loading";
  }

  return "badge is-fallback";
}

export default function StudioHomePage() {
  const { value: plan, status: planStatus, error: planError } = useStudioPlan();
  const { value: progress, status: progressStatus, error: progressError } = useStudioProgress();
  const placeholderStorage = createPlaceholderOssStorageService();
  const samplePublicAssetUrl = placeholderStorage.getPublicUrl("story-packages/demo/lantern/cover.png");
  const sampleSignedAssetUrl = placeholderStorage.getSignedUrl(
    "story-packages/demo/lantern/pages/0/audio.mp3",
    900,
  );

  return (
    <main className="studio-shell">
      <div className="studio-stack">
        <section className="hero">
          <div className="eyebrow">Studio Contracts Probe</div>
          <h1>Studio now consumes shared plan and progress services, not raw aggregate blobs.</h1>
          <p>
            This minimal shell is not a CMS yet. It proves a second surface outside caregiver-web can pull the new
            caregiver subdomain page models through <code>@lumosreading/sdk</code> without depending on the aggregate
            dashboard route or re-implementing plan and progress adapters locally.
          </p>
          <div className="badge-row">
            <span className="badge">studio preview</span>
            <span className={statusClassName(planStatus)}>
              {planStatus === "live" ? "live plan contract" : planStatus === "loading" ? "syncing plan contract" : "fallback plan contract"}
            </span>
            <span className={statusClassName(progressStatus)}>
              {progressStatus === "live"
                ? "live progress contract"
                : progressStatus === "loading"
                  ? "syncing progress contract"
                  : "fallback progress contract"}
            </span>
          </div>
          <div className="metrics">
            <article className="metric">
              <div className="metric__label">Plan sessions</div>
              <div className="metric__value">{plan.weeklySessions}</div>
              <div className="note">Schema: {plan.schemaVersion}</div>
            </article>
            <article className="metric">
              <div className="metric__label">Tracked events</div>
              <div className="metric__value">{progress.trackedEvents}</div>
              <div className="note">Schema: {progress.schemaVersion}</div>
            </article>
            <article className="metric">
              <div className="metric__label">Completed sessions</div>
              <div className="metric__value">{progress.completedSessions}</div>
              <div className="note">Generated at {formatDateTime(progress.generatedAt)}</div>
            </article>
          </div>
          {planError ? <div className="note">{planError}</div> : null}
          {progressError ? <div className="note">{progressError}</div> : null}
        </section>

        <section className="grid">
          <article className="panel">
            <div className="panel__header">
              <h2>Plan Contract Preview</h2>
              <span className="badge">{String(caregiverPlanV1Schema.title ?? plan.schemaVersion)}</span>
            </div>
            <div className="rows">
              {plan.sessions.map((item) => (
                <article key={`${item.day}-${item.package.package_id}`} className="row">
                  <p className="row__title">
                    {item.day}: {item.package.title}
                  </p>
                  <div className="row__meta">
                    <span>{item.mode}</span>
                    <span>{item.package.language_mode}</span>
                    <span>{item.package.difficulty_level}</span>
                    <span>{formatMinutes(item.package.estimated_duration_sec)}</span>
                  </div>
                  <p>{item.objective}</p>
                </article>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel__header">
              <h2>Progress Contract Preview</h2>
              <span className="badge">{String(caregiverProgressV1Schema.title ?? progress.schemaVersion)}</span>
            </div>
            <div className="rows">
              {progress.timeline.map((entry) => (
                <article key={entry.eventId} className="row">
                  <p className="row__title">{entry.eventType}</p>
                  <div className="row__meta">
                    <span>{entry.childName}</span>
                    <span>{entry.packageTitle}</span>
                    <span>{entry.surface}</span>
                    <span>{formatDateTime(entry.occurredAt)}</span>
                  </div>
                  <p>{entry.description}</p>
                </article>
              ))}
            </div>
          </article>
        </section>

        <section className="grid">
          <article className="panel">
            <div className="panel__header">
              <h2>Placeholder OSS Contract</h2>
              <span className="badge">shared storage surface</span>
            </div>
            <div className="rows">
              <article className="row">
                <p className="row__title">Public asset URL</p>
                <p className="note">{samplePublicAssetUrl}</p>
              </article>
              <article className="row">
                <p className="row__title">Signed asset URL</p>
                <p className="note">{sampleSignedAssetUrl}</p>
              </article>
            </div>
            <p className="note">
              Until real OSS authorization is wired, signed URLs intentionally collapse to the same placeholder
              endpoint. The interface is stable now, the storage backend can change later.
            </p>
          </article>

          <article className="panel">
            <div className="panel__header">
              <h2>Distribution Signals</h2>
              <span className="badge">plan service output</span>
            </div>
            <div className="rows">
              {plan.packageQueue.map((item) => (
                <article key={item.package_id} className="row">
                  <p className="row__title">{item.title}</p>
                  <div className="row__meta">
                    <span>{item.release_channel}</span>
                    <span>{item.safety.review_status}</span>
                    <span>{item.cover_image_url ? "cover ready" : "cover pending"}</span>
                  </div>
                </article>
              ))}
            </div>
          </article>
        </section>
      </div>
    </main>
  );
}
