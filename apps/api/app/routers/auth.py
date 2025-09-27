"""
认证路由
用户登录、注册、密码重置等
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.database import get_db
from app.core.config import settings
from app.schemas.auth import (
    Token, UserLogin, UserRegister, WeChatLogin, 
    PasswordReset, VerificationCode
)
from app.models.user import User
from app.dependencies.auth import create_access_token, verify_token
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """用户注册"""
    try:
        auth_service = AuthService(db)
        
        # 检查用户是否已存在
        if auth_service.user_exists(user_data.phone, user_data.email):
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )
        
        # 创建用户
        user = await auth_service.create_user(user_data)
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录"""
    try:
        auth_service = AuthService(db)
        
        # 验证用户凭据
        user = await auth_service.authenticate_user(
            user_credentials.phone or user_credentials.email,
            user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User login failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )

@router.post("/wechat-login", response_model=Token)
async def wechat_login(
    wechat_data: WeChatLogin,
    db: Session = Depends(get_db)
):
    """微信登录"""
    try:
        auth_service = AuthService(db)
        
        # 验证微信授权码
        user = await auth_service.authenticate_wechat_user(wechat_data.code)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="WeChat authentication failed"
            )
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WeChat login failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="WeChat login failed"
        )

@router.post("/send-verification-code")
async def send_verification_code(
    phone: str,
    db: Session = Depends(get_db)
):
    """发送验证码"""
    try:
        auth_service = AuthService(db)
        await auth_service.send_verification_code(phone)
        
        return {"message": "Verification code sent successfully"}
        
    except Exception as e:
        logger.error(f"Failed to send verification code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send verification code"
        )

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """重置密码"""
    try:
        auth_service = AuthService(db)
        
        # 验证验证码
        if not await auth_service.verify_code(reset_data.phone, reset_data.verification_code):
            raise HTTPException(
                status_code=400,
                detail="Invalid verification code"
            )
        
        # 重置密码
        await auth_service.reset_password(reset_data.phone, reset_data.new_password)
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Password reset failed"
        )

@router.post("/verify-code")
async def verify_code(
    verification_data: VerificationCode,
    db: Session = Depends(get_db)
):
    """验证验证码"""
    try:
        auth_service = AuthService(db)
        
        is_valid = await auth_service.verify_code(
            verification_data.phone,
            verification_data.code
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid verification code"
            )
        
        return {"message": "Verification code is valid"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Code verification failed"
        )
