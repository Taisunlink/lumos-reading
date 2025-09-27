"""
故事生成服务
处理故事生成的核心业务逻辑
"""

import uuid
import asyncio
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.story import Story, StoryStatus, GenerationType
from app.models.child_profile import ChildProfile
from app.schemas.story import StoryRequest
from app.services.ai_orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

class StoryGenerationService:
    """故事生成服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_orchestrator = None
    
    async def initialize_ai_orchestrator(self):
        """初始化AI编排器"""
        if not self.ai_orchestrator:
            self.ai_orchestrator = AIOrchestrator()
            await self.ai_orchestrator.initialize()
    
    async def generate_story_async(
        self,
        story_id: uuid.UUID,
        child_profile: ChildProfile,
        request: StoryRequest
    ):
        """异步生成故事"""
        try:
            await self.initialize_ai_orchestrator()
            
            # 获取故事记录
            story = self.db.query(Story).filter(Story.id == story_id).first()
            if not story:
                logger.error(f"Story {story_id} not found")
                return
            
            # 准备请求数据
            child_data = {
                "id": str(child_profile.id),
                "name": child_profile.name,
                "age": child_profile.age,
                "age_group": child_profile.age_group,
                "neuro_profile": child_profile.neuro_profile or {},
                "preferences": child_profile.preferences or {},
                "cognitive_stage": child_profile.cognitive_stage
            }
            
            story_request_data = {
                "theme": request.theme,
                "series_bible_id": request.series_bible_id,
                "user_preferences": request.user_preferences
            }
            
            # 生成故事
            story_result = await self.ai_orchestrator.generate_story_with_fallback(
                child_data, story_request_data
            )
            
            # 更新故事记录
            story.title = story_result.get("title", "生成的故事")
            story.content = story_result.get("content", {})
            story.generation_type = GenerationType.REALTIME
            story.status = StoryStatus.READY
            story.quality_score = story_result.get("quality_score", 0.0)
            story.safety_score = story_result.get("safety_score", 0.0)
            story.educational_value_score = story_result.get("educational_value_score", 0.0)
            story.word_count = self._calculate_word_count(story.content)
            story.page_count = len(story.content.get("pages", []))
            story.reading_time = self._calculate_reading_time(story.content)
            story.updated_at = datetime.utcnow()
            
            # 添加生成元数据
            story.metadata = {
                **story.metadata,
                "generation_completed_at": datetime.utcnow().isoformat(),
                "ai_model_used": story_result.get("ai_model", "unknown"),
                "generation_time_seconds": story_result.get("generation_time", 0),
                "fallback_used": story_result.get("fallback_reason") is not None
            }
            
            self.db.commit()
            logger.info(f"Story {story_id} generated successfully")
            
        except Exception as e:
            logger.error(f"Story generation failed for {story_id}: {str(e)}")
            
            # 更新故事状态为失败
            story = self.db.query(Story).filter(Story.id == story_id).first()
            if story:
                story.status = StoryStatus.FAILED
                story.metadata = {
                    **story.metadata,
                    "generation_failed_at": datetime.utcnow().isoformat(),
                    "error_message": str(e)
                }
                self.db.commit()
    
    def _calculate_word_count(self, content: Dict[str, Any]) -> int:
        """计算字数"""
        pages = content.get("pages", [])
        total_words = 0
        
        for page in pages:
            text = page.get("text", "")
            # 简单的中文字符计数
            chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
            total_words += chinese_chars
        
        return total_words
    
    def _calculate_reading_time(self, content: Dict[str, Any]) -> int:
        """计算阅读时间（秒）"""
        pages = content.get("pages", [])
        total_time = 0
        
        for page in pages:
            reading_time = page.get("reading_time_seconds", 30)
            total_time += reading_time
        
        return total_time
    
    async def get_story_generation_status(self, story_id: uuid.UUID) -> Dict[str, Any]:
        """获取故事生成状态"""
        story = self.db.query(Story).filter(Story.id == story_id).first()
        
        if not story:
            return {"status": "not_found"}
        
        if story.status == StoryStatus.GENERATING:
            # 计算预估剩余时间
            generation_start = story.created_at
            elapsed_time = (datetime.utcnow() - generation_start).total_seconds()
            estimated_total = 120  # 预估2分钟
            remaining_time = max(0, estimated_total - elapsed_time)
            
            return {
                "status": "generating",
                "progress_percentage": min(90, (elapsed_time / estimated_total) * 100),
                "estimated_remaining_seconds": int(remaining_time)
            }
        
        elif story.status == StoryStatus.READY:
            return {
                "status": "ready",
                "story_id": str(story.id),
                "title": story.title,
                "quality_score": story.quality_score
            }
        
        elif story.status == StoryStatus.FAILED:
            return {
                "status": "failed",
                "error_message": story.metadata.get("error_message", "Unknown error")
            }
        
        return {"status": "unknown"}
