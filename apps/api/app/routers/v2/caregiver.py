from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.v2.caregiver import (
    CaregiverAssignmentCommandV1,
    CaregiverAssignmentResponseV1,
    CaregiverChildrenV1,
    CaregiverDashboardV1,
    CaregiverHouseholdV1,
    CaregiverPlanV1,
    CaregiverProgressV1,
)
from app.services.v2.caregiver_assignment_service import (
    CaregiverAssignmentNotFoundError,
    CaregiverAssignmentService,
    CaregiverAssignmentValidationError,
)
from app.services.v2.caregiver_children_read_service import CaregiverChildrenReadService
from app.services.v2.caregiver_dashboard_service import CaregiverDashboardService
from app.services.v2.caregiver_household_read_service import CaregiverHouseholdReadService
from app.services.v2.caregiver_plan_read_service import CaregiverPlanReadService
from app.services.v2.caregiver_progress_read_service import CaregiverProgressReadService
from app.services.v2.child_service import DemoChildService
from app.services.v2.child_home_service import ChildHomeService
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.household_service import DemoHouseholdService
from app.services.v2.plan_service import DemoPlanService
from app.services.v2.progress_service import DemoProgressService
from app.services.v2.story_package_release_service import create_release_story_package_services

router = APIRouter()
story_package_service, _release_service = create_release_story_package_services(
    clock=lambda: FIXTURE_TIMESTAMP,
)
household_service = DemoHouseholdService()
child_service = DemoChildService()
plan_service = DemoPlanService(story_package_service)
progress_service = DemoProgressService()
child_home_service = ChildHomeService(
    child_service=child_service,
    plan_service=plan_service,
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)

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
assignment_service = CaregiverAssignmentService(
    child_service=child_service,
    child_home_service=child_home_service,
    plan_service=plan_service,
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)


@router.get(
    "/households/{household_id}",
    response_model=CaregiverHouseholdV1,
    response_model_exclude_none=True,
)
async def get_caregiver_household(household_id: UUID) -> CaregiverHouseholdV1:
    """Return the V2 caregiver household read model."""
    return household_read_service.get_household(household_id)


@router.get(
    "/households/{household_id}/children",
    response_model=CaregiverChildrenV1,
    response_model_exclude_none=True,
)
async def get_caregiver_children(household_id: UUID) -> CaregiverChildrenV1:
    """Return the V2 caregiver child assignment read model."""
    return children_read_service.get_children(household_id)


@router.post(
    "/households/{household_id}/children/{child_id}/assignment",
    response_model=CaregiverAssignmentResponseV1,
    response_model_exclude_none=True,
)
async def assign_caregiver_package(
    household_id: UUID,
    child_id: UUID,
    command: CaregiverAssignmentCommandV1,
) -> CaregiverAssignmentResponseV1:
    """Update the currently assigned package for a child."""
    if command.household_id != household_id or command.child_id != child_id:
        raise HTTPException(
            status_code=400,
            detail="Path ids must match the caregiver assignment payload.",
        )

    try:
        return assignment_service.assign_package(command)
    except CaregiverAssignmentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CaregiverAssignmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/households/{household_id}/plan",
    response_model=CaregiverPlanV1,
    response_model_exclude_none=True,
)
async def get_caregiver_plan(household_id: UUID) -> CaregiverPlanV1:
    """Return the V2 caregiver weekly plan read model."""
    return plan_read_service.get_plan(household_id)


@router.get(
    "/households/{household_id}/progress",
    response_model=CaregiverProgressV1,
    response_model_exclude_none=True,
)
async def get_caregiver_progress(household_id: UUID) -> CaregiverProgressV1:
    """Return the V2 caregiver progress read model."""
    return progress_read_service.get_progress(household_id)


@router.get(
    "/households/{household_id}/dashboard",
    response_model=CaregiverDashboardV1,
    response_model_exclude_none=True,
)
async def get_caregiver_dashboard(household_id: UUID) -> CaregiverDashboardV1:
    """Return the V2 caregiver household dashboard aggregate."""
    return dashboard_service.get_dashboard(household_id)
