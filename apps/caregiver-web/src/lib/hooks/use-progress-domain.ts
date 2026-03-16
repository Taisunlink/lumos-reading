"use client";

import { getCaregiverProgress } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";
import { demoHouseholdId, fallbackCaregiverProgress } from "@/lib/page-models";
import { buildProgressDomainView } from "@/lib/services/progress-service";

export function useProgressDomain() {
  const { value, status, error } = useCaregiverResource(
    demoHouseholdId,
    fallbackCaregiverProgress,
    getCaregiverProgress,
    "Failed to hydrate caregiver progress.",
  );

  return {
    progressDomain: buildProgressDomainView(value),
    status,
    error,
  };
}
