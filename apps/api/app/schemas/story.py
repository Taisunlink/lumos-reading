from pydantic import BaseModel, Field
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

class StoryPage(BaseModel):
    """故事页面"""
    page_number: int
    text: str
    illustration_prompt: str
    crowd_prompt: Optional[Dict[str, str]] = None
    reading_time_seconds: int = 30
    word_count: int = 0

class StoryRequest(BaseModel):
    """故事生成请求"""
    child_id: str
    theme: str
    series_bible_id: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None
    generation_type: GenerationType = GenerationType.REALTIME

class StoryGenerationResponse(BaseModel):
    """故事生成响应"""
    story_id: str
    status: StoryStatus
    estimated_time_minutes: Optional[int] = None
    message: str

class StoryGenerationStatus(BaseModel):
    """故事生成状态"""
    status: str
    progress_percentage: Optional[float] = None
    estimated_remaining_seconds: Optional[int] = None
    story_id: Optional[str] = None
    title: Optional[str] = None
    quality_score: Optional[float] = None
    error_message: Optional[str] = None

class ProgressiveGenerationRequest(BaseModel):
    """渐进式生成请求"""
    child_id: str
    theme: str
    total_pages: int = 8
    series_bible_id: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None

class ProgressiveGenerationResponse(BaseModel):
    """渐进式生成响应"""
    story_id: str
    status: StoryStatus
    total_pages: int
    generated_pages: int
    websocket_url: str

class StoryDetailResponse(StoryResponse):
    """故事详情响应（继承自StoryResponse）"""
    pass
