"use client";

import { startTransition, useEffect, useState } from "react";
import type {
  StoryBriefV1,
  StoryGenerationJobV1,
  StoryPackageBuildV1,
  StoryPackageDraftV1,
  StoryPackageReleaseV1,
} from "@lumosreading/contracts";
import {
  buildStoryBriefCards,
  buildStoryGenerationJobCards,
  buildDemoStoryPackageHistory,
  buildStoryPackageDraftCards,
  buildStoryPackageHistoryView,
  fallbackStoryBriefIndex,
  fallbackStoryGenerationJobIndex,
  fallbackStoryPackageDraftIndex,
  type StoryBriefCard,
  type StoryGenerationJobCard,
  type StoryPackageDraftCard,
  type StoryPackageHistoryView,
} from "@lumosreading/sdk";
import { storyGenerationServices, storyPackageReleaseServices } from "@/lib/api";

export type ResourceStatus = "loading" | "live" | "fallback";
export type ActionStatus = "idle" | "running" | "success" | "error";

export type StudioReleaseBoard = {
  drafts: StoryPackageDraftCard[];
  histories: StoryPackageHistoryView[];
  historiesByPackageId: Record<string, StoryPackageHistoryView>;
  generatedAt: string;
};

export type StudioReleaseBoardSummary = {
  packageCount: number;
  activeReleaseCount: number;
  recalledReleaseCount: number;
  supersededReleaseCount: number;
  packagesWithFindings: number;
  totalFindings: number;
  packagesWithoutActiveRelease: number;
  packagesReadyToPublish: number;
};

export type StudioActionState = {
  status: ActionStatus;
  message: string | null;
  error: string | null;
};

export type StudioGenerationBoard = {
  briefs: StoryBriefCard[];
  jobs: StoryGenerationJobCard[];
  generatedAt: string;
};

const STUDIO_OPERATOR_ID = "studio.operator";

function parseTime(value: string): number {
  return Number.isNaN(Date.parse(value)) ? 0 : Date.parse(value);
}

function sortByUpdatedAt<T extends { updatedAt: string }>(left: T, right: T): number {
  return parseTime(right.updatedAt) - parseTime(left.updatedAt);
}

function describeError(caught: unknown, fallbackMessage: string): string {
  if (caught instanceof Error && caught.message) {
    return caught.message;
  }

  return fallbackMessage;
}

function buildHistoryLookup(
  histories: StoryPackageHistoryView[],
): Record<string, StoryPackageHistoryView> {
  return Object.fromEntries(
    histories.map((history) => [history.packageId, history]),
  ) as Record<string, StoryPackageHistoryView>;
}

function buildFallbackBoard(): StudioReleaseBoard {
  const drafts = buildStoryPackageDraftCards(fallbackStoryPackageDraftIndex).sort(sortByUpdatedAt);
  const histories = [buildStoryPackageHistoryView(buildDemoStoryPackageHistory())].sort(sortByUpdatedAt);

  return {
    drafts,
    histories,
    historiesByPackageId: buildHistoryLookup(histories),
    generatedAt: fallbackStoryPackageDraftIndex.generated_at,
  };
}

function buildFallbackGenerationBoard(): StudioGenerationBoard {
  return {
    briefs: buildStoryBriefCards(fallbackStoryBriefIndex).sort(sortByUpdatedAt),
    jobs: buildStoryGenerationJobCards(fallbackStoryGenerationJobIndex).sort(sortByUpdatedAt),
    generatedAt: fallbackStoryBriefIndex.generated_at,
  };
}

async function fetchStudioReleaseBoard(): Promise<StudioReleaseBoard> {
  const drafts = (await storyPackageReleaseServices.listDraftCards()).sort(sortByUpdatedAt);
  const histories = (
    await Promise.all(
      drafts.map((draft) => storyPackageReleaseServices.getHistoryView(draft.packageId)),
    )
  ).sort(sortByUpdatedAt);

  return {
    drafts,
    histories,
    historiesByPackageId: buildHistoryLookup(histories),
    generatedAt: new Date().toISOString(),
  };
}

async function fetchStudioGenerationBoard(): Promise<StudioGenerationBoard> {
  const [briefs, jobs] = await Promise.all([
    storyGenerationServices.listBriefCards(),
    storyGenerationServices.listJobCards(),
  ]);

  return {
    briefs: briefs.sort(sortByUpdatedAt),
    jobs: jobs.sort(sortByUpdatedAt),
    generatedAt: new Date().toISOString(),
  };
}

export function summarizeStudioReleaseBoard(
  board: StudioReleaseBoard,
): StudioReleaseBoardSummary {
  const releases = board.histories.flatMap((history) => history.releases);

  return {
    packageCount: board.drafts.length,
    activeReleaseCount: releases.filter((release) => release.status === "active").length,
    recalledReleaseCount: releases.filter((release) => release.status === "recalled").length,
    supersededReleaseCount: releases.filter((release) => release.status === "superseded").length,
    packagesWithFindings: board.histories.filter((history) => history.findingCount > 0).length,
    totalFindings: board.histories.reduce(
      (count, history) => count + history.findingCount,
      0,
    ),
    packagesWithoutActiveRelease: board.histories.filter(
      (history) => history.activeReleaseId === null,
    ).length,
    packagesReadyToPublish: board.histories.filter(
      (history) =>
        history.latestBuildId !== null &&
        history.activeReleaseId === null &&
        history.auditStatus === "approved" &&
        history.audit.resolution.action === "release",
    ).length,
  };
}

