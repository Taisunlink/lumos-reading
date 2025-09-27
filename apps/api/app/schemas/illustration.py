from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from app.models.illustration import IllustrationStatus, IllustrationStyle

class IllustrationBase(BaseModel):
    story_id: UUID
    page_number: int
    prompt: str
    negative_prompt: Optional[str] = None
    style: IllustrationStyle = IllustrationStyle.WATERCOLOR
    character_bible: Optional[Dict[str, Any]] = None

class IllustrationCreate(IllustrationBase):
    pass

class IllustrationUpdate(BaseModel):
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    style: Optional[IllustrationStyle] = None
    character_bible: Optional[Dict[str, Any]] = None

class IllustrationResponse(BaseModel):
    id: UUID
    story_id: UUID
    page_number: int
    prompt: str = Field(alias='generation_prompt')  # 映射数据库字段
    negative_prompt: Optional[str] = None
    style: IllustrationStyle
    status: IllustrationStatus
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    local_path: Optional[str] = None
    quality_score: Optional[float] = None
    safety_score: Optional[float] = None
    appropriateness_score: Optional[float] = None
    generation_metadata: Dict[str, Any] = {}
    character_consistency_data: Dict[str, Any] = {}
    safety_info: Dict[str, Any] = {}  # 新增字段
    provider: Optional[str] = None  # 新增字段
    model_name: Optional[str] = None  # 新增字段
    cache_key: Optional[str] = None  # 新增字段
    created_at: datetime
    updated_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True  # 允许使用别名和原字段名

class BatchIllustrationRequest(BaseModel):
    story_id: UUID
    pages: List[Dict[str, Any]]
    character_bible: Optional[Dict[str, Any]] = None
    style: IllustrationStyle = IllustrationStyle.WATERCOLOR

class BatchIllustrationResponse(BaseModel):
    story_id: UUID
    illustrations: List[IllustrationResponse]
    total_pages: int
    successful_generations: int
    failed_generations: int

class IllustrationStatusResponse(BaseModel):
    id: UUID
    status: IllustrationStatus
    progress: int
    image_url: Optional[str] = None
    created_at: datetime
    generated_at: Optional[datetime] = None
