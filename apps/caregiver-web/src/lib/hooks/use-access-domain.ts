"use client";

import {
  demoHouseholdId,
  fallbackAccessDomainView,
  fallbackWeeklyValueDomainView,
} from "@lumosreading/sdk";
import { monetizationServices } from "@/lib/api/v2";
import { useCaregiverResource } from "@/lib/hooks/use-caregiver-resource";

function combineStatus(left: string, right: string): "loading" | "live" | "fallback" {
  if (left === "fallback" || right === "fallback") {
    return "fallback";
  }

  if (left === "loading" || right === "loading") {
    return "loading";
  }

  return "live";
}

export function useAccessDomain() {
  const accessResource = useCaregiverResource(
    demoHouseholdId,
    fallbackAccessDomainView,
    monetizationServices.access.getAccessOverview,
    "Failed to hydrate household entitlement.",
  );
  const valueResource = useCaregiverResource(
    demoHouseholdId,
    fallbackWeeklyValueDomainView,
    monetizationServices.value.getWeeklyValue,
    "Failed to hydrate weekly value report.",
  );

  function refresh() {
    accessResource.refresh();
    valueResource.refresh();
  }

  return {
    accessDomain: accessResource.value,
    valueDomain: valueResource.value,
    status: combineStatus(accessResource.status, valueResource.status),
    error: accessResource.error ?? valueResource.error,
    refresh,
  };
}
