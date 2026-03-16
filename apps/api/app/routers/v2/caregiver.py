from uuid import UUID

from fastapi import APIRouter

from app.schemas.v2.caregiver import CaregiverDashboardV1
from app.services.v2.caregiver_dashboard_service import CaregiverDashboardService
from app.services.v2.child_service import DemoChildService
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.household_service import DemoHouseholdService
from app.services.v2.plan_service import DemoPlanService
from app.services.v2.progress_service import DemoProgressService
from app.services.v2.story_package_service import DemoStoryPackageService

router = APIRouter()
story_package_service = DemoStoryPackageService()
dashboard_service = CaregiverDashboardService(
    household_service=DemoHouseholdService(),
    child_service=DemoChildService(),
    plan_service=DemoPlanService(story_package_service),
    progress_service=DemoProgressService(),
    clock=lambda: FIXTURE_TIMESTAMP,
)


@router.get("/households/{household_id}/dashboard", response_model=CaregiverDashboardV1)
async def get_caregiver_dashboard(household_id: UUID) -> CaregiverDashboardV1:
    """Return the V2 caregiver household dashboard aggregate."""
    return dashboard_service.get_dashboard(household_id)
