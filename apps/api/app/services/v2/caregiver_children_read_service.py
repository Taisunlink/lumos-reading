from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverChildAssignmentV1, CaregiverChildrenV1
from app.services.v2.access_errors import NoEntitledPackagesError
from app.services.v2.child_service import ChildService
from app.services.v2.plan_service import PlanService
from app.services.v2.story_package_service import StoryPackageService


class CaregiverChildrenReadService:
    def __init__(
        self,
        child_service: ChildService,
        plan_service: PlanService,
        story_package_service: StoryPackageService,
        clock: Callable[[], datetime],
    ):
        self.child_service = child_service
        self.plan_service = plan_service
        self.story_package_service = story_package_service
        self.clock = clock

    def get_children(self, household_id: UUID) -> CaregiverChildrenV1:
        children = self.child_service.list_children(household_id)
        plan = self.plan_service.get_household_plan(household_id)
        if not plan.package_queue:
            raise NoEntitledPackagesError(f"Household {household_id} has no entitled packages.")
        package_map = {story_package.package_id: story_package for story_package in plan.package_queue}
        fallback_package = plan.package_queue[0]

        return CaregiverChildrenV1(
            household_id=household_id,
            children=[
                CaregiverChildAssignmentV1(
                    child_id=child.child_id,
                    name=child.name,
                    age_label=child.age_label,
                    focus=child.focus,
                    weekly_goal=child.weekly_goal,
                    current_package_id=current_package.package_id,
                    current_package=current_package,
                )
                for child in children
                for current_package in [package_map.get(child.current_package_id) or fallback_package]
            ],
            planned_session_count=len(plan.weekly_plan),
            generated_at=self.clock(),
        )
