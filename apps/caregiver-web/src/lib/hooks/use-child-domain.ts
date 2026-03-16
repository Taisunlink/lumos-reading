"use client";

import { getCaregiverChildren } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";
import { demoHouseholdId, fallbackCaregiverChildren } from "@/lib/page-models";
import { buildChildDomainView } from "@/lib/services/child-service";

export function useChildDomain() {
  const { value, status, error } = useCaregiverResource(
    demoHouseholdId,
    fallbackCaregiverChildren,
    getCaregiverChildren,
    "Failed to hydrate caregiver children.",
  );

  return {
    childDomain: buildChildDomainView(value),
    status,
    error,
  };
}
