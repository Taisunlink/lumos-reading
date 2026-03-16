import type { CaregiverDashboardV1, StoryPackageManifestV1 } from "@lumosreading/contracts";
import { buildPackageMap } from "@/lib/page-models";

export type HouseholdOverview = {
  householdId: string;
  householdName: string;
  featuredPackageId: string;
  featuredPackage: StoryPackageManifestV1;
  packageQueue: StoryPackageManifestV1[];
  childCount: number;
  packageCount: number;
  completedSessions: number;
  translationReveals: number;
  generatedAt: string;
};

export function buildHouseholdOverview(dashboard: CaregiverDashboardV1): HouseholdOverview {
  const packageMap = buildPackageMap(dashboard);
  const featuredPackage = packageMap[dashboard.featured_package_id] ?? dashboard.package_queue[0];

  return {
    householdId: dashboard.household_id,
    householdName: dashboard.household_name,
    featuredPackageId: dashboard.featured_package_id,
    featuredPackage,
    packageQueue: dashboard.package_queue,
    childCount: dashboard.children.length,
    packageCount: dashboard.package_queue.length,
    completedSessions: dashboard.progress_metrics.completed_sessions,
    translationReveals: dashboard.progress_metrics.translation_reveals,
    generatedAt: dashboard.generated_at,
  };
}
