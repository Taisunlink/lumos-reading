"use client";

import { useCaregiverDashboardState } from "@/lib/caregiver-dashboard-context";
import { buildChildDomainView } from "@/lib/services/child-service";

export function useChildDomain() {
  const { dashboard, status, error } = useCaregiverDashboardState();

  return {
    childDomain: buildChildDomainView(dashboard),
    status,
    error,
  };
}
