from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import redis
from datetime import datetime

from config import config
from orchestrator import AIOrchestrator, StoryGenerationRequest, StoryGenerationResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LumosReading AI Service",
    description="AI专家Agent系统 - 儿童故事生成和质量控制",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化AI编排器
orchestrator = AIOrchestrator()

@app.get("/")
def read_root():
    return {"message": "LumosReading AI Service", "status": "running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "lumosreading-ai-service",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/generate-story", response_model=StoryGenerationResponse)
async def generate_story(request: StoryGenerationRequest):
    """
    生成儿童故事
    """
    try:
        logger.info(f"Received story generation request: {request.theme}")
        
        # 验证请求
        if not request.child_profile:
            raise HTTPException(status_code=400, detail="Child profile is required")
        
        if not request.theme:
            raise HTTPException(status_code=400, detail="Theme is required")
        
        # 生成故事
        response = await orchestrator.generate_story(request)
        
        # 缓存结果
        await cache_story_response(response)
        
        logger.info(f"Story generated successfully: {response.story_id}")
        return response
        
    except Exception as e:
        logger.error(f"Story generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

@app.get("/story-status/{story_id}", response_model=StoryGenerationResponse)
async def get_story_status(story_id: str):
    """
    获取故事生成状态
    """
    try:
        status = await orchestrator.get_generation_status(story_id)
        if not status:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get story status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get story status: {str(e)}")

@app.get("/cost-summary")
async def get_cost_summary(days: int = 7):
    """
    获取AI服务成本摘要
    """
    try:
        summary = await orchestrator.get_cost_summary(days)
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get cost summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost summary: {str(e)}")

@app.post("/psychology/framework")
async def generate_psychology_framework(
    child_profile: Dict[str, Any],
    story_request: Dict[str, Any]
):
    """
    生成心理学教育框架
    """
    try:
        framework = await orchestrator.psychology_expert.generate_educational_framework(
            child_profile, story_request
        )
        return framework.dict()
        
    except Exception as e:
        logger.error(f"Psychology framework generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Psychology framework generation failed: {str(e)}")

@app.post("/literature/create")
async def create_story_content(
    framework: Dict[str, Any],
    theme: str,
    series_bible: Optional[Dict[str, Any]] = None,
    user_preferences: Optional[Dict[str, Any]] = None
):
    """
    创作故事内容
    """
    try:
        from agents.psychology.expert import EducationalFramework
        from agents.story_creation.expert import StoryContent
        
        # 转换framework为EducationalFramework对象
        edu_framework = EducationalFramework(**framework)
        
        story_content = await orchestrator.literature_expert.create_story_content(
            edu_framework, theme, series_bible, user_preferences
        )
        
        return story_content.dict()
        
    except Exception as e:
        logger.error(f"Story content creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Story content creation failed: {str(e)}")

@app.post("/quality/check")
async def quality_check(
    story_content: Dict[str, Any],
    framework: Dict[str, Any],
    child_profile: Dict[str, Any]
):
    """
    质量检查
    """
    try:
        from agents.psychology.expert import EducationalFramework
        from agents.story_creation.expert import StoryContent
        
        # 转换对象
        edu_framework = EducationalFramework(**framework)
        story = StoryContent(**story_content)
        
        quality_report = await orchestrator.quality_controller.comprehensive_quality_check(
            story, edu_framework, child_profile
        )
        
        return quality_report.dict()
        
    except Exception as e:
        logger.error(f"Quality check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quality check failed: {str(e)}")

async def cache_story_response(response: StoryGenerationResponse):
    """缓存故事响应"""
    try:
        redis_client = redis.Redis.from_url(config.redis_url)
        cache_key = f"story_response:{response.story_id}"
        cache_data = response.dict()
        
        # 缓存1小时
        await redis_client.setex(
            cache_key, 
            3600, 
            json.dumps(cache_data, default=str)
        )
        
    except Exception as e:
        logger.warning(f"Failed to cache story response: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
