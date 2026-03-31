from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.v2.child_home import ChildHomeV1
from app.schemas.v2.story_package import StoryPackageManifestV1
from app.services.v2.access_errors import NoEntitledPackagesError
from app.services.v2.child_package_delivery_service import (
    ChildPackageDeliveryAccessError,
    ChildPackageDeliveryNotFoundError,
    ChildPackageDeliveryService,
)
from app.services.v2.child_home_service import ChildHomeService
from app.services.v2.child_service import DemoChildService
from app.services.v2.entitlement_service import DemoEntitlementService
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.plan_service import DemoPlanService, EntitlementAwarePlanService
from app.services.v2.story_package_release_service import create_release_story_package_services

router = APIRouter()
story_package_service, _release_service = create_release_story_package_services(
    clock=lambda: FIXTURE_TIMESTAMP,
)
child_service = DemoChildService()
entitlement_service = DemoEntitlementService(
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)
plan_service = EntitlementAwarePlanService(
    base_plan_service=DemoPlanService(story_package_service),
    package_access_policy=entitlement_service,
)
child_home_service = ChildHomeService(
    child_service=child_service,
    plan_service=plan_service,
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)
child_package_delivery_service = ChildPackageDeliveryService(
    child_service=child_service,
    entitlement_service=entitlement_service,
    story_package_service=story_package_service,
    clock=lambda: FIXTURE_TIMESTAMP,
)


@router.get(
    "/{child_id}",
    response_model=ChildHomeV1,
    response_model_exclude_none=True,
)
async def get_child_home(child_id: UUID) -> ChildHomeV1:
    """Return the assigned package shelf for the child runtime."""
    try:
        return child_home_service.get_home(child_id)
    except NoEntitledPackagesError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{child_id}/packages/{package_id}",
    response_model=StoryPackageManifestV1,
    response_model_exclude_none=True,
)
async def get_child_scoped_story_package(
    child_id: UUID,
    package_id: UUID,
) -> StoryPackageManifestV1:
    """Return a runtime package only if the child's household is entitled to it."""
    try:
        return child_package_delivery_service.get_package(child_id, package_id)
    except ChildPackageDeliveryAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ChildPackageDeliveryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
