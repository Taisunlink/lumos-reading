"""
认证相关Schema
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """访问令牌"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[str] = None

class UserLogin(BaseModel):
    """用户登录"""
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

class UserRegister(BaseModel):
    """用户注册"""
    phone: str
    password: str
    email: Optional[EmailStr] = None
    wechat_openid: Optional[str] = None

class WeChatLogin(BaseModel):
    """微信登录"""
    code: str
    encrypted_data: Optional[str] = None
    iv: Optional[str] = None

class PasswordReset(BaseModel):
    """密码重置"""
    phone: str
    new_password: str
    verification_code: str

class VerificationCode(BaseModel):
    """验证码"""
    phone: str
    code: str
