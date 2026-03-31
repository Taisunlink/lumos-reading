from fastapi import APIRouter

from app.schemas.v2.monetization import OpsMetricsSnapshotV1
from app.services.v2.entitlement_service import DemoEntitlementService
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.ops_metrics_service import OpsMetricsService
from app.services.v2.progress_service import DemoProgressService
from app.services.v2.story_package_release_service import create_release_story_package_services
from app.services.v2.weekly_value_service import WeeklyValueService

router = APIRouter()
story_package_service, _release_service = create_release_story_package_services(
    clock=lambda: FIXTURE_TIMESTAMP,
)
entitlement_service = DemoEntitlementService(
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)
progress_service = DemoProgressService()
weekly_value_service = WeeklyValueService(
    progress_service=progress_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)
ops_metrics_service = OpsMetricsService(
    entitlement_service=entitlement_service,
    progress_service=progress_service,
    weekly_value_service=weekly_value_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)


@router.get(
    "/metrics",
    response_model=OpsMetricsSnapshotV1,
    response_model_exclude_none=True,
)
async def get_ops_metrics() -> OpsMetricsSnapshotV1:
    """Return the current demo operations snapshot for Phase 6."""
    return ops_metrics_service.get_snapshot()
