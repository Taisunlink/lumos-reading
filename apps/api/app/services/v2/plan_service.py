from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverWeeklyPlanItemV1
from app.schemas.v2.story_package import StoryPackageManifestV1
from app.services.v2.fixtures import (
    DEMO_HOUSEHOLD_ID,
    HOUSEHOLD_PACKAGE_QUEUE_IDS,
    HOUSEHOLD_WEEKLY_PLAN_FIXTURES,
)
from app.services.v2.story_package_service import StoryPackageService


@dataclass(frozen=True)
class HouseholdPlanSnapshot:
    package_queue: list[StoryPackageManifestV1]
    weekly_plan: list[CaregiverWeeklyPlanItemV1]


class PlanService(Protocol):
    def get_household_plan(self, household_id: UUID) -> HouseholdPlanSnapshot:
        """Return curated package queue and weekly plan for a household."""


class DemoPlanService:
    def __init__(self, story_package_service: StoryPackageService):
        self.story_package_service = story_package_service

    def get_household_plan(self, household_id: UUID) -> HouseholdPlanSnapshot:
        package_ids = HOUSEHOLD_PACKAGE_QUEUE_IDS.get(
            household_id,
            HOUSEHOLD_PACKAGE_QUEUE_IDS.get(DEMO_HOUSEHOLD_ID, ()),
        )
        weekly_plan_fixtures = HOUSEHOLD_WEEKLY_PLAN_FIXTURES.get(
            household_id,
            HOUSEHOLD_WEEKLY_PLAN_FIXTURES.get(DEMO_HOUSEHOLD_ID, ()),
        )

        return HouseholdPlanSnapshot(
            package_queue=self.story_package_service.list_story_packages(package_ids),
            weekly_plan=[
                CaregiverWeeklyPlanItemV1(
                    day=fixture.day,
                    mode=fixture.mode,
                    package_id=fixture.package_id,
                    objective=fixture.objective,
                )
                for fixture in weekly_plan_fixtures
            ],
        )
