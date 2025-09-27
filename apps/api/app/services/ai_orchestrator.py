"""
AI编排器服务
与AI服务通信的封装
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """AI编排器"""
    
    def __init__(self):
        self.ai_service_url = settings.ai_service_url
        self.timeout = settings.ai_service_timeout
        self.client = None
    
    async def initialize(self):
        """初始化AI服务连接"""
        self.client = httpx.AsyncClient(
            base_url=self.ai_service_url,
            timeout=self.timeout
        )
        logger.info("AI Orchestrator initialized")
    
    async def cleanup(self):
        """清理资源"""
        if self.client:
            await self.client.aclose()
        logger.info("AI Orchestrator cleaned up")
    
    async def generate_educational_framework(
        self, 
        child_profile: Dict[str, Any], 
        story_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成教育心理学框架"""
        try:
            response = await self.client.post(
                "/psychology/framework",
                json={
                    "child_profile": child_profile,
                    "story_request": story_request
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to generate educational framework: {str(e)}")
            raise
    
    async def generate_story_content(
        self,
        framework: Dict[str, Any],
        theme: str,
        series_bible: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成故事内容"""
        try:
            response = await self.client.post(
                "/literature/create",
                json={
                    "framework": framework,
                    "theme": theme,
                    "series_bible": series_bible,
                    "user_preferences": user_preferences
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to generate story content: {str(e)}")
            raise
    
    async def conduct_quality_control(
        self,
        story_content: Dict[str, Any],
        framework: Dict[str, Any]
    ) -> Dict[str, Any]:
        """进行质量控制"""
        try:
            response = await self.client.post(
                "/quality/check",
                json={
                    "story_content": story_content,
                    "framework": framework
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to conduct quality control: {str(e)}")
            raise
    
    async def analyze_rhythm(
        self,
        story_text: str,
        target_age: str
    ) -> Dict[str, Any]:
        """分析韵律"""
        try:
            response = await self.client.post(
                "/literature/rhythm-analysis",
                json={
                    "story_text": story_text,
                    "target_age": target_age
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to analyze rhythm: {str(e)}")
            raise
    
    async def generate_story_with_fallback(
        self,
        child_profile: Dict[str, Any],
        story_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成故事（带优雅降级）"""
        try:
            # 尝试AI生成
            response = await self.client.post(
                "/story/generate",
                json={
                    "child_profile": child_profile,
                    "theme": story_request.get("theme", "友谊"),
                    "series_bible_id": story_request.get("series_bible_id"),
                    "user_preferences": story_request.get("user_preferences")
                }
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.warning(f"AI generation failed, using fallback: {str(e)}")
            # 返回模板故事
            return await self._get_fallback_story(story_request)
    
    async def _get_fallback_story(self, story_request: Dict[str, Any]) -> Dict[str, Any]:
        """获取后备故事"""
        theme = story_request.get("theme", "友谊")
        
        # 返回预定义的模板故事
        return {
            "title": f"关于{theme}的故事",
            "content": {
                "pages": [
                    {
                        "page_number": 1,
                        "text": f"从前有一个小朋友，他非常喜欢{theme}。",
                        "illustration_prompt": f"一个快乐的小朋友在{theme}的场景中",
                        "reading_time_seconds": 30
                    },
                    {
                        "page_number": 2,
                        "text": f"有一天，他遇到了一个关于{theme}的挑战。",
                        "illustration_prompt": f"小朋友面对{theme}挑战的场景",
                        "reading_time_seconds": 30
                    },
                    {
                        "page_number": 3,
                        "text": f"通过努力和智慧，他学会了{theme}的真谛。",
                        "illustration_prompt": f"小朋友学会{theme}的温馨场景",
                        "reading_time_seconds": 30
                    }
                ]
            },
            "generation_type": "template",
            "quality_score": 0.7,
            "fallback_reason": "AI service unavailable"
        }
