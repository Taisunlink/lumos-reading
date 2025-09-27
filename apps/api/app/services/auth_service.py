"""
认证服务
处理用户认证相关的业务逻辑
"""

import hashlib
import secrets
import random
import logging
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import redis

from app.models.user import User, SubscriptionTier
from app.schemas.auth import UserRegister, WeChatLogin
from app.core.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    """认证服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis.from_url(settings.redis_url)
    
    def user_exists(self, phone: str, email: Optional[str] = None) -> bool:
        """检查用户是否已存在"""
        query = self.db.query(User).filter(User.phone == phone)
        
        if email:
            query = query.union(self.db.query(User).filter(User.email == email))
        
        return query.first() is not None
    
    async def create_user(self, user_data: UserRegister) -> User:
        """创建用户"""
        # 生成密码哈希
        password_hash = self._hash_password(user_data.password)
        
        # 创建用户对象
        user = User(
            phone=user_data.phone,
            email=user_data.email,
            password_hash=password_hash,
            wechat_openid=user_data.wechat_openid,
            subscription_tier=SubscriptionTier.FREE,
            is_active=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User created: {user.phone}")
        return user
    
    async def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        # 查找用户（通过手机号或邮箱）
        user = self.db.query(User).filter(
            (User.phone == identifier) | (User.email == identifier)
        ).first()
        
        if not user or not self._verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def authenticate_wechat_user(self, code: str) -> Optional[User]:
        """验证微信用户"""
        try:
            # 这里应该调用微信API获取用户信息
            # 简化实现，实际需要调用微信接口
            wechat_user_info = await self._get_wechat_user_info(code)
            
            if not wechat_user_info:
                return None
            
            # 查找或创建微信用户
            user = self.db.query(User).filter(
                User.wechat_openid == wechat_user_info.get("openid")
            ).first()
            
            if not user:
                # 创建新用户
                user = User(
                    wechat_openid=wechat_user_info.get("openid"),
                    subscription_tier=SubscriptionTier.FREE,
                    is_active=True
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
            
            return user
            
        except Exception as e:
            logger.error(f"WeChat authentication failed: {str(e)}")
            return None
    
    async def send_verification_code(self, phone: str) -> bool:
        """发送验证码"""
        try:
            # 生成6位验证码
            code = str(random.randint(100000, 999999))
            
            # 存储到Redis，5分钟过期
            key = f"verification_code:{phone}"
            self.redis_client.setex(key, 300, code)
            
            # 这里应该调用短信服务发送验证码
            # 简化实现，实际需要调用短信API
            logger.info(f"Verification code for {phone}: {code}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification code: {str(e)}")
            return False
    
    async def verify_code(self, phone: str, code: str) -> bool:
        """验证验证码"""
        try:
            key = f"verification_code:{phone}"
            stored_code = self.redis_client.get(key)
            
            if not stored_code:
                return False
            
            return stored_code.decode() == code
            
        except Exception as e:
            logger.error(f"Failed to verify code: {str(e)}")
            return False
    
    async def reset_password(self, phone: str, new_password: str) -> bool:
        """重置密码"""
        try:
            user = self.db.query(User).filter(User.phone == phone).first()
            
            if not user:
                return False
            
            # 更新密码
            user.password_hash = self._hash_password(new_password)
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # 删除验证码
            key = f"verification_code:{phone}"
            self.redis_client.delete(key)
            
            logger.info(f"Password reset for user: {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset password: {str(e)}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{pwd_hash.hex()}"
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            salt, hash_hex = hashed_password.split(':')
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return pwd_hash.hex() == hash_hex
        except ValueError:
            return False
    
    async def _get_wechat_user_info(self, code: str) -> Optional[dict]:
        """获取微信用户信息（简化实现）"""
        # 实际实现需要调用微信API
        # 这里返回模拟数据
        return {
            "openid": f"wx_{code}",
            "nickname": "微信用户",
            "headimgurl": ""
        }
