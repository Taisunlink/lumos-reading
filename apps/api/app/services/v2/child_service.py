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


class DemoChildService:
    def list_children(self, household_id: UUID) -> list[CaregiverChildSummaryV1]:
        fixtures = HOUSEHOLD_CHILD_FIXTURES.get(
            household_id,
            HOUSEHOLD_CHILD_FIXTURES.get(DEMO_HOUSEHOLD_ID, ()),
        )
        return [
            CaregiverChildSummaryV1(
                child_id=fixture.child_id,
                name=fixture.name,
                age_label=fixture.age_label,
                focus=fixture.focus,
                weekly_goal=fixture.weekly_goal,
                current_package_id=fixture.current_package_id,
            )
            for fixture in fixtures
        ]

    def get_child_assignment(self, child_id: UUID) -> ChildAssignmentSnapshot | None:
        for household_id, fixtures in HOUSEHOLD_CHILD_FIXTURES.items():
            for fixture in fixtures:
                if fixture.child_id == child_id:
                    return ChildAssignmentSnapshot(
                        household_id=household_id,
                        child=CaregiverChildSummaryV1(
                            child_id=fixture.child_id,
                            name=fixture.name,
                            age_label=fixture.age_label,
                            focus=fixture.focus,
                            weekly_goal=fixture.weekly_goal,
                            current_package_id=fixture.current_package_id,
                        ),
                    )

        fallback_fixtures = HOUSEHOLD_CHILD_FIXTURES.get(DEMO_HOUSEHOLD_ID, ())
        fallback = next((fixture for fixture in fallback_fixtures if fixture.child_id == child_id), None)

        if fallback is None:
            return None

        return ChildAssignmentSnapshot(
            household_id=DEMO_HOUSEHOLD_ID,
            child=CaregiverChildSummaryV1(
                child_id=fallback.child_id,
                name=fallback.name,
                age_label=fallback.age_label,
                focus=fallback.focus,
                weekly_goal=fallback.weekly_goal,
                current_package_id=fallback.current_package_id,
            ),
        )
