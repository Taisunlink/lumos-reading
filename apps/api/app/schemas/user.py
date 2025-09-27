from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import SubscriptionTier

class UserBase(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    wechat_openid: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    subscription_tier: Optional[SubscriptionTier] = None

class UserResponse(UserBase):
    id: UUID
    subscription_tier: SubscriptionTier
    subscription_expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
