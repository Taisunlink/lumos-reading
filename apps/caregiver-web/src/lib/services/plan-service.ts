import type { CaregiverPlanV1, StoryPackageManifestV1 } from "@lumosreading/contracts";

export type PlannedSession = {
  day: string;
  mode: string;
  objective: string;
  packageId: string;
  package: StoryPackageManifestV1;
};

export type PlanDomainView = {
  sessions: PlannedSession[];
  packageQueue: StoryPackageManifestV1[];
  weeklySessions: number;
  totalPlannedMinutes: number;
  scheduledPackageCoverage: number;
};

export function buildPlanDomainView(planResource: CaregiverPlanV1): PlanDomainView {
  const sessions = planResource.weekly_plan.map((item) => ({
    day: item.day,
    mode: item.mode,
    objective: item.objective,
    packageId: item.package_id,
    package: item.package,
  }));

  return {
    sessions,
    packageQueue: planResource.package_queue,
    weeklySessions: sessions.length,
    totalPlannedMinutes: sessions.reduce(
      (sum, item) => sum + Math.max(1, Math.round(item.package.estimated_duration_sec / 60)),
      0,
    ),
    scheduledPackageCoverage: new Set(sessions.map((item) => item.package.package_id)).size,
  };
}
