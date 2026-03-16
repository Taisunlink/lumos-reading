from uuid import UUID

from fastapi import APIRouter

from app.schemas.v2.caregiver import CaregiverDashboardV1
from app.services.v2_demo_data import get_caregiver_dashboard_fixture

router = APIRouter()


@router.get("/households/{household_id}/dashboard", response_model=CaregiverDashboardV1)
async def get_caregiver_dashboard(household_id: UUID) -> CaregiverDashboardV1:
    """Return the V2 caregiver household dashboard aggregate."""
    return get_caregiver_dashboard_fixture(household_id)
