from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class SeriesBibleBase(BaseModel):
    title: str
    description: Optional[str] = None
    characters: List[Dict[str, Any]] = []
    world_settings: Dict[str, Any] = {}
    narrative_rules: Dict[str, Any] = {}
    visual_style: Dict[str, Any] = {}
    lora_models: Dict[str, Any] = {}
    visual_assets: List[Dict[str, Any]] = []
    is_active: bool = True

class SeriesBibleCreate(SeriesBibleBase):
    user_id: UUID

class SeriesBibleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    characters: Optional[List[Dict[str, Any]]] = None
    world_settings: Optional[Dict[str, Any]] = None
    narrative_rules: Optional[Dict[str, Any]] = None
    visual_style: Optional[Dict[str, Any]] = None
    lora_models: Optional[Dict[str, Any]] = None
    visual_assets: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

class SeriesBibleResponse(SeriesBibleBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
