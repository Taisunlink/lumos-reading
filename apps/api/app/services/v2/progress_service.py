from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.schemas.v2.caregiver import CaregiverProgressMetricsV1
from app.schemas.v2.reading import ReadingEventV1
from app.services.v2.fixtures import (
    DEFAULT_STORY_PACKAGE_FIXTURE,
    DEMO_HOUSEHOLD_ID,
    HOUSEHOLD_READING_EVENT_FIXTURES,
    PACKAGE_FIXTURES,
)
from app.services.v2.reading_event_store import list_ingested_reading_events


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
        events_by_id = {
            event.event_id: event
            for event in [self._build_fixture_event(fixture) for fixture in fixtures]
        }

        for ingested_event in list_ingested_reading_events(household_id):
            events_by_id[ingested_event.event_id] = self._normalize_event(
                ingested_event
            )

        events = sorted(
            events_by_id.values(),
            key=lambda event: event.occurred_at,
            reverse=True,
        )

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

    def _build_fixture_event(self, fixture) -> ReadingEventV1:
        return ReadingEventV1(
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
            language_mode=self._resolve_language_mode(fixture.package_id),
            payload=fixture.payload,
        )

    def _normalize_event(self, event: ReadingEventV1) -> ReadingEventV1:
        return ReadingEventV1(
            event_id=event.event_id,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            session_id=event.session_id,
            child_id=event.child_id,
            package_id=event.package_id,
            page_index=event.page_index,
            platform=event.platform,
            surface=event.surface,
            app_version=event.app_version,
            language_mode=event.language_mode
            or self._resolve_language_mode(event.package_id),
            payload=event.payload,
        )

    def _resolve_language_mode(self, package_id: UUID) -> str:
        return PACKAGE_FIXTURES.get(
            package_id,
            DEFAULT_STORY_PACKAGE_FIXTURE,
        ).language_mode
