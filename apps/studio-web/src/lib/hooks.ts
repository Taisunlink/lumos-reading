"use client";

import { startTransition, useEffect, useState } from "react";
import type { CaregiverPlanV1, CaregiverProgressV1 } from "@lumosreading/contracts";
import { getCaregiverPlan, getCaregiverProgress } from "@/lib/api";
import {
  demoHouseholdId,
  fallbackCaregiverPlan,
  fallbackCaregiverProgress,
} from "@/lib/fallbacks";

type ResourceStatus = "loading" | "live" | "fallback";

function useStudioResource<T>(
  initialValue: T,
  load: (householdId: string) => Promise<T>,
  fallbackMessage: string,
) {
  const [value, setValue] = useState<T>(initialValue);
  const [status, setStatus] = useState<ResourceStatus>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    setStatus("loading");
    setError(null);

    load(demoHouseholdId)
      .then((response) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setValue(response);
          setStatus("live");
          setError(null);
        });
      })
      .catch((caught) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setValue(initialValue);
          setStatus("fallback");
          setError(caught instanceof Error ? caught.message : fallbackMessage);
        });
      });

    return () => {
      active = false;
    };
  }, [fallbackMessage, initialValue, load]);

  return { value, status, error };
}

export function useStudioPlan() {
  return useStudioResource<CaregiverPlanV1>(
    fallbackCaregiverPlan,
    getCaregiverPlan,
    "Failed to hydrate studio plan preview.",
  );
}

export function useStudioProgress() {
  return useStudioResource<CaregiverProgressV1>(
    fallbackCaregiverProgress,
    getCaregiverProgress,
    "Failed to hydrate studio progress preview.",
  );
}
