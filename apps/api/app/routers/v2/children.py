from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.v2.child_home import ChildHomeV1
from app.services.v2.child_home_service import ChildHomeService
from app.services.v2.child_service import DemoChildService
from app.services.v2.fixtures import FIXTURE_TIMESTAMP
from app.services.v2.plan_service import DemoPlanService
from app.services.v2.story_package_release_service import create_release_story_package_services

router = APIRouter()
story_package_service, _release_service = create_release_story_package_services(
    clock=lambda: FIXTURE_TIMESTAMP,
)
child_service = DemoChildService()
plan_service = DemoPlanService(story_package_service)
child_home_service = ChildHomeService(
    child_service=child_service,
    plan_service=plan_service,
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
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
