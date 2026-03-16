from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SafetyAuditFindingV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    title: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    page_index: Optional[int] = Field(default=None, ge=0)
    action_required: bool


class SafetyAuditReviewerV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer_type: Literal["system", "human", "hybrid"]
    reviewer_id: Optional[str] = None


class SafetyAuditResolutionV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["none", "revise", "block", "release", "recall", "escalate"]
    notes: Optional[str] = None
    resolved_at: Optional[datetime] = None


class SafetyAuditV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["safety-audit.v1"] = "safety-audit.v1"
    audit_id: UUID
    target_type: Literal["story_master", "story_variant", "story_package", "user_report"]
    target_id: UUID
    audit_source: Literal["pre_release", "post_release_report", "scheduled_review", "incident_response"]
    audit_status: Literal[
        "pending",
        "in_review",
        "approved",
        "needs_revision",
        "rejected",
        "recalled",
        "escalated",
    ]
    severity: Literal["low", "medium", "high", "critical"]
    policy_version: str
    findings: List[SafetyAuditFindingV1] = Field(default_factory=list)
    reviewer: SafetyAuditReviewerV1
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    resolution: SafetyAuditResolutionV1
