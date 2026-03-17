"use client";

import { startTransition, useEffect, useState } from "react";
import {
  demoHouseholdId,
  fallbackPlanDomainView,
  fallbackProgressDomainView,
  type PlanDomainView,
  type ProgressDomainView,
} from "@lumosreading/sdk";
import { caregiverSubdomainServices } from "@/lib/api";

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
  return useStudioResource<PlanDomainView>(
    fallbackPlanDomainView,
    caregiverSubdomainServices.plan.getWeeklyPlan,
    "Failed to hydrate studio plan preview.",
  );
}

export function useStudioProgress() {
  return useStudioResource<ProgressDomainView>(
    fallbackProgressDomainView,
    caregiverSubdomainServices.progress.getInsights,
    "Failed to hydrate studio progress preview.",
  );
}
