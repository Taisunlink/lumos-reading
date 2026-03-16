import type { ReadingEventV1 } from "@lumosreading/contracts";
import { formatDateTime, formatEventType, formatMinutesFromMs } from "@/lib/format";
import { children, dashboardModel, recentEvents } from "@/lib/page-models";

function getNumericPayloadField(event: ReadingEventV1, field: string): number | null {
  const value = event.payload[field];
  return typeof value === "number" ? value : null;
}

function getStringPayloadField(event: ReadingEventV1, field: string): string | null {
  const value = event.payload[field];
  return typeof value === "string" ? value : null;
}

function describeEvent(event: ReadingEventV1): string {
  if (event.event_type === "session_completed") {
    const dwellMs = getNumericPayloadField(event, "dwell_ms");
    return dwellMs === null ? "Completed session with no dwell payload." : `Completed in ${formatMinutesFromMs(dwellMs)}.`;
  }

  if (event.event_type === "word_revealed_translation") {
    const word = getStringPayloadField(event, "word") ?? "Unknown word";
    const revealCount = getNumericPayloadField(event, "reveal_count") ?? 0;
    return `${word} translation revealed ${revealCount} time(s).`;
  }

  if (event.event_type === "page_replayed_audio") {
    const replayCount = getNumericPayloadField(event, "replay_count") ?? 0;
    return `Audio replayed ${replayCount} time(s) on the same page.`;
  }

  if (event.event_type === "assist_mode_enabled") {
    const assistMode = getStringPayloadField(event, "assist_mode") ?? "unknown";
    return `Assist mode enabled: ${assistMode}.`;
  }

  return "Typed reading event recorded.";
}

export default function ProgressPage() {
  const childNameById = new Map(children.map((child) => [child.id, child.name]));
  const packageTitleById = new Map(dashboardModel.packageQueue.map((pkg) => [pkg.package_id, pkg.title]));
  const uniqueSessions = new Set(recentEvents.map((event) => event.session_id)).size;
  const totalDwellMs = recentEvents.reduce(
    (sum, event) => sum + (getNumericPayloadField(event, "dwell_ms") ?? 0),
    0,
  );

  const eventTypeCounts = recentEvents.reduce<Record<string, number>>((accumulator, event) => {
    accumulator[event.event_type] = (accumulator[event.event_type] ?? 0) + 1;
    return accumulator;
  }, {});

  const orderedEventTypeCounts = Object.entries(eventTypeCounts).sort((left, right) => right[1] - left[1]);

  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Progress and instrumentation</div>
        <h1>Progress should come from typed events, not from UI assumptions.</h1>
        <p className="hero-card__lead">
          This page is the first caregiver-facing proof that <code>ReadingEventV1</code> can support completion,
          replay, translation, and assist-mode insights without relying on ad hoc frontend state.
        </p>
        <div className="metrics-grid">
          <article className="metric-card">
            <div className="metric-card__label">Tracked events</div>
            <div className="metric-card__value">{recentEvents.length}</div>
            <div className="metric-card__meta">Recent instrumentation entries ready for caregiver reporting.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Unique sessions</div>
            <div className="metric-card__value">{uniqueSessions}</div>
            <div className="metric-card__meta">Session identifiers already survive across multiple event types.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Observed dwell</div>
            <div className="metric-card__value">{formatMinutesFromMs(totalDwellMs)}</div>
            <div className="metric-card__meta">Completed-session payloads can feed reports, reminders, and retention logic.</div>
          </article>
        </div>
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Recent event timeline</h2>
            <span className="panel-card__eyebrow">Derived from shared contract payloads</span>
          </div>
          <div className="timeline">
            {recentEvents.map((event) => (
              <article key={event.event_id} className="timeline-item">
                <div className="panel-card__header">
                  <span className="timeline-item__title">{formatEventType(event.event_type)}</span>
                  <span className="panel-card__eyebrow">{formatDateTime(event.occurred_at)}</span>
                </div>
                <div className="list-row__meta">
                  <span>{childNameById.get(event.child_id) ?? event.child_id}</span>
                  <span>{packageTitleById.get(event.package_id) ?? event.package_id}</span>
                  <span>{event.surface}</span>
                </div>
                <p>{describeEvent(event)}</p>
              </article>
            ))}
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Event coverage</h2>
            <span className="panel-card__eyebrow">What the current sample already proves</span>
          </div>
          <div className="stack-list">
            {orderedEventTypeCounts.map(([eventType, count]) => (
              <article key={eventType} className="list-row">
                <p className="list-row__title">{formatEventType(eventType)}</p>
                <div className="list-row__meta">
                  <span>{count} event(s)</span>
                  <span className="mono">{eventType}</span>
                </div>
              </article>
            ))}
          </div>
          <div className="note-card">
            Next step: ingest batched events from the child surface and add caregiver-facing rollups instead of keeping
            analytics logic in page components.
          </div>
        </article>
      </section>
    </main>
  );
}

