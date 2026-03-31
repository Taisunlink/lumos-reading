from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StoryBriefCommandV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-brief-command.v1"] = "story-brief-command.v1"
    title: str = Field(min_length=1)
    theme: str = Field(min_length=1)
    premise: str = Field(min_length=1)
    language_mode: str = Field(min_length=1)
    age_band: str = Field(min_length=1)
    desired_page_count: int = Field(ge=1, le=10)
    source_outline: Optional[str] = None
    requested_by: str = Field(min_length=1)
    requested_at: datetime


class StoryBriefV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-brief.v1"] = "story-brief.v1"
    brief_id: UUID
    package_id: UUID
    title: str = Field(min_length=1)
    theme: str = Field(min_length=1)
    premise: str = Field(min_length=1)
    language_mode: str = Field(min_length=1)
    age_band: str = Field(min_length=1)
    desired_page_count: int = Field(ge=1, le=10)
    status: Literal["draft_requested", "draft_ready", "media_ready", "failed"]
    source_outline: Optional[str] = None
    latest_job_id: Optional[UUID] = None
    latest_failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class StoryBriefIndexV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-brief-index.v1"] = "story-brief-index.v1"
    generated_at: datetime
    briefs: List[StoryBriefV1] = Field(default_factory=list)


class StoryGenerationJobCommandV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-generation-job-command.v1"] = "story-generation-job-command.v1"
    job_type: Literal["brief_to_draft", "draft_to_media"]
    provider_preference: Optional[Literal["qwen", "vertex", "openai", "placeholder"]] = None
    notes: Optional[str] = None
    requested_by: str = Field(min_length=1)
    requested_at: datetime


class StoryGenerationProviderAttemptV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["qwen", "vertex", "openai", "placeholder"]
    status: Literal["succeeded", "failed", "skipped"]
    reason: Optional[str] = None


class StoryGenerationJobV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-generation-job.v1"] = "story-generation-job.v1"
    job_id: UUID
    brief_id: UUID
    package_id: UUID
    job_type: Literal["brief_to_draft", "draft_to_media"]
    status: Literal["queued", "running", "succeeded", "failed"]
    selected_provider: Optional[Literal["qwen", "vertex", "openai", "placeholder"]] = None
    attempts: List[StoryGenerationProviderAttemptV1] = Field(default_factory=list)
    generated_asset_keys: Optional[List[str]] = None
    requested_by: str = Field(min_length=1)
    requested_at: datetime
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    notes: Optional[str] = None


class StoryGenerationJobIndexV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-generation-job-index.v1"] = "story-generation-job-index.v1"
    generated_at: datetime
    jobs: List[StoryGenerationJobV1] = Field(default_factory=list)
