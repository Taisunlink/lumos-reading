from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverProgressMetricsV1
from app.schemas.v2.reading import ReadingEventV1
from app.services.v2.fixtures import DEMO_HOUSEHOLD_ID, HOUSEHOLD_READING_EVENT_FIXTURES


@dataclass(frozen=True)
class HouseholdProgressSnapshot:
    recent_events: list[ReadingEventV1]
    progress_metrics: CaregiverProgressMetricsV1


class ProgressService(Protocol):
    def get_household_progress(self, household_id: UUID) -> HouseholdProgressSnapshot:
        """Return recent reading telemetry and caregiver-facing progress metrics."""


class DemoProgressService:
    def get_household_progress(self, household_id: UUID) -> HouseholdProgressSnapshot:
        fixtures = HOUSEHOLD_READING_EVENT_FIXTURES.get(
            household_id,
            HOUSEHOLD_READING_EVENT_FIXTURES.get(DEMO_HOUSEHOLD_ID, ()),
        )
        events = [
            ReadingEventV1(
                event_id=fixture.event_id,
                event_type=fixture.event_type,
                occurred_at=fixture.occurred_at,
                session_id=fixture.session_id,
                child_id=fixture.child_id,
                package_id=fixture.package_id,
                page_index=fixture.page_index,
                platform="ipadOS",
                surface="child-app",
                app_version="2.0.0",
                language_mode="zh-CN",
                payload=fixture.payload,
            )
            for fixture in fixtures
        ]

        return HouseholdProgressSnapshot(
            recent_events=events,
            progress_metrics=CaregiverProgressMetricsV1(
                completed_sessions=sum(1 for event in events if event.event_type == "session_completed"),
                translation_reveals=sum(
                    1 for event in events if event.event_type == "word_revealed_translation"
                ),
                audio_replays=sum(1 for event in events if event.event_type == "page_replayed_audio"),
            ),
        )
