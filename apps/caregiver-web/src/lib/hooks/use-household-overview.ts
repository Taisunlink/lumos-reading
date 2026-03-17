"use client";

import {
  demoHouseholdId,
  fallbackHouseholdOverview,
} from "@lumosreading/sdk";
import { caregiverSubdomainServices } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";

export function useHouseholdOverview() {
  const { value, status, error } = useCaregiverResource(
    demoHouseholdId,
    fallbackHouseholdOverview,
    caregiverSubdomainServices.household.getOverview,
    "Failed to hydrate caregiver household.",
  );

  return {
    overview: value,
    status,
    error,
  };
}
