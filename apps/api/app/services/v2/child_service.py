from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverChildSummaryV1
from app.services.v2.fixtures import DEMO_HOUSEHOLD_ID, HOUSEHOLD_CHILD_FIXTURES


@dataclass(frozen=True)
class ChildAssignmentSnapshot:
    household_id: UUID
    child: CaregiverChildSummaryV1


class ChildService(Protocol):
    def list_children(self, household_id: UUID) -> list[CaregiverChildSummaryV1]:
        """Return the household child summaries used by caregiver surfaces."""

    def get_child_assignment(self, child_id: UUID) -> ChildAssignmentSnapshot | None:
        """Resolve a child id back to the owning household and assignment snapshot."""

    def assign_package(
        self,
        household_id: UUID,
        child_id: UUID,
        package_id: UUID,
    ) -> ChildAssignmentSnapshot | None:
        """Update the currently assigned package for a child inside a household."""


CHILD_PACKAGE_ASSIGNMENT_OVERRIDES: dict[UUID, UUID] = {}


def resolve_child_package_id(child_id: UUID, default_package_id: UUID) -> UUID:
    return CHILD_PACKAGE_ASSIGNMENT_OVERRIDES.get(child_id, default_package_id)


def reset_child_package_assignment_overrides() -> None:
    CHILD_PACKAGE_ASSIGNMENT_OVERRIDES.clear()


def build_child_summary(fixture) -> CaregiverChildSummaryV1:
    return CaregiverChildSummaryV1(
        child_id=fixture.child_id,
        name=fixture.name,
        age_label=fixture.age_label,
        focus=fixture.focus,
        weekly_goal=fixture.weekly_goal,
        current_package_id=resolve_child_package_id(
            fixture.child_id,
            fixture.current_package_id,
        ),
    )


class DemoChildService:
    def list_children(self, household_id: UUID) -> list[CaregiverChildSummaryV1]:
        fixtures = HOUSEHOLD_CHILD_FIXTURES.get(
            household_id,
            HOUSEHOLD_CHILD_FIXTURES.get(DEMO_HOUSEHOLD_ID, ()),
        )
        return [build_child_summary(fixture) for fixture in fixtures]

    def get_child_assignment(self, child_id: UUID) -> ChildAssignmentSnapshot | None:
        for household_id, fixtures in HOUSEHOLD_CHILD_FIXTURES.items():
            for fixture in fixtures:
                if fixture.child_id == child_id:
                    return ChildAssignmentSnapshot(
                        household_id=household_id,
                        child=build_child_summary(fixture),
                    )

        fallback_fixtures = HOUSEHOLD_CHILD_FIXTURES.get(DEMO_HOUSEHOLD_ID, ())
        fallback = next((fixture for fixture in fallback_fixtures if fixture.child_id == child_id), None)

        if fallback is None:
            return None

        return ChildAssignmentSnapshot(
            household_id=DEMO_HOUSEHOLD_ID,
            child=build_child_summary(fallback),
        )

    def assign_package(
        self,
        household_id: UUID,
        child_id: UUID,
        package_id: UUID,
    ) -> ChildAssignmentSnapshot | None:
        fixtures = HOUSEHOLD_CHILD_FIXTURES.get(household_id, ())
        fixture = next((item for item in fixtures if item.child_id == child_id), None)

        if fixture is None:
            return None

        if package_id == fixture.current_package_id:
            CHILD_PACKAGE_ASSIGNMENT_OVERRIDES.pop(child_id, None)
        else:
            CHILD_PACKAGE_ASSIGNMENT_OVERRIDES[child_id] = package_id

        return ChildAssignmentSnapshot(
            household_id=household_id,
            child=build_child_summary(fixture),
        )
