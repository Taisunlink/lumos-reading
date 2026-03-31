from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .safety_audit import SafetyAuditV1
from .story_package import StoryPackageManifestV1


class StoryPackageBuildCommandV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-build-command.v1"] = "story-package-build-command.v1"
    build_reason: str = Field(min_length=1)
    requested_by: str = Field(min_length=1)
    requested_at: datetime


class StoryPackageReleaseCommandV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-release-command.v1"] = "story-package-release-command.v1"
    build_id: UUID
    release_channel: Literal["general", "pilot", "experimental", "internal"]
    requested_by: str = Field(min_length=1)
    requested_at: datetime
    notes: Optional[str] = None


class StoryPackageRecallCommandV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-recall-command.v1"] = "story-package-recall-command.v1"
    release_id: UUID
    requested_by: str = Field(min_length=1)
    requested_at: datetime
    reason: Optional[str] = None


class StoryPackageRollbackCommandV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-rollback-command.v1"] = "story-package-rollback-command.v1"
    target_release_id: UUID
    requested_by: str = Field(min_length=1)
    requested_at: datetime
    reason: Optional[str] = None


class StoryPackageReviewCommandV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-review-command.v1"] = "story-package-review-command.v1"
    audit_status: Literal[
        "pending",
        "in_review",
        "approved",
        "needs_revision",
        "rejected",
        "recalled",
        "escalated",
    ]
    resolution_action: Literal["none", "revise", "block", "release", "recall", "escalate"]
    reviewer_type: Literal["system", "human", "hybrid"]
    reviewer_id: Optional[str] = None
    notes: Optional[str] = None
    requested_by: str = Field(min_length=1)
    requested_at: datetime


class StoryPackageDraftV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-draft.v1"] = "story-package-draft.v1"
    draft_id: UUID
    package_id: UUID
    source_type: Literal["editorial", "ai_generated"]
    workflow_state: Literal["draft", "built", "released", "recalled"]
    package_preview: StoryPackageManifestV1
    safety_audit: SafetyAuditV1
    operator_notes: List[str] = Field(default_factory=list)
    latest_build_id: Optional[UUID] = None
    active_release_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class StoryPackageDraftIndexV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-draft-index.v1"] = "story-package-draft-index.v1"
    generated_at: datetime
    drafts: List[StoryPackageDraftV1] = Field(default_factory=list)


class StoryPackageBuildV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-build.v1"] = "story-package-build.v1"
    build_id: UUID
    draft_id: UUID
    package_id: UUID
    build_version: int = Field(ge=1)
    status: Literal["queued", "running", "succeeded", "failed"]
    build_reason: str = Field(min_length=1)
    worker_job_id: str = Field(min_length=1)
    manifest_object_key: str = Field(min_length=1)
    artifact_root_object_key: str = Field(min_length=1)
    requested_by: str = Field(min_length=1)
    requested_at: datetime
    completed_at: Optional[datetime] = None
    failure_message: Optional[str] = None
    built_package: StoryPackageManifestV1


class StoryPackageReleaseV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-release.v1"] = "story-package-release.v1"
    release_id: UUID
    package_id: UUID
    draft_id: UUID
    build_id: UUID
    release_version: int = Field(ge=1)
    release_channel: Literal["general", "pilot", "experimental", "internal"]
    status: Literal["active", "recalled", "superseded"]
    runtime_lookup_key: str = Field(min_length=1)
    requested_by: str = Field(min_length=1)
    released_at: datetime
    notes: Optional[str] = None
    recalled_at: Optional[datetime] = None
    rollback_of_release_id: Optional[UUID] = None


class StoryPackageHistoryV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["story-package-history.v1"] = "story-package-history.v1"
    package_id: UUID
    draft: StoryPackageDraftV1
    builds: List[StoryPackageBuildV1] = Field(default_factory=list)
    releases: List[StoryPackageReleaseV1] = Field(default_factory=list)
    active_release_id: Optional[UUID] = None
    generated_at: datetime
