"use client";

import { getCaregiverPlan } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";
import { demoHouseholdId, fallbackCaregiverPlan } from "@/lib/page-models";
import { buildPlanDomainView } from "@/lib/services/plan-service";

export function usePlanDomain() {
  const { value, status, error } = useCaregiverResource(
    demoHouseholdId,
    fallbackCaregiverPlan,
    getCaregiverPlan,
    "Failed to hydrate caregiver plan.",
  );

  return {
    planDomain: buildPlanDomainView(value),
    status,
    error,
  };
}
