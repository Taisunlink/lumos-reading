from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.schemas.v2.monetization import (
    HouseholdEntitlementPackageV1,
    HouseholdEntitlementV1,
)
from app.services.v2.fixtures import (
    DEMO_HOUSEHOLD_ID,
    HOUSEHOLD_ENTITLEMENT_FIXTURES,
    HOUSEHOLD_FIXTURES,
)
from app.services.v2.story_package_service import StoryPackageService


@dataclass(frozen=True)
class PackageAccessResolution:
    package_id: UUID
    access_state: str
    entitlement_source: str
    reason: str

    @property
    def is_entitled(self) -> bool:
        return self.access_state == "entitled"


class EntitlementService(Protocol):
    def get_household_entitlement(self, household_id: UUID) -> HouseholdEntitlementV1:
        """Return the household entitlement state."""

    def is_package_entitled(self, household_id: UUID, package_id: UUID) -> bool:
        """Return whether the household can currently access the package."""

    def resolve_package_access(
        self,
        household_id: UUID,
        package_id: UUID,
    ) -> PackageAccessResolution | None:
        """Resolve package access inside the household scope."""

    def list_household_ids(self) -> list[UUID]:
        """Return all household identifiers in scope for the demo."""


class DemoEntitlementService:
    def __init__(
        self,
        story_package_service: StoryPackageService,
        clock: Callable[[], datetime],
    ):
        self.story_package_service = story_package_service
        self.clock = clock

    def get_household_entitlement(self, household_id: UUID) -> HouseholdEntitlementV1:
        fixture = HOUSEHOLD_ENTITLEMENT_FIXTURES.get(
            household_id,
            HOUSEHOLD_ENTITLEMENT_FIXTURES[DEMO_HOUSEHOLD_ID],
        )
        package_access = []

        for item in fixture.package_access:
            story_package = self.story_package_service.get_story_package(item.package_id)
            package_access.append(
                HouseholdEntitlementPackageV1(
                    package_id=item.package_id,
                    title=story_package.title,
                    language_mode=story_package.language_mode,
                    age_band=story_package.age_band,
                    release_channel=story_package.release_channel,
                    access_state=item.access_state,
                    entitlement_source=item.entitlement_source,
                    reason=item.reason,
                )
            )

        return HouseholdEntitlementV1(
            household_id=household_id,
            subscription_status=fixture.subscription_status,
            access_state=fixture.access_state,
            plan_name=fixture.plan_name,
            billing_interval=fixture.billing_interval,
            trial_ends_at=fixture.trial_ends_at,
            renews_at=fixture.renews_at,
            package_access=package_access,
            entitled_package_count=sum(1 for item in package_access if item.access_state == "entitled"),
            locked_package_count=sum(1 for item in package_access if item.access_state == "locked"),
            generated_at=self.clock(),
        )

    def resolve_package_access(
        self,
        household_id: UUID,
        package_id: UUID,
    ) -> PackageAccessResolution | None:
        fixture = HOUSEHOLD_ENTITLEMENT_FIXTURES.get(
            household_id,
            HOUSEHOLD_ENTITLEMENT_FIXTURES[DEMO_HOUSEHOLD_ID],
        )
        match = next(
            (item for item in fixture.package_access if item.package_id == package_id),
            None,
        )

        if match is None:
            return None

        return PackageAccessResolution(
            package_id=match.package_id,
            access_state=match.access_state,
            entitlement_source=match.entitlement_source,
            reason=match.reason,
        )

    def is_package_entitled(self, household_id: UUID, package_id: UUID) -> bool:
        resolution = self.resolve_package_access(household_id, package_id)
        return resolution is not None and resolution.is_entitled

    def list_household_ids(self) -> list[UUID]:
        return list(HOUSEHOLD_FIXTURES.keys())
