"use client";

import {
  demoHouseholdId,
  fallbackProgressDomainView,
} from "@lumosreading/sdk";
import { caregiverSubdomainServices } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";

export function useProgressDomain() {
  const { value, status, error } = useCaregiverResource(
    demoHouseholdId,
    fallbackProgressDomainView,
    caregiverSubdomainServices.progress.getInsights,
    "Failed to hydrate caregiver progress.",
  );

  return {
    progressDomain: value,
    status,
    error,
  };
}
