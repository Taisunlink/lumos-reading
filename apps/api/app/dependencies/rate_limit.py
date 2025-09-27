"""
限流依赖
端点级限流装饰器
"""

from functools import wraps
from typing import Callable
import time
import redis
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis客户端
redis_client = redis.from_url(settings.redis_url)

def rate_limit(requests: int, per_minutes: int):
    """
    限流装饰器
    
    Args:
        requests: 允许的请求数
        per_minutes: 时间窗口（分钟）
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取请求对象
            request = None
            for arg in args:
                if hasattr(arg, 'client') and hasattr(arg, 'headers'):
                    request = arg
                    break
            
            if not request:
                return await func(*args, **kwargs)
            
            # 获取客户端标识
            client_id = _get_client_id(request)
            endpoint = f"{func.__module__}.{func.__name__}"
            key = f"rate_limit:{endpoint}:{client_id}"
            
            # 检查限流
            if not _check_endpoint_rate_limit(key, requests, per_minutes):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {requests} requests per {per_minutes} minutes"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def _get_client_id(request) -> str:
    """获取客户端标识"""
    # 优先使用用户ID
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

def _check_endpoint_rate_limit(key: str, requests: int, per_minutes: int) -> bool:
    """检查端点限流"""
    try:
        current_time = int(time.time())
        window_start = current_time - (per_minutes * 60)
        
        # 使用Redis管道
        pipe = redis_client.pipeline()
        
        # 移除过期记录
        pipe.zremrangebyscore(key, 0, window_start)
        
        # 获取当前请求数
        pipe.zcard(key)
        
        # 添加当前请求
        pipe.zadd(key, {str(current_time): current_time})
        
        # 设置过期时间
        pipe.expire(key, per_minutes * 60)
        
        results = pipe.execute()
        current_requests = results[1]
        
        return current_requests < requests
        
    except Exception as e:
        logger.error(f"Rate limit check failed: {str(e)}")
        # 发生错误时允许请求通过
        return True
