import type { CaregiverDashboardV1, StoryPackageManifestV1 } from "@lumosreading/contracts";
import { buildPackageMap } from "@/lib/page-models";

export type ChildAssignment = {
  childId: string;
  name: string;
  ageLabel: string;
  focus: string;
  weeklyGoal: string;
  currentPackageId: string;
  currentPackage: StoryPackageManifestV1;
};

export type ChildSupportSignal = {
  childId: string;
  name: string;
  focus: string;
  ageBand: string;
  releaseChannel: string;
  reviewStatus: string;
};

export type ChildDomainView = {
  children: ChildAssignment[];
  supportSignals: ChildSupportSignal[];
  bilingualAssignments: number;
  plannedSessions: number;
};

export function buildChildDomainView(dashboard: CaregiverDashboardV1): ChildDomainView {
  const packageMap = buildPackageMap(dashboard);

  const children = dashboard.children.map((child) => {
    const currentPackage =
      packageMap[child.current_package_id] ??
      dashboard.package_queue.find((item) => item.package_id === child.current_package_id) ??
      dashboard.package_queue[0];

    return {
      childId: child.child_id,
      name: child.name,
      ageLabel: child.age_label,
      focus: child.focus,
      weeklyGoal: child.weekly_goal,
      currentPackageId: child.current_package_id,
      currentPackage,
    };
  });

  return {
    children,
    supportSignals: children.map((child) => ({
      childId: child.childId,
      name: child.name,
      focus: child.focus,
      ageBand: child.currentPackage.age_band,
      releaseChannel: child.currentPackage.release_channel,
      reviewStatus: child.currentPackage.safety.review_status,
    })),
    bilingualAssignments: children.filter((child) => child.currentPackage.tags?.includes("bilingual-assist")).length,
    plannedSessions: dashboard.weekly_plan.length,
  };
}
