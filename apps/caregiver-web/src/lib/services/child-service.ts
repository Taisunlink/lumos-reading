import type { CaregiverChildrenV1, StoryPackageManifestV1 } from "@lumosreading/contracts";

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

export function buildChildDomainView(childrenResource: CaregiverChildrenV1): ChildDomainView {
  const children = childrenResource.children.map((child) => ({
    childId: child.child_id,
    name: child.name,
    ageLabel: child.age_label,
    focus: child.focus,
    weeklyGoal: child.weekly_goal,
    currentPackageId: child.current_package_id,
    currentPackage: child.current_package,
  }));

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
    plannedSessions: childrenResource.planned_session_count,
  };
}
