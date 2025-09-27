from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID
from app.models.child_profile import Gender

class ChildProfileBase(BaseModel):
    name: str
    nickname: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[Gender] = None
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = {}
    neuro_profile: Dict[str, Any] = {}
    developmental_milestones: Dict[str, Any] = {}
    attention_span_baseline: Optional[int] = None
    reading_level: Optional[str] = None

class ChildProfileCreate(ChildProfileBase):
    user_id: UUID

class ChildProfileUpdate(BaseModel):
    name: Optional[str] = None
    nickname: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[Gender] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    neuro_profile: Optional[Dict[str, Any]] = None
    developmental_milestones: Optional[Dict[str, Any]] = None
    attention_span_baseline: Optional[int] = None
    reading_level: Optional[str] = None

class ChildProfileResponse(ChildProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    age_in_months: Optional[int] = None
    cognitive_stage: Optional[str] = None

    class Config:
        from_attributes = True
