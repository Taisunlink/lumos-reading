from uuid import UUID

from fastapi import APIRouter

from app.schemas.v2.caregiver import (
    CaregiverChildrenV1,
    CaregiverDashboardV1,
    CaregiverHouseholdV1,
    CaregiverPlanV1,
    CaregiverProgressV1,
)
from app.services.v2.caregiver_children_read_service import CaregiverChildrenReadService
from app.services.v2.caregiver_dashboard_service import CaregiverDashboardService
from app.services.v2.caregiver_household_read_service import CaregiverHouseholdReadService
from app.services.v2.caregiver_plan_read_service import CaregiverPlanReadService
from app.services.v2.caregiver_progress_read_service import CaregiverProgressReadService
from app.services.v2.child_service import DemoChildService
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.household_service import DemoHouseholdService
from app.services.v2.plan_service import DemoPlanService
from app.services.v2.progress_service import DemoProgressService
from app.services.v2.story_package_service import DemoStoryPackageService

router = APIRouter()
story_package_service = DemoStoryPackageService()
household_service = DemoHouseholdService()
child_service = DemoChildService()
plan_service = DemoPlanService(story_package_service)
progress_service = DemoProgressService()

dashboard_service = CaregiverDashboardService(
    household_service=household_service,
    child_service=child_service,
    plan_service=plan_service,
    progress_service=progress_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)
household_read_service = CaregiverHouseholdReadService(
    household_service=household_service,
    child_service=child_service,
    plan_service=plan_service,
    progress_service=progress_service,
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)
children_read_service = CaregiverChildrenReadService(
    child_service=child_service,
    plan_service=plan_service,
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)
plan_read_service = CaregiverPlanReadService(
    plan_service=plan_service,
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)
progress_read_service = CaregiverProgressReadService(
    progress_service=progress_service,
    child_service=child_service,
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)


@router.get("/households/{household_id}", response_model=CaregiverHouseholdV1)
async def get_caregiver_household(household_id: UUID) -> CaregiverHouseholdV1:
    """Return the V2 caregiver household read model."""
    return household_read_service.get_household(household_id)


@router.get("/households/{household_id}/children", response_model=CaregiverChildrenV1)
async def get_caregiver_children(household_id: UUID) -> CaregiverChildrenV1:
    """Return the V2 caregiver child assignment read model."""
    return children_read_service.get_children(household_id)


@router.get("/households/{household_id}/plan", response_model=CaregiverPlanV1)
async def get_caregiver_plan(household_id: UUID) -> CaregiverPlanV1:
    """Return the V2 caregiver weekly plan read model."""
    return plan_read_service.get_plan(household_id)


@router.get("/households/{household_id}/progress", response_model=CaregiverProgressV1)
async def get_caregiver_progress(household_id: UUID) -> CaregiverProgressV1:
    """Return the V2 caregiver progress read model."""
    return progress_read_service.get_progress(household_id)


@router.get("/households/{household_id}/dashboard", response_model=CaregiverDashboardV1)
async def get_caregiver_dashboard(household_id: UUID) -> CaregiverDashboardV1:
    """Return the V2 caregiver household dashboard aggregate."""
    return dashboard_service.get_dashboard(household_id)
