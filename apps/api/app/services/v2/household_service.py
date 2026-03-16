from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.services.v2.fixtures import DEMO_HOUSEHOLD_ID, HOUSEHOLD_FIXTURES


@dataclass(frozen=True)
class HouseholdSnapshot:
    household_id: UUID
    household_name: str
    featured_package_id: UUID


class HouseholdService(Protocol):
    def get_household(self, household_id: UUID) -> HouseholdSnapshot:
        """Return household-level caregiver metadata."""


class DemoHouseholdService:
    def get_household(self, household_id: UUID) -> HouseholdSnapshot:
        fixture = HOUSEHOLD_FIXTURES.get(household_id)

        if fixture is None:
            fallback = HOUSEHOLD_FIXTURES[DEMO_HOUSEHOLD_ID]
            return HouseholdSnapshot(
                household_id=household_id,
                household_name="Demo household",
                featured_package_id=fallback.featured_package_id,
            )

        return HouseholdSnapshot(
            household_id=household_id,
            household_name=fixture.household_name,
            featured_package_id=fixture.featured_package_id,
        )
