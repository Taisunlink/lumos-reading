from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter

from app.schemas.v2.reading import (
    ReadingEventBatchRequest,
    ReadingEventIngestedResponse,
    ReadingSessionCreateV2,
    ReadingSessionResponseV2,
)
from app.services.v2.child_service import DemoChildService
from app.services.v2.reading_event_store import append_ingested_reading_events

router = APIRouter()
child_service = DemoChildService()


@router.post("/reading-sessions", response_model=ReadingSessionResponseV2)
async def create_reading_session(
    request: ReadingSessionCreateV2,
) -> ReadingSessionResponseV2:
    """Accept a V2 reading session payload and return a session receipt."""
    return ReadingSessionResponseV2(
        session_id=uuid4(),
        status="accepted",
        accepted_at=datetime.now(timezone.utc),
        child_id=request.child_id,
        package_id=request.package_id,
    )


@router.post("/reading-events:batch", response_model=ReadingEventIngestedResponse)
async def ingest_reading_events(
    request: ReadingEventBatchRequest,
) -> ReadingEventIngestedResponse:
    """Accept a V2 batch of reading events for downstream analytics ingestion."""
    events_by_household = defaultdict(list)

    for event in request.events:
        assignment = child_service.get_child_assignment(event.child_id)

        if assignment is None:
            continue

        events_by_household[assignment.household_id].append(event)

    for household_id, events in events_by_household.items():
        append_ingested_reading_events(household_id, events)

    session_ids = sorted({event.session_id for event in request.events}, key=str)
    return ReadingEventIngestedResponse(
        status="accepted",
        accepted_count=len(request.events),
        accepted_at=datetime.now(timezone.utc),
        session_ids=session_ids,
    )
