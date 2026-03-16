"use client";

import { useCaregiverDashboardState } from "@/lib/caregiver-dashboard-context";
import { buildProgressDomainView } from "@/lib/services/progress-service";

export function useProgressDomain() {
  const { dashboard, status, error } = useCaregiverDashboardState();

  return {
    progressDomain: buildProgressDomainView(dashboard),
    status,
    error,
  };
}
