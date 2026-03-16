"use client";

import { useMemo, useState } from "react";
import type {
  ReadingSessionCreateV2,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from "@lumosreading/contracts";
import { API_BASE_URL } from "@/lib/api/v2";
import { useReadingSessionMutation } from "@/lib/hooks/use-reading-session-mutation";
import { useStoryPackageLookup } from "@/lib/hooks/use-story-package-lookup";

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
  const [resultKind, setResultKind] = useState<"package" | "session" | null>(null);
  const packageLookup = useStoryPackageLookup();
  const readingSessionMutation = useReadingSessionMutation();

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

  const result: ResultState =
    resultKind === "package" && packageLookup.data
      ? { kind: "package", payload: packageLookup.data }
      : resultKind === "session" && readingSessionMutation.data
        ? { kind: "session", payload: readingSessionMutation.data }
        : null;

  const loading =
    packageLookup.status === "pending"
      ? "package"
      : readingSessionMutation.status === "pending"
        ? "session"
        : null;

  const error = packageLookup.error ?? readingSessionMutation.error;

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
        <div className="badge-row">
          <span className="badge is-green">shared sdk</span>
          <span className="badge is-sky">hooked queries</span>
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
