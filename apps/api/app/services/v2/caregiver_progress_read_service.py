from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverProgressEventV1, CaregiverProgressV1
from app.services.v2.child_service import ChildService
from app.services.v2.progress_service import ProgressService
from app.services.v2.story_package_service import StoryPackageService


class CaregiverProgressReadService:
    def __init__(
        self,
        progress_service: ProgressService,
        child_service: ChildService,
        story_package_service: StoryPackageService,
        clock: Callable[[], datetime],
    ):
        self.progress_service = progress_service
        self.child_service = child_service
        self.story_package_service = story_package_service
        self.clock = clock

    def get_progress(self, household_id: UUID) -> CaregiverProgressV1:
        progress = self.progress_service.get_household_progress(household_id)
        child_name_by_id = {
            child.child_id: child.name for child in self.child_service.list_children(household_id)
        }
        package_ids = list(dict.fromkeys(event.package_id for event in progress.recent_events))
        package_title_by_id = {
            story_package.package_id: story_package.title
            for story_package in self.story_package_service.list_story_packages(package_ids)
        }

        return CaregiverProgressV1(
            household_id=household_id,
            recent_events=[
                CaregiverProgressEventV1(
                    event=event,
                    child_name=child_name_by_id.get(event.child_id, str(event.child_id)),
                    package_title=package_title_by_id.get(event.package_id, str(event.package_id)),
                )
                for event in progress.recent_events
            ],
            progress_metrics=progress.progress_metrics,
            generated_at=self.clock(),
        )
