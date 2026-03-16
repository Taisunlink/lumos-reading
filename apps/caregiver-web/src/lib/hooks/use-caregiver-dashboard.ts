"use client";

import { startTransition, useEffect, useState } from "react";
import type { CaregiverDashboardV1 } from "@lumosreading/contracts";
import { getCaregiverDashboard } from "@/lib/api/v2";

type DashboardStatus = "loading" | "live" | "fallback";

export function useCaregiverDashboard(
  householdId: string,
  initialDashboard: CaregiverDashboardV1,
) {
  const [dashboard, setDashboard] = useState<CaregiverDashboardV1>(initialDashboard);
  const [status, setStatus] = useState<DashboardStatus>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    setStatus("loading");
    setError(null);

    getCaregiverDashboard(householdId)
      .then((response) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setDashboard(response);
          setStatus("live");
          setError(null);
        });
      })
      .catch((caught) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setDashboard(initialDashboard);
          setStatus("fallback");
          setError(
            caught instanceof Error ? caught.message : "Failed to hydrate caregiver dashboard.",
          );
        });
      });

    return () => {
      active = false;
    };
  }, [householdId, initialDashboard]);

  return {
    dashboard,
    status,
    error,
  };
}