export function useStudioReleaseBoard() {
  const [board, setBoard] = useState<StudioReleaseBoard>(buildFallbackBoard());
  const [status, setStatus] = useState<ResourceStatus>("loading");
  const [error, setError] = useState<string | null>(null);
  const [actionState, setActionState] = useState<StudioActionState>({
    status: "idle",
    message: null,
    error: null,
  });
  const [refreshToken, setRefreshToken] = useState(0);

  useEffect(() => {
    let active = true;

    setStatus("loading");
    setError(null);

    fetchStudioReleaseBoard()
      .then((nextBoard) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setBoard(nextBoard);
          setStatus("live");
          setError(null);
        });
      })
      .catch((caught) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setBoard(buildFallbackBoard());
          setStatus("fallback");
          setError(
            describeError(caught, "Failed to hydrate the studio release board."),
          );
        });
      });

    return () => {
      active = false;
    };
  }, [refreshToken]);

  function refresh() {
    startTransition(() => {
      setRefreshToken((current) => current + 1);
    });
  }

  async function runAction<T>(
    pendingMessage: string,
    successMessage: string,
    action: () => Promise<T>,
  ): Promise<T | null> {
    startTransition(() => {
      setActionState({
        status: "running",
        message: pendingMessage,
        error: null,
      });
    });

    try {
      const result = await action();

      try {
        const nextBoard = await fetchStudioReleaseBoard();

        startTransition(() => {
          setBoard(nextBoard);
          setStatus("live");
          setError(null);
          setActionState({
            status: "success",
            message: successMessage,
            error: null,
          });
        });
      } catch (refreshCaught) {
        startTransition(() => {
          setActionState({
            status: "error",
            message: `${successMessage} Refresh is required.`,
            error: describeError(
              refreshCaught,
              "Action succeeded but the studio board refresh failed.",
            ),
          });
        });
      }

      return result;
    } catch (caught) {
      startTransition(() => {
        setActionState({
          status: "error",
          message: pendingMessage,
          error: describeError(caught, "Studio operator action failed."),
        });
      });

      return null;
    }
  }

  function triggerBuild(packageId: string, buildReason: string): Promise<StoryPackageBuildV1 | null> {
    return runAction(
      `Building ${packageId}.`,
      `Build created for ${packageId}.`,
      () =>
        storyPackageReleaseServices.triggerBuild(packageId, {
          schema_version: "story-package-build-command.v1",
          build_reason: buildReason,
          requested_by: STUDIO_OPERATOR_ID,
          requested_at: new Date().toISOString(),
        }),
    );
  }

  function publishBuild(
    packageId: string,
    buildId: string,
    releaseChannel: StoryPackageReleaseV1["release_channel"],
    notes: string,
  ): Promise<StoryPackageReleaseV1 | null> {
    return runAction(
      `Publishing ${packageId}.`,
      `Release promoted for ${packageId}.`,
      () =>
        storyPackageReleaseServices.publishBuild(packageId, {
          schema_version: "story-package-release-command.v1",
          build_id: buildId,
          release_channel: releaseChannel,
          requested_by: STUDIO_OPERATOR_ID,
          requested_at: new Date().toISOString(),
          notes,
        }),
    );
  }

  function reviewPackage(
    packageId: string,
    args: {
      auditStatus: string;
      resolutionAction: string;
      notes: string;
    },
  ): Promise<StoryPackageDraftV1 | null> {
    return runAction(
      `Reviewing ${packageId}.`,
      `Review updated for ${packageId}.`,
      () =>
        storyPackageReleaseServices.reviewPackage(packageId, {
          schema_version: "story-package-review-command.v1",
          audit_status: args.auditStatus as
            | "pending"
            | "in_review"
            | "approved"
            | "needs_revision"
            | "rejected"
            | "recalled"
            | "escalated",
          resolution_action: args.resolutionAction as
            | "none"
            | "revise"
            | "block"
            | "release"
            | "recall"
            | "escalate",
          reviewer_type: "human",
          reviewer_id: STUDIO_OPERATOR_ID,
          notes: args.notes,
          requested_by: STUDIO_OPERATOR_ID,
          requested_at: new Date().toISOString(),
        }),
    );
  }

  function recallRelease(
    packageId: string,
    releaseId: string,
    reason: string,
  ): Promise<StoryPackageReleaseV1 | null> {
    return runAction(
      `Recalling ${packageId}.`,
      `Release recalled for ${packageId}.`,
      () =>
        storyPackageReleaseServices.recallRelease(packageId, {
          schema_version: "story-package-recall-command.v1",
          release_id: releaseId,
          requested_by: STUDIO_OPERATOR_ID,
          requested_at: new Date().toISOString(),
          reason,
        }),
    );
  }

  function rollbackRelease(
    packageId: string,
    targetReleaseId: string,
    reason: string,
  ): Promise<StoryPackageReleaseV1 | null> {
    return runAction(
      `Rolling back ${packageId}.`,
      `Rollback created for ${packageId}.`,
      () =>
        storyPackageReleaseServices.rollbackRelease(packageId, {
          schema_version: "story-package-rollback-command.v1",
          target_release_id: targetReleaseId,
          requested_by: STUDIO_OPERATOR_ID,
          requested_at: new Date().toISOString(),
          reason,
        }),
    );
  }

  return {
    board,
    status,
    error,
    actionState,
    refresh,
    triggerBuild,
    publishBuild,
    reviewPackage,
    recallRelease,
    rollbackRelease,
  };
}

