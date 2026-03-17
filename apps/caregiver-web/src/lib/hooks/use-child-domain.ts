"use client";

import {
  demoHouseholdId,
  fallbackChildDomainView,
} from "@lumosreading/sdk";
import { caregiverSubdomainServices } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";

export function useChildDomain() {
  const { value, status, error } = useCaregiverResource(
    demoHouseholdId,
    fallbackChildDomainView,
    caregiverSubdomainServices.children.getAssignments,
    "Failed to hydrate caregiver children.",
  );

  return {
    childDomain: value,
    status,
    error,
  };
}
