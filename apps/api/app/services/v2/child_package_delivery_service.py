from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from app.schemas.v2.story_package import StoryPackageManifestV1
from app.services.v2.child_service import ChildService
from app.services.v2.entitlement_service import EntitlementService
from app.services.v2.package_access_store import (
    record_blocked_package_request,
    record_entitled_package_delivery,
)
from app.services.v2.story_package_service import StoryPackageService


class ChildPackageDeliveryNotFoundError(LookupError):
    """Raised when the target child cannot be resolved."""


class ChildPackageDeliveryAccessError(PermissionError):
    """Raised when the child household is not entitled to the requested package."""


class ChildPackageDeliveryService:
    def __init__(
        self,
        child_service: ChildService,
        entitlement_service: EntitlementService,
        story_package_service: StoryPackageService,
        clock: Callable[[], datetime],
    ):
        self.child_service = child_service
        self.entitlement_service = entitlement_service
        self.story_package_service = story_package_service
        self.clock = clock

    def get_package(self, child_id: UUID, package_id: UUID) -> StoryPackageManifestV1:
        assignment = self.child_service.get_child_assignment(child_id)

        if assignment is None:
            raise ChildPackageDeliveryNotFoundError(f"Unknown child id: {child_id}")

        access = self.entitlement_service.resolve_package_access(
            assignment.household_id,
            package_id,
        )

        if access is None:
            raise ChildPackageDeliveryNotFoundError(
                f"Unknown package id {package_id} for household {assignment.household_id}"
            )

        if not access.is_entitled:
            record_blocked_package_request(
                household_id=assignment.household_id,
                child_id=child_id,
                package_id=package_id,
                surface="child-app",
                reason=access.reason,
                occurred_at=self.clock(),
            )
            raise ChildPackageDeliveryAccessError(
                f"Package {package_id} is locked for child {child_id}: {access.reason}"
            )

        story_package = self.story_package_service.get_story_package(package_id)
        record_entitled_package_delivery(
            household_id=assignment.household_id,
            child_id=child_id,
            package_id=package_id,
            surface="child-app",
            reason=access.reason,
            occurred_at=self.clock(),
        )
        return story_package
