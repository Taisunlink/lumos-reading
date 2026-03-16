"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { CaregiverDashboardV1 } from "@lumosreading/contracts";
import { useCaregiverDashboard } from "@/lib/hooks/use-caregiver-dashboard";
import { demoHouseholdId, fallbackCaregiverDashboard } from "@/lib/page-models";

type DashboardStatus = "loading" | "live" | "fallback";

type CaregiverDashboardContextValue = {
  dashboard: CaregiverDashboardV1;
  status: DashboardStatus;
  error: string | null;
};

const CaregiverDashboardContext = createContext<CaregiverDashboardContextValue | null>(null);

export function CaregiverDashboardProvider({ children }: { children: ReactNode }) {
  const value = useCaregiverDashboard(demoHouseholdId, fallbackCaregiverDashboard);

  return (
    <CaregiverDashboardContext.Provider value={value}>{children}</CaregiverDashboardContext.Provider>
  );
}

export function useCaregiverDashboardState(): CaregiverDashboardContextValue {
  const context = useContext(CaregiverDashboardContext);

  if (context === null) {
    throw new Error("useCaregiverDashboardState must be used within CaregiverDashboardProvider.");
  }

  return context;
}
