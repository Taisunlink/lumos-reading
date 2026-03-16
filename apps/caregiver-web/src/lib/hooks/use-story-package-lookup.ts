"use client";

import { startTransition, useState } from "react";
import type { StoryPackageManifestV1 } from "@lumosreading/contracts";
import { getStoryPackage } from "@/lib/api/v2";

type LookupStatus = "idle" | "pending" | "success" | "error";

export function useStoryPackageLookup() {
  const [data, setData] = useState<StoryPackageManifestV1 | null>(null);
  const [status, setStatus] = useState<LookupStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  async function lookup(packageId: string): Promise<StoryPackageManifestV1> {
    setStatus("pending");
    setError(null);

    try {
      const response = await getStoryPackage(packageId);

      startTransition(() => {
        setData(response);
        setStatus("success");
      });

      return response;
    } catch (caught) {
      const message =
        caught instanceof Error ? caught.message : `Failed to load story package ${packageId}.`;

      startTransition(() => {
        setStatus("error");
        setError(message);
      });

      throw caught;
    }
  }

  return {
    data,
    status,
    error,
    lookup,
  };
}
