"use client";

import { getCaregiverHousehold } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";
import { demoHouseholdId, fallbackCaregiverHousehold } from "@/lib/page-models";
import { buildHouseholdOverview } from "@/lib/services/household-service";

export function useHouseholdOverview() {
  const { value, status, error } = useCaregiverResource(
    demoHouseholdId,
    fallbackCaregiverHousehold,
    getCaregiverHousehold,
    "Failed to hydrate caregiver household.",
  );

  return {
    overview: buildHouseholdOverview(value),
    status,
    error,
  };
}
