import type { CaregiverDashboardV1, ReadingEventV1 } from "@lumosreading/contracts";
import { formatMinutesFromMs } from "@/lib/format";
import { buildPackageMap } from "@/lib/page-models";

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

export function buildProgressDomainView(dashboard: CaregiverDashboardV1): ProgressDomainView {
  const childNameById = new Map(dashboard.children.map((child) => [child.child_id, child.name]));
  const packageTitleById = new Map(
    Object.values(buildPackageMap(dashboard)).map((storyPackage) => [storyPackage.package_id, storyPackage.title]),
  );
  const eventTypeCounts = dashboard.recent_events.reduce<Record<string, number>>((accumulator, event) => {
    accumulator[event.event_type] = (accumulator[event.event_type] ?? 0) + 1;
    return accumulator;
  }, {});

  return {
    trackedEvents: dashboard.recent_events.length,
    uniqueSessions: new Set(dashboard.recent_events.map((event) => event.session_id)).size,
    totalDwellMs: dashboard.recent_events.reduce(
      (sum, event) => sum + (getNumericPayloadField(event, "dwell_ms") ?? 0),
      0,
    ),
    timeline: dashboard.recent_events.map((event) => ({
      eventId: event.event_id,
      eventType: event.event_type,
      occurredAt: event.occurred_at,
      childName: childNameById.get(event.child_id) ?? event.child_id,
      packageTitle: packageTitleById.get(event.package_id) ?? event.package_id,
      surface: event.surface,
      description: describeEvent(event),
    })),
    eventCoverage: Object.entries(eventTypeCounts)
      .sort((left, right) => right[1] - left[1])
      .map(([eventType, count]) => ({ eventType, count })),
  };
}
