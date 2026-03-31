"use client";

import { startTransition, useState } from "react";
import { CAREGIVER_ASSIGNMENT_COMMAND_SCHEMA_VERSION } from "@lumosreading/contracts";

import { formatDurationMinutes, formatEventType } from "@/lib/format";
import { useCaregiverAssignmentMutation } from "@/lib/hooks/use-caregiver-assignment-mutation";
import { useChildDomain } from "@/lib/hooks/use-child-domain";
import { usePlanDomain } from "@/lib/hooks/use-plan-domain";
import { useProgressDomain } from "@/lib/hooks/use-progress-domain";

const supportPatterns = [
  "Keep the primary reading language stable and reveal translation support only on demand.",
  "Assign predictable calm packages for wind-down sessions instead of reusing the same challenge package every night.",
  "Treat caregiver prompts as guided co-reading scaffolds, not extra screen tasks for the child.",
];

export default function ChildrenPage() {
  const { childDomain, status, error, refresh } = useChildDomain();
  const { planDomain } = usePlanDomain();
  const { progressDomain, refresh: refreshProgress } = useProgressDomain();
  const assignmentMutation = useCaregiverAssignmentMutation();
  const [selectedPackageIds, setSelectedPackageIds] = useState<Record<string, string>>({});
  const [activeChildId, setActiveChildId] = useState<string | null>(null);
  const { children, supportSignals, bilingualAssignments, plannedSessions } = childDomain;
  const latestProgressByChildId = progressDomain.timeline.reduce<
    Record<string, (typeof progressDomain.timeline)[number]>
  >((accumulator, entry) => {
    const currentEntry = accumulator[entry.childId];

    if (!currentEntry || entry.occurredAt > currentEntry.occurredAt) {
      accumulator[entry.childId] = entry;
    }

    return accumulator;
  }, {});

  async function assignPackage(childId: string, packageId: string) {
    setActiveChildId(childId);

    try {
      await assignmentMutation.mutate({
        schema_version: CAREGIVER_ASSIGNMENT_COMMAND_SCHEMA_VERSION,
        household_id: childDomain.householdId,
        child_id: childId,
        package_id: packageId,
        source: "caregiver-web",
        requested_at: new Date().toISOString(),
      });
      refresh();
      refreshProgress();
    } catch {
      return;
    }
  }

  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Child profiles and package fit</div>
        <h1>Assignments stay tied to developmental goals, not just to content inventory.</h1>
        <p className="hero-card__lead">
          Each child card reflects the current package assignment, support focus, and the weekly target that the
          caregiver surface should help manage.
        </p>
        <div className="badge-row">
          <span className={`badge ${status === "live" ? "is-green" : status === "loading" ? "is-sky" : "is-warm"}`}>
            {status === "live" ? "live child service" : status === "loading" ? "syncing child service" : "fallback child service"}
          </span>
        </div>
        {error ? <div className="note-card">{error}</div> : null}
        <div className="metrics-grid">
          <article className="metric-card">
            <div className="metric-card__label">Active children</div>
            <div className="metric-card__value">{children.length}</div>
            <div className="metric-card__meta">Profiles with an assigned package and weekly goal.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Bilingual assignments</div>
            <div className="metric-card__value">{bilingualAssignments}</div>
            <div className="metric-card__meta">Profiles currently using a package tagged for translation assistance.</div>
          </article>
          <article className="metric-card">
            <div className="metric-card__label">Planned sessions</div>
            <div className="metric-card__value">{plannedSessions}</div>
            <div className="metric-card__meta">Weekly plan entries already mapped to household needs.</div>
          </article>
        </div>
      </section>

      <section className="card-grid">
        {children.map((child) => (
          <article key={child.childId} className="panel-card">
            <div className="panel-card__header">
              <div>
                <h2>{child.name}</h2>
                <p className="panel-card__eyebrow">{child.ageLabel}</p>
              </div>
              <span className="badge is-green">{child.currentPackage.language_mode}</span>
            </div>

            <p>{child.focus}</p>

            <div className="badge-row">
              {child.currentPackage.tags?.map((tag) => (
                <span key={tag} className="badge">
                  {tag}
                </span>
              ))}
            </div>

            <div className="meta-pairs">
              <div className="meta-pair">
                <span className="meta-pair__label">Weekly goal</span>
                <span className="meta-pair__value">{child.weeklyGoal}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Package</span>
                <span className="meta-pair__value">{child.currentPackage.title}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Difficulty</span>
                <span className="meta-pair__value">{child.currentPackage.difficulty_level}</span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Expected session</span>
                <span className="meta-pair__value">
                  {formatDurationMinutes(child.currentPackage.estimated_duration_sec)}
                </span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Latest reading status</span>
                <span className="meta-pair__value">
                  {latestProgressByChildId[child.childId]?.description ?? "No reading event yet."}
                </span>
              </div>
              <div className="meta-pair">
                <span className="meta-pair__label">Latest package outcome</span>
                <span className="meta-pair__value">
                  {latestProgressByChildId[child.childId]
                    ? `${latestProgressByChildId[child.childId].packageTitle} / ${formatEventType(
                        latestProgressByChildId[child.childId].eventType,
                      )}`
                    : "Waiting for the first completed loop."}
                </span>
              </div>
            </div>

            <div className="api-workbench__controls">
              <select
                className="api-workbench__input"
                value={selectedPackageIds[child.childId] ?? child.currentPackageId}
                onChange={(event) => {
                  const nextPackageId = event.target.value;

                  startTransition(() => {
                    setSelectedPackageIds((previous) => ({
                      ...previous,
                      [child.childId]: nextPackageId,
                    }));
                  });
                }}
              >
                {planDomain.packageQueue.map((storyPackage) => (
                  <option key={storyPackage.package_id} value={storyPackage.package_id}>
                    {storyPackage.title} / {storyPackage.language_mode} / {storyPackage.difficulty_level}
                  </option>
                ))}
              </select>
              <div className="button-row">
                <button
                  className="button"
                  disabled={
                    assignmentMutation.status === "pending" ||
                    (selectedPackageIds[child.childId] ?? child.currentPackageId) ===
                      child.currentPackageId
                  }
                  onClick={() =>
                    void assignPackage(
                      child.childId,
                      selectedPackageIds[child.childId] ?? child.currentPackageId,
                    )
                  }
                >
                  {assignmentMutation.status === "pending" && activeChildId === child.childId
                    ? "Saving assignment..."
                    : "Assign package"}
                </button>
              </div>
            </div>

            {assignmentMutation.status === "success" &&
            assignmentMutation.data?.child_id === child.childId ? (
              <div className="note-card">
                Assignment saved. The child home shelf will pick up the updated package on the next refresh.
              </div>
            ) : null}

            {assignmentMutation.status === "error" && activeChildId === child.childId ? (
              <div className="note-card">{assignmentMutation.error}</div>
            ) : null}
          </article>
        ))}
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Assignment heuristics</h2>
            <span className="panel-card__eyebrow">Business logic before UI polish</span>
          </div>
          <ul className="clean-list">
            {supportPatterns.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Current support signals</h2>
            <span className="panel-card__eyebrow">What the caregiver should monitor</span>
          </div>
          <div className="stack-list">
            {supportSignals.map((signal) => (
              <article key={signal.childId} className="list-row">
                <p className="list-row__title">{signal.name}</p>
                <div className="list-row__meta">
                  <span>{signal.focus}</span>
                </div>
                <div className="badge-row">
                  <span className="badge is-sky">{signal.ageBand}</span>
                  <span className="badge">{signal.releaseChannel}</span>
                  <span className="badge is-green">{signal.reviewStatus}</span>
                </div>
              </article>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}