export function useStudioGenerationBoard() {
  const [board, setBoard] = useState<StudioGenerationBoard>(buildFallbackGenerationBoard());
  const [status, setStatus] = useState<ResourceStatus>("loading");
  const [error, setError] = useState<string | null>(null);
  const [actionState, setActionState] = useState<StudioActionState>({
    status: "idle",
    message: null,
    error: null,
  });
  const [refreshToken, setRefreshToken] = useState(0);

  useEffect(() => {
    let active = true;

    setStatus("loading");
    setError(null);

    fetchStudioGenerationBoard()
      .then((nextBoard) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setBoard(nextBoard);
          setStatus("live");
          setError(null);
        });
      })
      .catch((caught) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setBoard(buildFallbackGenerationBoard());
          setStatus("fallback");
          setError(
            describeError(caught, "Failed to hydrate the studio generation board."),
          );
        });
      });

    return () => {
      active = false;
    };
  }, [refreshToken]);

  function refresh() {
    startTransition(() => {
      setRefreshToken((current) => current + 1);
    });
  }

  async function runAction<T>(
    pendingMessage: string,
    successMessage: string,
    action: () => Promise<T>,
  ): Promise<T | null> {
    startTransition(() => {
      setActionState({
        status: "running",
        message: pendingMessage,
        error: null,
      });
    });

    try {
      const result = await action();

      try {
        const nextBoard = await fetchStudioGenerationBoard();

        startTransition(() => {
          setBoard(nextBoard);
          setStatus("live");
          setError(null);
          setActionState({
            status: "success",
            message: successMessage,
            error: null,
          });
        });
      } catch (refreshCaught) {
        startTransition(() => {
          setActionState({
            status: "error",
            message: `${successMessage} Refresh is required.`,
            error: describeError(
              refreshCaught,
              "Action succeeded but the studio generation board refresh failed.",
            ),
          });
        });
      }

      return result;
    } catch (caught) {
      startTransition(() => {
        setActionState({
          status: "error",
          message: pendingMessage,
          error: describeError(caught, "Studio generation action failed."),
        });
      });

      return null;
    }
  }

  function createBrief(input: {
    title: string;
    theme: string;
    premise: string;
    languageMode: string;
    ageBand: string;
    desiredPageCount: number;
    sourceOutline?: string;
  }): Promise<StoryBriefV1 | null> {
    return runAction(
      `Creating brief ${input.title}.`,
      `Brief created for ${input.title}.`,
      () =>
        storyGenerationServices.createBrief({
          schema_version: "story-brief-command.v1",
          title: input.title,
          theme: input.theme,
          premise: input.premise,
          language_mode: input.languageMode,
          age_band: input.ageBand,
          desired_page_count: input.desiredPageCount,
          source_outline: input.sourceOutline ?? null,
          requested_by: STUDIO_OPERATOR_ID,
          requested_at: new Date().toISOString(),
        }),
    );
  }

  function generateDraft(briefId: string): Promise<StoryGenerationJobV1 | null> {
    return runAction(
      `Generating draft for ${briefId}.`,
      `Draft generated for ${briefId}.`,
      () =>
        storyGenerationServices.generateDraft(briefId, {
          schema_version: "story-generation-job-command.v1",
          job_type: "brief_to_draft",
          provider_preference: "placeholder",
          notes: "Generate a reviewable package draft from the studio briefs board.",
          requested_by: STUDIO_OPERATOR_ID,
          requested_at: new Date().toISOString(),
        }),
    );
  }

  function generateMedia(
    briefId: string,
    providerPreference: "qwen" | "vertex" | "openai" | "placeholder" = "qwen",
  ): Promise<StoryGenerationJobV1 | null> {
    return runAction(
      `Generating media for ${briefId}.`,
      `Media generated for ${briefId}.`,
      () =>
        storyGenerationServices.generateMedia(briefId, {
          schema_version: "story-generation-job-command.v1",
          job_type: "draft_to_media",
          provider_preference: providerPreference,
          notes: "Generate images and audio for the reviewable package draft.",
          requested_by: STUDIO_OPERATOR_ID,
          requested_at: new Date().toISOString(),
        }),
    );
  }

  return {
    board,
    status,
    error,
    actionState,
    refresh,
    createBrief,
    generateDraft,
    generateMedia,
  };
}
