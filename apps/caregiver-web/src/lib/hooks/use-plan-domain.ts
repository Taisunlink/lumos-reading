"use client";

import {
  demoHouseholdId,
  fallbackPlanDomainView,
} from "@lumosreading/sdk";
import { caregiverSubdomainServices } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";

export function usePlanDomain() {
  const { value, status, error } = useCaregiverResource(
    demoHouseholdId,
    fallbackPlanDomainView,
    caregiverSubdomainServices.plan.getWeeklyPlan,
    "Failed to hydrate caregiver plan.",
  );

  return {
    planDomain: value,
    status,
    error,
  };
}
