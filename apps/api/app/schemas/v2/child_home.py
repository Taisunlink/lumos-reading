from datetime import datetime
from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.v2.story_package import StoryPackageManifestV1


class ChildHomeV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["child-home.v1"] = "child-home.v1"
    child_id: UUID
    household_id: UUID
    child_name: str
    focus: str
    weekly_goal: str
    featured_package_id: UUID
    current_package_id: UUID
    package_queue: List[StoryPackageManifestV1]
    support_mode_defaults: List[str]
    generated_at: datetime
