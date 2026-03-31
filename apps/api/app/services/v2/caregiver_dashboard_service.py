from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverDashboardV1
from app.services.v2.access_errors import NoEntitledPackagesError
from app.services.v2.child_service import ChildService
from app.services.v2.household_service import HouseholdService
from app.services.v2.plan_service import PlanService
from app.services.v2.progress_service import ProgressService


class Clock(Protocol):
    def __call__(self) -> datetime:
        """Return the current timestamp for aggregate generation."""


class CaregiverDashboardService:
    def __init__(
        self,
        *,
        household_service: HouseholdService,
        child_service: ChildService,
        plan_service: PlanService,
        progress_service: ProgressService,
        clock: Clock | None = None,
    ):
        self.household_service = household_service
        self.child_service = child_service
        self.plan_service = plan_service
        self.progress_service = progress_service
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def get_dashboard(self, household_id: UUID) -> CaregiverDashboardV1:
        household = self.household_service.get_household(household_id)
        plan = self.plan_service.get_household_plan(household_id)
        if not plan.package_queue:
            raise NoEntitledPackagesError(f"Household {household_id} has no entitled packages.")
        progress = self.progress_service.get_household_progress(household_id)
        package_ids = {story_package.package_id for story_package in plan.package_queue}
        fallback_package_id = plan.package_queue[0].package_id

        return CaregiverDashboardV1(
            household_id=household.household_id,
            household_name=household.household_name,
            featured_package_id=(
                household.featured_package_id
                if household.featured_package_id in package_ids
                else fallback_package_id
            ),
            package_queue=plan.package_queue,
            recent_events=progress.recent_events,
            children=[
                child.model_copy(
                    update={
                        "current_package_id": (
                            child.current_package_id
                            if child.current_package_id in package_ids
                            else fallback_package_id
                        )
                    }
                )
                for child in self.child_service.list_children(household_id)
            ],
            weekly_plan=plan.weekly_plan,
            progress_metrics=progress.progress_metrics,
            generated_at=self.clock(),
        )
