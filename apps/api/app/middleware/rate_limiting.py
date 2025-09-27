"""
限流中间件
基于Redis的分布式限流
"""

import time
import json
from typing import Callable, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import redis
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """限流中间件"""
    
    def __init__(self, app):
        self.app = app
        self.redis_client = redis.from_url(settings.redis_url)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # 获取客户端标识
        client_id = self._get_client_id(request)
        
        # 检查限流
        if not await self._check_rate_limit(client_id):
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": settings.rate_limit_window
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用用户ID（如果已认证）
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # 使用IP地址
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """检查限流"""
        try:
            current_time = int(time.time())
            window_start = current_time - settings.rate_limit_window
            
            # 使用Redis的滑动窗口算法
            pipe = self.redis_client.pipeline()
            
            # 移除过期的记录
            pipe.zremrangebyscore(f"rate_limit:{client_id}", 0, window_start)
            
            # 获取当前窗口内的请求数
            pipe.zcard(f"rate_limit:{client_id}")
            
            # 添加当前请求
            pipe.zadd(f"rate_limit:{client_id}", {str(current_time): current_time})
            
            # 设置过期时间
            pipe.expire(f"rate_limit:{client_id}", settings.rate_limit_window)
            
            results = pipe.execute()
            current_requests = results[1]
            
            return current_requests < settings.rate_limit_requests
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            # 发生错误时允许请求通过
            return True

def rate_limit(requests: int, per_minutes: int):
    """装饰器：端点级限流"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里可以实现更细粒度的限流
            # 暂时直接调用原函数
            return await func(*args, **kwargs)
        return wrapper
    return decorator
