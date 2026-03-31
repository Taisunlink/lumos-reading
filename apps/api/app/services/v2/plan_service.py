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


class PackageAccessPolicy(Protocol):
    def is_package_entitled(self, household_id: UUID, package_id: UUID) -> bool:
        """Return whether the household can currently access the requested package."""


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


class EntitlementAwarePlanService:
    def __init__(
        self,
        base_plan_service: PlanService,
        package_access_policy: PackageAccessPolicy,
    ):
        self.base_plan_service = base_plan_service
        self.package_access_policy = package_access_policy

    def get_household_plan(self, household_id: UUID) -> HouseholdPlanSnapshot:
        plan = self.base_plan_service.get_household_plan(household_id)
        entitled_queue = [
            story_package
            for story_package in plan.package_queue
            if self.package_access_policy.is_package_entitled(
                household_id,
                story_package.package_id,
            )
        ]
        entitled_package_ids = {
            story_package.package_id for story_package in entitled_queue
        }

        return HouseholdPlanSnapshot(
            package_queue=entitled_queue,
            weekly_plan=[
                CaregiverWeeklyPlanItemV1(
                    day=item.day,
                    mode=item.mode,
                    package_id=item.package_id,
                    objective=item.objective,
                )
                for item in plan.weekly_plan
                if item.package_id in entitled_package_ids
            ],
        )
