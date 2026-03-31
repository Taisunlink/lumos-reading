from uuid import UUID

from app.schemas.v2.reading import ReadingEventV1

INGESTED_READING_EVENTS_BY_HOUSEHOLD: dict[UUID, dict[UUID, ReadingEventV1]] = {}


def append_ingested_reading_events(
    household_id: UUID,
    events: list[ReadingEventV1],
) -> None:
    household_events = INGESTED_READING_EVENTS_BY_HOUSEHOLD.setdefault(
        household_id,
        {},
    )

    for event in events:
        household_events[event.event_id] = event


def list_ingested_reading_events(household_id: UUID) -> list[ReadingEventV1]:
    return list(
        INGESTED_READING_EVENTS_BY_HOUSEHOLD.get(
            household_id,
            {},
        ).values()
    )


def reset_ingested_reading_events() -> None:
    INGESTED_READING_EVENTS_BY_HOUSEHOLD.clear()
