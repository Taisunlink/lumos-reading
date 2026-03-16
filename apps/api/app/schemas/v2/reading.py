from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReadingSessionCreateV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    child_id: UUID
    package_id: UUID
    started_at: datetime
    mode: str
    language_mode: str
    assist_mode: List[str] = Field(default_factory=list)


class ReadingSessionResponseV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: UUID
    status: Literal["accepted"]
    accepted_at: datetime
    child_id: UUID
    package_id: UUID


class ReadingEventV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["reading-event.v1"] = "reading-event.v1"
    event_id: UUID
    event_type: Literal[
        "session_started",
        "session_completed",
        "page_viewed",
        "page_replayed_audio",
        "word_revealed_translation",
        "caregiver_prompt_opened",
        "caregiver_prompt_completed",
        "mode_changed",
        "assist_mode_enabled",
        "content_reported",
    ]
    occurred_at: datetime
    session_id: UUID
    child_id: UUID
    package_id: UUID
    page_index: Optional[int] = Field(default=None, ge=0)
    platform: Literal["ipadOS", "ios", "android", "web", "desktop-web", "unknown"]
    surface: Literal["child-app", "caregiver-web", "studio-web"]
    app_version: str
    language_mode: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class ReadingEventBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: List[ReadingEventV1] = Field(min_length=1)


class ReadingEventIngestedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["accepted"]
    accepted_count: int = Field(ge=0)
    accepted_at: datetime
    session_ids: List[UUID] = Field(default_factory=list)
