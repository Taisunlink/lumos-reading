from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HouseholdEntitlementPackageV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: UUID
    title: str = Field(min_length=1)
    language_mode: str = Field(min_length=1)
    age_band: str = Field(min_length=1)
    release_channel: Literal["general", "pilot", "experimental", "internal"]
    access_state: Literal["entitled", "locked"]
    entitlement_source: Literal["trial", "subscription", "editorial_free", "grace_period"]
    reason: str = Field(min_length=1)


class HouseholdEntitlementV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["household-entitlement.v1"] = "household-entitlement.v1"
    household_id: UUID
    subscription_status: Literal["trial_active", "active", "grace_period", "expired", "canceled"]
    access_state: Literal["trial", "paid", "grace", "expired"]
    plan_name: str = Field(min_length=1)
    billing_interval: Literal["monthly", "annual", "none"]
    trial_ends_at: Optional[datetime] = None
    renews_at: Optional[datetime] = None
    package_access: List[HouseholdEntitlementPackageV1] = Field(default_factory=list)
    entitled_package_count: int = Field(ge=0)
    locked_package_count: int = Field(ge=0)
    generated_at: datetime


class WeeklyValueHighlightV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    title: str = Field(min_length=1)
    detail: str = Field(min_length=1)


class WeeklyValueReportV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["weekly-value-report.v1"] = "weekly-value-report.v1"
    household_id: UUID
    period_start: datetime
    period_end: datetime
    completed_sessions: int = Field(ge=0)
    total_reading_minutes: int = Field(ge=0)
    distinct_packages_completed: int = Field(ge=0)
    reread_sessions: int = Field(ge=0)
    caregiver_prompt_completions: int = Field(ge=0)
    value_score: int = Field(ge=0, le=100)
    highlights: List[WeeklyValueHighlightV1] = Field(default_factory=list)
    generated_at: datetime


class OpsMetricsSnapshotV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["ops-metrics-snapshot.v1"] = "ops-metrics-snapshot.v1"
    generated_at: datetime
    households_in_scope: int = Field(ge=0)
    households_in_trial: int = Field(ge=0)
    households_with_paid_access: int = Field(ge=0)
    entitled_package_deliveries: int = Field(ge=0)
    blocked_package_requests: int = Field(ge=0)
    completed_sessions: int = Field(ge=0)
    reuse_signals: int = Field(ge=0)
    average_weekly_value_score: float = Field(ge=0, le=100)
