"use client";

import { useCaregiverDashboardState } from "@/lib/caregiver-dashboard-context";
import { buildHouseholdOverview } from "@/lib/services/household-service";

export function useHouseholdOverview() {
  const { dashboard, status, error } = useCaregiverDashboardState();

  return {
    overview: buildHouseholdOverview(dashboard),
    status,
    error,
  };
}
