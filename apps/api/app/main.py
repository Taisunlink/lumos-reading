from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import time
import uvicorn
import os

from app.core.database import engine, Base
from app.core.config import settings
from app.routers import users, children, stories, auth, illustrations
from app.middleware.security import SecurityMiddleware
from app.middleware.rate_limiting import RateLimitMiddleware

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting LumosReading API Server...")

    # 创建数据库表（同步方式）
    Base.metadata.create_all(bind=engine)

    # 初始化AI服务连接
    from app.services.ai_orchestrator import AIOrchestrator
    ai_orchestrator = AIOrchestrator()
    await ai_orchestrator.initialize()

    logger.info("API Server started successfully")

    yield

    # 关闭时
    logger.info("Shutting down API Server...")
    await ai_orchestrator.cleanup()

# 创建FastAPI应用
app = FastAPI(
    title="LumosReading API",
    description="AI-Powered Children's Reading Platform with Neurodiversity Support",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# 安全中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 自定义中间件
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 记录请求
    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    # 记录响应时间
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")

    return response

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time()
        }
    )

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "lumosreading-api",
        "version": "1.0.0",
        "timestamp": time.time()
    }

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(children.router, prefix="/api/v1/children", tags=["children"])
app.include_router(stories.router, prefix="/api/v1/stories", tags=["stories"])
app.include_router(illustrations.router, prefix="/api/v1/illustrations", tags=["illustrations"])

# 静态文件服务
static_dir = "/tmp/claude/illustrations"
if os.path.exists(static_dir):
    app.mount("/api/static/illustrations", StaticFiles(directory=static_dir), name="illustrations")

# 根端点
@app.get("/")
async def root():
    return {
        "message": "LumosReading API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )