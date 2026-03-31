from collections.abc import Callable
from datetime import datetime

from app.schemas.v2.caregiver import (
    CaregiverAssignmentCommandV1,
    CaregiverAssignmentResponseV1,
)
from app.services.v2.child_home_service import ChildHomeService
from app.services.v2.child_service import ChildService
from app.services.v2.plan_service import PlanService
from app.services.v2.story_package_service import StoryPackageService


class CaregiverAssignmentService:
    def __init__(
        self,
        child_service: ChildService,
        child_home_service: ChildHomeService,
        plan_service: PlanService,
        story_package_service: StoryPackageService,
        clock: Callable[[], datetime],
    ):
        self.child_service = child_service
        self.child_home_service = child_home_service
        self.plan_service = plan_service
        self.story_package_service = story_package_service
        self.clock = clock

    def assign_package(
        self,
        command: CaregiverAssignmentCommandV1,
    ) -> CaregiverAssignmentResponseV1:
        previous_assignment = self.child_service.get_child_assignment(command.child_id)

        if previous_assignment is None or previous_assignment.household_id != command.household_id:
            raise ValueError(
                f"Unknown child id {command.child_id} for household {command.household_id}"
            )

        updated_assignment = self.child_service.assign_package(
            command.household_id,
            command.child_id,
            command.package_id,
        )

        if updated_assignment is None:
            raise ValueError(
                f"Unknown child id {command.child_id} for household {command.household_id}"
            )

        plan = self.plan_service.get_household_plan(command.household_id)
        package_map = {
            story_package.package_id: story_package
            for story_package in plan.package_queue
        }
        current_package = package_map.get(command.package_id)

        if current_package is None:
            raise ValueError(
                f"Unknown package id {command.package_id} for household {command.household_id}"
            )

        return CaregiverAssignmentResponseV1(
            schema_version="caregiver-assignment-response.v1",
            status="accepted",
            household_id=command.household_id,
            child_id=command.child_id,
            previous_package_id=previous_assignment.child.current_package_id,
            current_package_id=current_package.package_id,
            current_package=current_package,
            child_home=self.child_home_service.get_home(command.child_id),
            accepted_at=self.clock(),
        )
