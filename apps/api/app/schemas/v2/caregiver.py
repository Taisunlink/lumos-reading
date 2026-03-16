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


class CaregiverChildAssignmentV1(CaregiverChildSummaryV1):
    model_config = ConfigDict(extra="forbid")

    current_package: StoryPackageManifestV1


class CaregiverPlannedSessionV1(CaregiverWeeklyPlanItemV1):
    model_config = ConfigDict(extra="forbid")

    package: StoryPackageManifestV1


class CaregiverProgressEventV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: ReadingEventV1
    child_name: str
    package_title: str


class CaregiverHouseholdV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["caregiver-household.v1"] = "caregiver-household.v1"
    household_id: UUID
    household_name: str
    featured_package_id: UUID
    featured_package: StoryPackageManifestV1
    package_queue: List[StoryPackageManifestV1]
    child_count: int = Field(ge=0)
    progress_metrics: CaregiverProgressMetricsV1
    generated_at: datetime


class CaregiverChildrenV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["caregiver-children.v1"] = "caregiver-children.v1"
    household_id: UUID
    children: List[CaregiverChildAssignmentV1]
    planned_session_count: int = Field(ge=0)
    generated_at: datetime


class CaregiverPlanV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["caregiver-plan.v1"] = "caregiver-plan.v1"
    household_id: UUID
    package_queue: List[StoryPackageManifestV1]
    weekly_plan: List[CaregiverPlannedSessionV1]
    generated_at: datetime


class CaregiverProgressV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["caregiver-progress.v1"] = "caregiver-progress.v1"
    household_id: UUID
    recent_events: List[CaregiverProgressEventV1]
    progress_metrics: CaregiverProgressMetricsV1
    generated_at: datetime


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
