from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class ReadingSessionBase(BaseModel):
    progress: float = 0.0
    interaction_responses: List[Dict[str, Any]] = []
    duration: Optional[int] = None
    device_info: Dict[str, Any] = {}
    vocabulary_learned: List[Dict[str, Any]] = []
    comprehension_score: Optional[float] = None
    engagement_metrics: Dict[str, Any] = {}

class ReadingSessionCreate(ReadingSessionBase):
    story_id: UUID
    child_id: UUID

class ReadingSessionResponse(ReadingSessionBase):
    id: UUID
    story_id: UUID
    child_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
