import type { ReactNode } from "react";

export function formatDateTime(value?: string | null): string {
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

export function formatMinutes(seconds: number): string {
  return `${Math.max(1, Math.round(seconds / 60))} min`;
}

export function titleize(value: string): string {
  return value
    .split(/[_-]/)
    .filter(Boolean)
    .map((part) => part.slice(0, 1).toUpperCase() + part.slice(1))
    .join(" ");
}

export function toneForWorkflowState(state: string): string {
  switch (state) {
    case "released":
      return "is-green";
    case "built":
      return "is-sky";
    case "recalled":
      return "is-red";
    default:
      return "is-amber";
  }
}

export function toneForReviewStatus(status: string): string {
  switch (status) {
    case "approved":
      return "is-green";
    case "limited_release":
      return "is-amber";
    case "recalled":
      return "is-red";
    default:
      return "is-neutral";
  }
}

export function toneForAuditStatus(status: string): string {
  switch (status) {
    case "approved":
      return "is-green";
    case "in_review":
      return "is-sky";
    case "recalled":
    case "rejected":
    case "escalated":
      return "is-red";
    case "needs_revision":
      return "is-amber";
    default:
      return "is-neutral";
  }
}

export function toneForReleaseStatus(status: string): string {
  switch (status) {
    case "active":
      return "is-green";
    case "recalled":
      return "is-red";
    case "superseded":
      return "is-neutral";
    default:
      return "is-sky";
  }
}

export function toneForSeverity(severity: string): string {
  switch (severity) {
    case "critical":
    case "high":
      return "is-red";
    case "medium":
      return "is-amber";
    case "low":
      return "is-green";
    default:
      return "is-neutral";
  }
}

export function toneForResourceStatus(status: string): string {
  switch (status) {
    case "live":
    case "success":
      return "is-green";
    case "loading":
    case "running":
      return "is-sky";
    case "fallback":
      return "is-amber";
    case "error":
      return "is-red";
    default:
      return "is-neutral";
  }
}

export function StatusBadge({
  label,
  tone,
}: {
  label: string;
  tone: string;
}) {
  return <span className={`status-badge ${tone}`}>{label}</span>;
}

export function MetricCard({
  label,
  value,
  meta,
}: {
  label: string;
  value: ReactNode;
  meta?: ReactNode;
}) {
  return (
    <article className="metric-card">
      <div className="metric-card__label">{label}</div>
      <div className="metric-card__value">{value}</div>
      {meta ? <div className="metric-card__meta">{meta}</div> : null}
    </article>
  );
}

export function MetaPair({
  label,
  value,
}: {
  label: string;
  value: ReactNode;
}) {
  return (
    <div className="meta-pair">
      <div className="meta-pair__label">{label}</div>
      <div className="meta-pair__value">{value}</div>
    </div>
  );
}

export function EmptyState({
  title,
  copy,
}: {
  title: string;
  copy: string;
}) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p>{copy}</p>
    </div>
  );
}

export function FeedbackBanner({
  status,
  message,
  error,
}: {
  status: string;
  message?: string | null;
  error?: string | null;
}) {
  if (!message && !error) {
    return null;
  }

  return (
    <div className={`feedback-banner ${toneForResourceStatus(status)}`}>
      {message ? <div className="feedback-banner__title">{message}</div> : null}
      {error ? <p>{error}</p> : null}
    </div>
  );
}
