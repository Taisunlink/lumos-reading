from datetime import datetime
from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.v2.reading import ReadingEventV1
from app.schemas.v2.story_package import StoryPackageManifestV1


class CaregiverChildSummaryV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    child_id: UUID
    name: str
    age_label: str
    focus: str
    weekly_goal: str
    current_package_id: UUID


class CaregiverWeeklyPlanItemV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: str
    mode: str
    package_id: UUID
    objective: str


class CaregiverProgressMetricsV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    completed_sessions: int = Field(ge=0)
    translation_reveals: int = Field(ge=0)
    audio_replays: int = Field(ge=0)


class CaregiverDashboardV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["caregiver-dashboard.v1"] = "caregiver-dashboard.v1"
    household_id: UUID
    household_name: str
    featured_package_id: UUID
    package_queue: List[StoryPackageManifestV1]
    recent_events: List[ReadingEventV1]
    children: List[CaregiverChildSummaryV1]
    weekly_plan: List[CaregiverWeeklyPlanItemV1]
    progress_metrics: CaregiverProgressMetricsV1
    generated_at: datetime
