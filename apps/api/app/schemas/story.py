from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from app.models.story import GenerationType, StoryStatus

class StoryBase(BaseModel):
    title: str
    theme: Optional[str] = None
    age_group: Optional[str] = None
    content: Dict[str, Any]
    generation_type: Optional[GenerationType] = None
    status: StoryStatus = StoryStatus.GENERATING
    reading_time: Optional[int] = None
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    illustrations: List[Dict[str, Any]] = []
    interaction_points: List[Dict[str, Any]] = []
    quality_score: Optional[float] = None
    safety_score: Optional[float] = None
    educational_value_score: Optional[float] = None
    story_metadata: Dict[str, Any] = {}

class StoryCreate(StoryBase):
    child_id: UUID
    series_bible_id: Optional[UUID] = None

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    theme: Optional[str] = None
    age_group: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    status: Optional[StoryStatus] = None
    reading_time: Optional[int] = None
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    illustrations: Optional[List[Dict[str, Any]]] = None
    interaction_points: Optional[List[Dict[str, Any]]] = None
    quality_score: Optional[float] = None
    safety_score: Optional[float] = None
    educational_value_score: Optional[float] = None
    story_metadata: Optional[Dict[str, Any]] = None

class StoryResponse(StoryBase):
    id: UUID
    child_id: UUID
    series_bible_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
