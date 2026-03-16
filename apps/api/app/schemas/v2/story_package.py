from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StoryPackageSafetyV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_status: Literal["approved", "limited_release", "recalled"]
    reviewed_at: Optional[datetime] = None
    review_policy_version: Optional[str] = None


class StoryPackageTextRunV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    lang: str
    tts_timing: List[int] = Field(default_factory=list)


class StoryPackageMediaV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class StoryPackageOverlayV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vocabulary: List[str] = Field(default_factory=list)
    caregiver_prompt_ids: List[str] = Field(default_factory=list)
    interaction_ids: List[str] = Field(default_factory=list)


class StoryPackagePageV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_index: int = Field(ge=0)
    text_runs: List[StoryPackageTextRunV1]
    media: Optional[StoryPackageMediaV1] = None
    overlays: Optional[StoryPackageOverlayV1] = None


class StoryPackageManifestV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package.v1"] = "story-package.v1"
    package_id: UUID
    story_master_id: UUID
    story_variant_id: UUID
    title: str
    subtitle: Optional[str] = None
    language_mode: str
    difficulty_level: str
    age_band: str
    estimated_duration_sec: int = Field(ge=0)
    release_channel: Literal["general", "pilot", "experimental", "internal"]
    cover_image_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    safety: StoryPackageSafetyV1
    pages: List[StoryPackagePageV1]
