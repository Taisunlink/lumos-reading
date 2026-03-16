import type { CaregiverDashboardV1, StoryPackageManifestV1 } from "@lumosreading/contracts";
import { buildPackageMap } from "@/lib/page-models";

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

export function buildPlanDomainView(dashboard: CaregiverDashboardV1): PlanDomainView {
  const packageMap = buildPackageMap(dashboard);

  const sessions = dashboard.weekly_plan.map((item) => {
    const storyPackage =
      packageMap[item.package_id] ??
      dashboard.package_queue.find((candidate) => candidate.package_id === item.package_id) ??
      dashboard.package_queue[0];

    return {
      day: item.day,
      mode: item.mode,
      objective: item.objective,
      packageId: item.package_id,
      package: storyPackage,
    };
  });

  return {
    sessions,
    packageQueue: dashboard.package_queue,
    weeklySessions: sessions.length,
    totalPlannedMinutes: sessions.reduce(
      (sum, item) => sum + Math.max(1, Math.round(item.package.estimated_duration_sec / 60)),
      0,
    ),
    scheduledPackageCoverage: new Set(sessions.map((item) => item.package.package_id)).size,
  };
}
