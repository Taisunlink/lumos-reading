"use client";

import { useMemo, useState } from "react";
import type {
  ReadingSessionCreateV2,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from "@lumosreading/contracts";
import { API_BASE_URL, createReadingSession, getStoryPackage } from "@/lib/api/v2";

const defaultPackageId = "33333333-3333-3333-3333-333333333333";
const defaultChildId = "55555555-5555-5555-5555-555555555555";

type PackageResult = {
  kind: "package";
  payload: StoryPackageManifestV1;
};

type SessionResult = {
  kind: "session";
  payload: ReadingSessionResponseV2;
};

type ResultState = PackageResult | SessionResult | null;

export function ApiWorkbench() {
  const [packageId, setPackageId] = useState(defaultPackageId);
  const [result, setResult] = useState<ResultState>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<"package" | "session" | null>(null);

  const demoSessionPayload = useMemo<ReadingSessionCreateV2>(
    () => ({
      child_id: defaultChildId,
      package_id: packageId,
      started_at: new Date().toISOString(),
      mode: "read_to_me",
      language_mode: "zh-CN",
      assist_mode: ["read_aloud_sync"],
    }),
    [packageId],
  );

  async function loadPackage() {
    setLoading("package");
    setError(null);
    try {
      const payload = await getStoryPackage(packageId);
      setResult({ kind: "package", payload });
    } catch (caught) {
      setResult(null);
      setError(caught instanceof Error ? caught.message : "Failed to load story package.");
    } finally {
      setLoading(null);
    }
  }

  async function startSession() {
    setLoading("session");
    setError(null);
    try {
      const payload = await createReadingSession(demoSessionPayload);
      setResult({ kind: "session", payload });
    } catch (caught) {
      setResult(null);
      setError(caught instanceof Error ? caught.message : "Failed to create reading session.");
    } finally {
      setLoading(null);
    }
  }

  const renderedResult = result
    ? JSON.stringify(result.payload, null, 2)
    : JSON.stringify(demoSessionPayload, null, 2);

  return (
    <div className="api-workbench">
      <div className="list-row">
        <p className="list-row__title">API workbench</p>
        <div className="list-row__meta">
          <span>Base URL</span>
          <code>{API_BASE_URL}</code>
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
