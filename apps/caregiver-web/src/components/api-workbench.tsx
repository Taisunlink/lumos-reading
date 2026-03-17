"use client";

import { useMemo, useState } from "react";
import type {
  ReadingEventBatchRequestV2,
  ReadingEventIngestedResponseV2,
  ReadingSessionCreateV2,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from "@lumosreading/contracts";
import {
  buildDemoReadingEventBatchRequest,
  buildDemoReadingSessionPayload,
  demoChildId,
  demoReadingSessionId,
  demoStoryPackageId,
} from "@lumosreading/sdk";
import { API_BASE_URL } from "@/lib/api/v2";
import { useReadingEventIngestMutation } from "@/lib/hooks/use-reading-event-ingest-mutation";
import { useReadingSessionMutation } from "@/lib/hooks/use-reading-session-mutation";
import { useStoryPackageLookup } from "@/lib/hooks/use-story-package-lookup";

const defaultPackageId = demoStoryPackageId;
const defaultChildId = demoChildId;

type PackageResult = {
  kind: "package";
  payload: StoryPackageManifestV1;
};

type SessionResult = {
  kind: "session";
  payload: ReadingSessionResponseV2;
};

type EventIngestResult = {
  kind: "events";
  payload: ReadingEventIngestedResponseV2;
};

type ResultState = PackageResult | SessionResult | EventIngestResult | null;

export function ApiWorkbench() {
  const [packageId, setPackageId] = useState(defaultPackageId);
  const [resultKind, setResultKind] = useState<"package" | "session" | "events" | null>(null);
  const packageLookup = useStoryPackageLookup();
  const readingSessionMutation = useReadingSessionMutation();
  const readingEventIngestMutation = useReadingEventIngestMutation();

  const demoSessionPayload = useMemo<ReadingSessionCreateV2>(
    () =>
      buildDemoReadingSessionPayload({
        childId: defaultChildId,
        packageId,
      }),
    [packageId],
  );

  const demoEventBatchPayload = useMemo<ReadingEventBatchRequestV2>(
    () =>
      buildDemoReadingEventBatchRequest({
        childId: defaultChildId,
        packageId,
        sessionId: readingSessionMutation.data?.session_id ?? demoReadingSessionId,
      }),
    [packageId, readingSessionMutation.data?.session_id],
  );

  async function loadPackage() {
    setResultKind("package");
    try {
      await packageLookup.lookup(packageId);
    } catch {
      return;
    }
  }

  async function startSession() {
    setResultKind("session");
    try {
      await readingSessionMutation.mutate(demoSessionPayload);
    } catch {
      return;
    }
  }

  async function ingestEvents() {
    setResultKind("events");
    try {
      await readingEventIngestMutation.mutate(demoEventBatchPayload);
    } catch {
      return;
    }
  }

  const result: ResultState =
    resultKind === "package" && packageLookup.data
      ? { kind: "package", payload: packageLookup.data }
      : resultKind === "session" && readingSessionMutation.data
        ? { kind: "session", payload: readingSessionMutation.data }
        : resultKind === "events" && readingEventIngestMutation.data
          ? { kind: "events", payload: readingEventIngestMutation.data }
        : null;

  const loading =
    packageLookup.status === "pending"
      ? "package"
      : readingSessionMutation.status === "pending"
        ? "session"
        : readingEventIngestMutation.status === "pending"
          ? "events"
        : null;

  const error =
    packageLookup.error ??
    readingSessionMutation.error ??
    readingEventIngestMutation.error;

  const renderedResult = result
    ? JSON.stringify(result.payload, null, 2)
    : resultKind === "events"
      ? JSON.stringify(demoEventBatchPayload, null, 2)
      : JSON.stringify(demoSessionPayload, null, 2);

  return (
    <div className="api-workbench">
      <div className="list-row">
        <p className="list-row__title">API workbench</p>
        <div className="list-row__meta">
          <span>Base URL</span>
          <code>{API_BASE_URL}</code>
        </div>
        <div className="badge-row">
          <span className="badge is-green">shared sdk</span>
          <span className="badge is-sky">shared app services</span>
          <span className="badge is-warm">commands plus query</span>
        </div>
        <div className="api-workbench__controls">
          <input
            className="api-workbench__input"
            value={packageId}
            onChange={(event) => setPackageId(event.target.value)}
            placeholder="Story package UUID"
          />
          <div className="button-row">
            <button className="button" onClick={loadPackage} disabled={loading !== null}>
              {loading === "package" ? "Loading package..." : "Load package"}
            </button>
            <button className="button is-secondary" onClick={startSession} disabled={loading !== null}>
              {loading === "session" ? "Creating session..." : "Create demo session"}
            </button>
            <button className="button is-secondary" onClick={ingestEvents} disabled={loading !== null}>
              {loading === "events" ? "Ingesting events..." : "Ingest demo events"}
            </button>
          </div>
        </div>
        {error ? <div className="note-card">{error}</div> : null}
      </div>

      <div className="api-workbench__result">
        <pre>{renderedResult}</pre>
      </div>
    </div>
  );
}
