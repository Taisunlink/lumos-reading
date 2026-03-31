from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from app.schemas.v2.child_home import ChildHomeV1
from app.services.v2.child_service import ChildService
from app.services.v2.fixtures import CHILD_SUPPORT_MODE_DEFAULTS
from app.services.v2.plan_service import PlanService
from app.services.v2.story_package_service import StoryPackageService


class ChildHomeService:
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

    def get_home(self, child_id: UUID) -> ChildHomeV1:
        assignment = self.child_service.get_child_assignment(child_id)

        if assignment is None:
            raise ValueError(f"Unknown child id: {child_id}")

        plan = self.plan_service.get_household_plan(assignment.household_id)
        package_map = {story_package.package_id: story_package for story_package in plan.package_queue}
        current_package = package_map.get(assignment.child.current_package_id) or self.story_package_service.get_story_package(
            assignment.child.current_package_id
        )
        package_queue = [current_package] + [
            item
            for item in plan.package_queue
            if item.package_id != current_package.package_id
        ]

        return ChildHomeV1(
            child_id=assignment.child.child_id,
            household_id=assignment.household_id,
            child_name=assignment.child.name,
            focus=assignment.child.focus,
            weekly_goal=assignment.child.weekly_goal,
            featured_package_id=package_queue[0].package_id,
            current_package_id=current_package.package_id,
            package_queue=package_queue,
            support_mode_defaults=list(
                CHILD_SUPPORT_MODE_DEFAULTS.get(
                    assignment.child.child_id,
                    ("read_aloud_sync", "focus_support"),
                )
            ),
            generated_at=self.clock(),
        )
