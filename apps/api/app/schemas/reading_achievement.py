from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ReadingAchievementResponse(BaseModel):
    id: UUID
    child_id: UUID
    achievement_type: str
    achievement_value: int
    achieved_at: datetime
    reward_claimed: bool
    achievement_metadata: Dict[str, Any]

    class Config:
        from_attributes = True
