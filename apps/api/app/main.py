import importlib
import logging
import os
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.security import SecurityMiddleware
from app.routers.v2 import caregiver as v2_caregiver
from app.routers.v2 import children as v2_children
from app.routers.v2 import reading as v2_reading
from app.routers.v2 import story_briefs as v2_story_briefs
from app.routers.v2 import story_packages as v2_story_packages


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format,
)
logger = logging.getLogger(__name__)


def include_optional_router(
    app: FastAPI,
    module_path: str,
    prefix: str,
    tags: list[str],
) -> None:
    """Register legacy routers on a best-effort basis during the V2 migration."""
    try:
        module = importlib.import_module(module_path)
        router = getattr(module, "router")
        app.include_router(router, prefix=prefix, tags=tags)
        logger.info("Registered router %s at %s", module_path, prefix)
    except Exception as exc:  # pragma: no cover
        logger.warning("Skipped router %s: %s", module_path, exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("Starting LumosReading API server")

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:  # pragma: no cover
        logger.warning("Skipped metadata initialization: %s", exc)

    ai_orchestrator = None
    try:
        from app.services.ai_orchestrator import AIOrchestrator

        ai_orchestrator = AIOrchestrator()
        await ai_orchestrator.initialize()
        app.state.ai_orchestrator = ai_orchestrator
    except Exception as exc:  # pragma: no cover
        app.state.ai_orchestrator = None
        logger.warning("AI orchestrator unavailable during startup: %s", exc)

    logger.info("API server started")
    yield

    logger.info("Shutting down API server")
    if ai_orchestrator is not None:
        await ai_orchestrator.cleanup()


app = FastAPI(
    title="LumosReading API",
    description="LumosReading V2 API entrypoint with legacy compatibility during migration.",
    version="2.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info("Request: %s %s", request.method, request.url)

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info("Response: %s - %.3fs", response.status_code, process_time)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time(),
        },
    )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "lumosreading-api",
        "version": "2.0.0",
        "timestamp": time.time(),
    }


app.include_router(v2_story_packages.router, prefix="/api/v2/story-packages", tags=["v2-story-packages"])
app.include_router(v2_story_briefs.router, prefix="/api/v2/story-briefs", tags=["v2-story-briefs"])
app.include_router(
    v2_story_briefs.jobs_router,
    prefix="/api/v2/story-generation-jobs",
    tags=["v2-story-generation"],
)
app.include_router(v2_caregiver.router, prefix="/api/v2/caregiver", tags=["v2-caregiver"])
app.include_router(v2_children.router, prefix="/api/v2/child-home", tags=["v2-child-home"])
app.include_router(v2_reading.router, prefix="/api/v2", tags=["v2-reading"])

if settings.enable_legacy_v1_routers:
    include_optional_router(app, "app.routers.auth", "/api/v1/auth", ["authentication"])
    include_optional_router(app, "app.routers.users", "/api/v1/users", ["users"])
    include_optional_router(app, "app.routers.children", "/api/v1/children", ["children"])
    include_optional_router(app, "app.routers.stories", "/api/v1/stories", ["stories"])
    include_optional_router(app, "app.routers.illustrations", "/api/v1/illustrations", ["illustrations"])
else:
    logger.info("Legacy v1 routers are disabled by default during the V2 migration")


static_dir = "/tmp/claude/illustrations"
if os.path.exists(static_dir):
    app.mount("/api/static/illustrations", StaticFiles(directory=static_dir), name="illustrations")


@app.get("/")
async def root():
    return {
        "message": "LumosReading API Server",
        "version": "2.0.0",
        "available_api_versions": ["/api/v2", "/api/v1"],
        "active_docs": [
            "docs/v2/01-strategy-review-and-references.md",
            "docs/v2/02-v2-architecture-and-migration-blueprint.md",
            "packages/contracts/schemas/README.md",
        ],
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
