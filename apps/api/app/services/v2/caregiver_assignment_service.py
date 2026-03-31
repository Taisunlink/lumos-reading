from collections.abc import Callable
from datetime import datetime

from app.schemas.v2.caregiver import (
    CaregiverAssignmentCommandV1,
    CaregiverAssignmentResponseV1,
)
from app.services.v2.child_home_service import ChildHomeService
from app.services.v2.child_service import ChildService
from app.services.v2.entitlement_service import EntitlementService
from app.services.v2.package_access_store import record_blocked_package_request
from app.services.v2.plan_service import PlanService
from app.services.v2.story_package_service import StoryPackageService


class CaregiverAssignmentNotFoundError(ValueError):
    """Raised when the target child cannot be resolved inside the household."""


class CaregiverAssignmentValidationError(ValueError):
    """Raised when the requested package is invalid for the household."""


class CaregiverAssignmentAccessError(PermissionError):
    """Raised when the household is not entitled to the requested package."""


class CaregiverAssignmentService:
    def __init__(
        self,
        child_service: ChildService,
        child_home_service: ChildHomeService,
        plan_service: PlanService,
        story_package_service: StoryPackageService,
        entitlement_service: EntitlementService,
        clock: Callable[[], datetime],
    ):
        self.child_service = child_service
        self.child_home_service = child_home_service
        self.plan_service = plan_service
        self.story_package_service = story_package_service
        self.entitlement_service = entitlement_service
        self.clock = clock

    def assign_package(
        self,
        command: CaregiverAssignmentCommandV1,
    ) -> CaregiverAssignmentResponseV1:
        previous_assignment = self.child_service.get_child_assignment(command.child_id)

        if previous_assignment is None or previous_assignment.household_id != command.household_id:
            raise CaregiverAssignmentNotFoundError(
                f"Unknown child id {command.child_id} for household {command.household_id}"
            )

        access = self.entitlement_service.resolve_package_access(
            command.household_id,
            command.package_id,
        )

        if access is None:
            raise CaregiverAssignmentValidationError(
                f"Unknown package id {command.package_id} for household {command.household_id}"
            )

        if not access.is_entitled:
            record_blocked_package_request(
                household_id=command.household_id,
                child_id=command.child_id,
                package_id=command.package_id,
                surface=command.source,
                reason=access.reason,
                occurred_at=self.clock(),
            )
            raise CaregiverAssignmentAccessError(
                f"Package {command.package_id} is locked for household {command.household_id}: {access.reason}"
            )

        plan = self.plan_service.get_household_plan(command.household_id)
        package_map = {
            story_package.package_id: story_package
            for story_package in plan.package_queue
        }
        current_package = package_map.get(command.package_id)

        if current_package is None:
            raise CaregiverAssignmentValidationError(
                f"Unknown package id {command.package_id} for household {command.household_id}"
            )

        updated_assignment = self.child_service.assign_package(
            command.household_id,
            command.child_id,
            command.package_id,
        )

        if updated_assignment is None:
            raise CaregiverAssignmentNotFoundError(
                f"Unknown child id {command.child_id} for household {command.household_id}"
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
