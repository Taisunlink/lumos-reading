from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverHouseholdV1
from app.services.v2.access_errors import NoEntitledPackagesError
from app.services.v2.child_service import ChildService
from app.services.v2.household_service import HouseholdService
from app.services.v2.plan_service import PlanService
from app.services.v2.progress_service import ProgressService
from app.services.v2.story_package_service import StoryPackageService


class CaregiverHouseholdReadService:
    def __init__(
        self,
        household_service: HouseholdService,
        child_service: ChildService,
        plan_service: PlanService,
        progress_service: ProgressService,
        story_package_service: StoryPackageService,
        clock: Callable[[], datetime],
    ):
        self.household_service = household_service
        self.child_service = child_service
        self.plan_service = plan_service
        self.progress_service = progress_service
        self.story_package_service = story_package_service
        self.clock = clock

    def get_household(self, household_id: UUID) -> CaregiverHouseholdV1:
        household = self.household_service.get_household(household_id)
        plan = self.plan_service.get_household_plan(household_id)
        if not plan.package_queue:
            raise NoEntitledPackagesError(f"Household {household_id} has no entitled packages.")
        progress = self.progress_service.get_household_progress(household_id)
        package_map = {story_package.package_id: story_package for story_package in plan.package_queue}
        featured_package = package_map.get(household.featured_package_id) or plan.package_queue[0]

        return CaregiverHouseholdV1(
            household_id=household.household_id,
            household_name=household.household_name,
            featured_package_id=featured_package.package_id,
            featured_package=featured_package,
            package_queue=plan.package_queue,
            child_count=len(self.child_service.list_children(household_id)),
            progress_metrics=progress.progress_metrics,
            generated_at=self.clock(),
        )
