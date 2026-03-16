from typing import Protocol
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverChildSummaryV1
from app.services.v2.fixtures import DEMO_HOUSEHOLD_ID, HOUSEHOLD_CHILD_FIXTURES


class ChildService(Protocol):
    def list_children(self, household_id: UUID) -> list[CaregiverChildSummaryV1]:
        """Return the household child summaries used by caregiver surfaces."""


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
