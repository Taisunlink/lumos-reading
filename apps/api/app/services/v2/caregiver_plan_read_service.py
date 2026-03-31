from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverPlanV1, CaregiverPlannedSessionV1
from app.services.v2.access_errors import NoEntitledPackagesError
from app.services.v2.plan_service import PlanService
from app.services.v2.story_package_service import StoryPackageService


class CaregiverPlanReadService:
    def __init__(
        self,
        plan_service: PlanService,
        story_package_service: StoryPackageService,
        clock: Callable[[], datetime],
    ):
        self.plan_service = plan_service
        self.story_package_service = story_package_service
        self.clock = clock

    def get_plan(self, household_id: UUID) -> CaregiverPlanV1:
        plan = self.plan_service.get_household_plan(household_id)
        if not plan.package_queue:
            raise NoEntitledPackagesError(f"Household {household_id} has no entitled packages.")
        package_map = {story_package.package_id: story_package for story_package in plan.package_queue}

        return CaregiverPlanV1(
            household_id=household_id,
            package_queue=plan.package_queue,
            weekly_plan=[
                CaregiverPlannedSessionV1(
                    day=item.day,
                    mode=item.mode,
                    package_id=item.package_id,
                    objective=item.objective,
                    package=package_map.get(item.package_id)
                    or self.story_package_service.get_story_package(item.package_id),
                )
                for item in plan.weekly_plan
            ],
            generated_at=self.clock(),
        )
