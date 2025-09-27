"""
安全中间件
处理安全相关的请求和响应
"""

import time
import hashlib
import hmac
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """安全中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # 安全检查
        try:
            # 1. 检查请求大小
            await self._check_request_size(request)
            
            # 2. 检查恶意请求模式
            await self._check_malicious_patterns(request)
            
            # 3. 添加安全头
            response = await self._add_security_headers(request)
            
            if response:
                await response(scope, receive, send)
                return
                
        except HTTPException as e:
            response = JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _check_request_size(self, request: Request):
        """检查请求大小"""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=413, detail="Request too large")
    
    async def _check_malicious_patterns(self, request: Request):
        """检查恶意请求模式"""
        # 检查SQL注入模式
        sql_patterns = [
            "union select", "drop table", "delete from", 
            "insert into", "update set", "exec(", "script>"
        ]
        
        query_string = str(request.url.query).lower()
        for pattern in sql_patterns:
            if pattern in query_string:
                logger.warning(f"Potential SQL injection detected: {request.url}")
                raise HTTPException(status_code=400, detail="Invalid request")
        
        # 检查XSS模式
        xss_patterns = ["<script", "javascript:", "onload=", "onerror="]
        for pattern in xss_patterns:
            if pattern in query_string:
                logger.warning(f"Potential XSS detected: {request.url}")
                raise HTTPException(status_code=400, detail="Invalid request")
    
    async def _add_security_headers(self, request: Request) -> Response:
        """添加安全头"""
        # 这里可以添加安全头，但通常由CORS中间件处理
        return None
