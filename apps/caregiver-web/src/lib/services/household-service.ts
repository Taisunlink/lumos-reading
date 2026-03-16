import type { CaregiverHouseholdV1, StoryPackageManifestV1 } from "@lumosreading/contracts";

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

export function buildHouseholdOverview(household: CaregiverHouseholdV1): HouseholdOverview {
  return {
    householdId: household.household_id,
    householdName: household.household_name,
    featuredPackageId: household.featured_package_id,
    featuredPackage: household.featured_package,
    packageQueue: household.package_queue,
    childCount: household.child_count,
    packageCount: household.package_queue.length,
    completedSessions: household.progress_metrics.completed_sessions,
    translationReveals: household.progress_metrics.translation_reveals,
    generatedAt: household.generated_at,
  };
}
