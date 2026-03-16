"use client";

import { startTransition, useEffect, useState } from "react";
import type { StoryPackageManifestV1 } from "@lumosreading/contracts";
import { getStoryPackage } from "@/lib/api/v2";

type CatalogStatus = "loading" | "live" | "fallback";

function toRecord(packages: StoryPackageManifestV1[]): Record<string, StoryPackageManifestV1> {
  const record: Record<string, StoryPackageManifestV1> = {};

  for (const item of packages) {
    record[item.package_id] = item;
  }

  return record;
}

export function useStoryPackageCatalog(
  packageIds: string[],
  initialPackages: StoryPackageManifestV1[],
) {
  const packageIdsKey = packageIds.join("|");
  const [packagesById, setPackagesById] = useState<Record<string, StoryPackageManifestV1>>(() =>
    toRecord(initialPackages),
  );
  const [status, setStatus] = useState<CatalogStatus>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const requestedPackageIds = packageIdsKey.length > 0 ? packageIdsKey.split("|") : [];

    if (requestedPackageIds.length === 0) {
      setStatus("fallback");
      setError(null);
      return () => {
        active = false;
      };
    }

    setStatus("loading");
    setError(null);

    async function loadCatalog() {
      const fallbackPackagesById = toRecord(initialPackages);
      const results = await Promise.allSettled(
        requestedPackageIds.map((packageId) => getStoryPackage(packageId)),
      );

      if (!active) {
        return;
      }

      const nextPackagesById = { ...fallbackPackagesById };
      let successCount = 0;
      let lastError: string | null = null;

      results.forEach((result, index) => {
        const packageId = requestedPackageIds[index];

        if (result.status === "fulfilled") {
          nextPackagesById[packageId] = result.value;
          successCount += 1;
          return;
        }

        lastError =
          result.reason instanceof Error
            ? result.reason.message
            : `Failed to load story package ${packageId}.`;
      });

      startTransition(() => {
        setPackagesById(nextPackagesById);
        setStatus(successCount === requestedPackageIds.length ? "live" : "fallback");
        setError(successCount === requestedPackageIds.length ? null : lastError);
      });
    }

    loadCatalog().catch((caught) => {
      if (!active) {
        return;
      }

      startTransition(() => {
        setPackagesById(toRecord(initialPackages));
        setStatus("fallback");
        setError(caught instanceof Error ? caught.message : "Failed to hydrate story package catalog.");
      });
    });

    return () => {
      active = false;
    };
  }, [initialPackages, packageIdsKey]);

  const fallbackPackagesById = toRecord(initialPackages);
  const packages = packageIds
    .map((packageId) => packagesById[packageId] ?? fallbackPackagesById[packageId])
    .filter((item): item is StoryPackageManifestV1 => Boolean(item));

  return {
    packages,
    packagesById,
    status,
    error,
  };
}
