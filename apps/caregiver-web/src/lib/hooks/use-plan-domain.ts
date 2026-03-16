"use client";

import { useCaregiverDashboardState } from "@/lib/caregiver-dashboard-context";
import { buildPlanDomainView } from "@/lib/services/plan-service";

export function usePlanDomain() {
  const { dashboard, status, error } = useCaregiverDashboardState();

  return {
    planDomain: buildPlanDomainView(dashboard),
    status,
    error,
  };
}
