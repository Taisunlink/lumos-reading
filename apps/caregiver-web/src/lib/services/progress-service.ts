import type { CaregiverProgressV1, ReadingEventV1 } from "@lumosreading/contracts";
import { formatMinutesFromMs } from "@/lib/format";

export type ProgressTimelineEntry = {
  eventId: string;
  eventType: string;
  occurredAt: string;
  childName: string;
  packageTitle: string;
  surface: string;
  description: string;
};

export type ProgressDomainView = {
  trackedEvents: number;
  uniqueSessions: number;
  totalDwellMs: number;
  timeline: ProgressTimelineEntry[];
  eventCoverage: Array<{ eventType: string; count: number }>;
};

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

export function buildProgressDomainView(progressResource: CaregiverProgressV1): ProgressDomainView {
  const eventTypeCounts = progressResource.recent_events.reduce<Record<string, number>>((accumulator, entry) => {
    accumulator[entry.event.event_type] = (accumulator[entry.event.event_type] ?? 0) + 1;
    return accumulator;
  }, {});

  return {
    trackedEvents: progressResource.recent_events.length,
    uniqueSessions: new Set(progressResource.recent_events.map((entry) => entry.event.session_id)).size,
    totalDwellMs: progressResource.recent_events.reduce(
      (sum, entry) => sum + (getNumericPayloadField(entry.event, "dwell_ms") ?? 0),
      0,
    ),
    timeline: progressResource.recent_events.map((entry) => ({
      eventId: entry.event.event_id,
      eventType: entry.event.event_type,
      occurredAt: entry.event.occurred_at,
      childName: entry.child_name,
      packageTitle: entry.package_title,
      surface: entry.event.surface,
      description: describeEvent(entry.event),
    })),
    eventCoverage: Object.entries(eventTypeCounts)
      .sort((left, right) => right[1] - left[1])
      .map(([eventType, count]) => ({ eventType, count })),
  };
}
