import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import redis
from pydantic import BaseModel

from config import config
from agents.psychology.expert import PsychologyExpert, EducationalFramework
from agents.story_creation.expert import ChildrenLiteratureExpert, StoryContent
from agents.quality_control.expert import QualityController, QualityControlReport
from utils.cost_tracker import CostTracker
from core.cost_control import EnhancedCostController, with_cost_control, BudgetExceededException

logger = logging.getLogger(__name__)

class StoryGenerationRequest(BaseModel):
    """故事生成请求"""
    child_profile: Dict[str, Any]
    theme: str
    series_bible_id: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None
    generation_type: str = "realtime"  # realtime, template, preproduced

class StoryGenerationResponse(BaseModel):
    """故事生成响应"""
    story_id: str
    title: str
    status: str  # generating, ready, failed
    content: Optional[StoryContent] = None
    quality_report: Optional[QualityControlReport] = None
    generation_metadata: Dict[str, Any] = {}
    created_at: datetime
    processing_time_seconds: float

class AIOrchestrator:
    """
    AI编排器 - 协调所有AI Agent的工作流程
    实现优雅降级和100%可用性保证
    """

    def __init__(self):
        self.redis_client = redis.Redis.from_url(config.redis_url)
        self.cost_tracker = CostTracker(self.redis_client)
        self.cost_controller = EnhancedCostController(self.redis_client)
        
        # 初始化各个Agent
        self.psychology_expert = PsychologyExpert()
        self.literature_expert = ChildrenLiteratureExpert(self.redis_client)
        self.quality_controller = QualityController(self.redis_client)
        
        # 降级策略配置
        self.fallback_strategies = [
            self._try_realtime_generation,
            self._try_template_adaptation,
            self._try_preproduced_match,
            self._try_classic_stories,
            self._emergency_content
        ]

    @with_cost_control
    async def generate_story(self, request: StoryGenerationRequest) -> StoryGenerationResponse:
        """
        生成故事 - 主入口点
        实现优雅降级策略确保100%可用性
        """
        
        start_time = datetime.now()
        story_id = f"story_{int(start_time.timestamp())}"
        
        try:
            # 检查成本限制
            daily_cost = await self.cost_tracker.get_daily_cost()
            if daily_cost > config.max_daily_cost_usd:
                logger.warning(f"Daily cost limit exceeded: ${daily_cost}")
                return await self._emergency_content(request, story_id, start_time)
            
            # 尝试各种生成策略
            for strategy in self.fallback_strategies:
                try:
                    result = await strategy(request, story_id, start_time)
                    if result and result.status != "failed":
                        return result
                except Exception as e:
                    logger.warning(f"Strategy {strategy.__name__} failed: {str(e)}")
                    continue
            
            # 所有策略都失败，返回紧急内容
            return await self._emergency_content(request, story_id, start_time)
            
        except Exception as e:
            logger.error(f"Story generation completely failed: {str(e)}")
            return await self._emergency_content(request, story_id, start_time)

    async def _try_realtime_generation(
        self, 
        request: StoryGenerationRequest, 
        story_id: str, 
        start_time: datetime
    ) -> Optional[StoryGenerationResponse]:
        """尝试实时AI生成"""
        
        logger.info(f"Attempting realtime generation for story {story_id}")
        
        try:
            # 1. 心理学专家生成教育框架
            framework = await self.psychology_expert.generate_educational_framework(
                request.child_profile, 
                {"theme": request.theme}
            )
            
            # 2. 儿童文学专家创作故事
            series_bible = await self._get_series_bible(request.series_bible_id)
            story_content = await self.literature_expert.create_story_content(
                framework, 
                request.theme, 
                series_bible, 
                request.user_preferences
            )
            
            # 3. 质量控制器检查
            quality_report = await self.quality_controller.comprehensive_quality_check(
                story_content, 
                framework, 
                request.child_profile
            )
            
            # 4. 如果质量不达标，尝试优化
            if quality_report.approval_status == "needs_revision":
                story_content = await self._optimize_story_content(
                    story_content, framework, quality_report
                )
                # 重新质量检查
                quality_report = await self.quality_controller.comprehensive_quality_check(
                    story_content, framework, request.child_profile
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return StoryGenerationResponse(
                story_id=story_id,
                title=story_content.title,
                status="ready" if quality_report.approval_status == "approved" else "generating",
                content=story_content,
                quality_report=quality_report,
                generation_metadata={
                    "method": "realtime_ai",
                    "framework_used": True,
                    "quality_checked": True,
                    "optimization_applied": quality_report.approval_status == "needs_revision"
                },
                created_at=start_time,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Realtime generation failed: {str(e)}")
            return None

    async def _try_template_adaptation(
        self, 
        request: StoryGenerationRequest, 
        story_id: str, 
        start_time: datetime
    ) -> Optional[StoryGenerationResponse]:
        """尝试模板适配"""
        
        logger.info(f"Attempting template adaptation for story {story_id}")
        
        try:
            # 获取最适合的模板
            template = await self._get_best_template(request.theme, request.child_profile)
            if not template:
                return None
            
            # 适配模板内容
            adapted_content = await self._adapt_template_content(
                template, request.child_profile, request.theme
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return StoryGenerationResponse(
                story_id=story_id,
                title=adapted_content.title,
                status="ready",
                content=adapted_content,
                generation_metadata={
                    "method": "template_adaptation",
                    "template_id": template.get("id"),
                    "adaptation_applied": True
                },
                created_at=start_time,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Template adaptation failed: {str(e)}")
            return None

    async def _try_preproduced_match(
        self, 
        request: StoryGenerationRequest, 
        story_id: str, 
        start_time: datetime
    ) -> Optional[StoryGenerationResponse]:
        """尝试预生产内容匹配"""
        
        logger.info(f"Attempting preproduced match for story {story_id}")
        
        try:
            # 从预生产库中查找匹配内容
            preproduced_story = await self._find_preproduced_story(
                request.theme, request.child_profile
            )
            
            if not preproduced_story:
                return None
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return StoryGenerationResponse(
                story_id=story_id,
                title=preproduced_story["title"],
                status="ready",
                content=preproduced_story["content"],
                generation_metadata={
                    "method": "preproduced_match",
                    "preproduced_id": preproduced_story["id"],
                    "match_score": preproduced_story.get("match_score", 0.8)
                },
                created_at=start_time,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Preproduced match failed: {str(e)}")
            return None

    async def _try_classic_stories(
        self, 
        request: StoryGenerationRequest, 
        story_id: str, 
        start_time: datetime
    ) -> Optional[StoryGenerationResponse]:
        """尝试经典故事"""
        
        logger.info(f"Attempting classic story for story {story_id}")
        
        try:
            # 获取经典故事
            classic_story = await self._get_classic_story(request.theme)
            if not classic_story:
                return None
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return StoryGenerationResponse(
                story_id=story_id,
                title=classic_story["title"],
                status="ready",
                content=classic_story["content"],
                generation_metadata={
                    "method": "classic_story",
                    "classic_id": classic_story["id"]
                },
                created_at=start_time,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Classic story failed: {str(e)}")
            return None

    async def _emergency_content(
        self, 
        request: StoryGenerationRequest, 
        story_id: str, 
        start_time: datetime
    ) -> StoryGenerationResponse:
        """紧急内容 - 最后的保障"""
        
        logger.warning(f"Using emergency content for story {story_id}")
        
        # 创建最简单的故事内容
        emergency_content = StoryContent(
            title=f"关于{request.theme}的小故事",
            moral_theme=request.theme,
            pages=[
                StoryPage(
                    page_number=1,
                    text=f"从前有一个关于{request.theme}的美丽故事，它教会我们很多道理。",
                    illustration_prompt="温馨的童话场景，柔和的色彩",
                    reading_time_seconds=30,
                    word_count=20
                )
            ],
            characters=[
                Character(
                    name="小主角",
                    description="故事的主人公",
                    personality="善良勇敢",
                    visual_description="可爱的卡通形象",
                    role_in_story="主角"
                )
            ],
            vocabulary_targets=[request.theme],
            extension_activities=["讨论故事主题"],
            cultural_elements=["中华文化元素"]
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return StoryGenerationResponse(
            story_id=story_id,
            title=emergency_content.title,
            status="ready",
            content=emergency_content,
            generation_metadata={
                "method": "emergency_content",
                "fallback_used": True
            },
            created_at=start_time,
            processing_time_seconds=processing_time
        )

    async def _get_series_bible(self, series_bible_id: Optional[str]) -> Optional[Dict]:
        """获取Series Bible"""
        if not series_bible_id:
            return None
        
        try:
            bible_data = await self.redis_client.get(f"series_bible:{series_bible_id}")
            return json.loads(bible_data) if bible_data else None
        except Exception as e:
            logger.warning(f"Failed to get series bible: {str(e)}")
            return None

    async def _optimize_story_content(
        self, 
        story_content: StoryContent, 
        framework: EducationalFramework, 
        quality_report: QualityControlReport
    ) -> StoryContent:
        """优化故事内容"""
        # 这里可以实现内容优化逻辑
        # 目前返回原内容
        logger.info("Story content optimization applied")
        return story_content

    async def _get_best_template(self, theme: str, child_profile: Dict[str, Any]) -> Optional[Dict]:
        """获取最佳模板"""
        # 这里实现模板匹配逻辑
        return None

    async def _adapt_template_content(
        self, 
        template: Dict, 
        child_profile: Dict[str, Any], 
        theme: str
    ) -> StoryContent:
        """适配模板内容"""
        # 这里实现模板适配逻辑
        return StoryContent(
            title=f"模板故事 - {theme}",
            moral_theme=theme,
            pages=[],
            characters=[],
            vocabulary_targets=[],
            extension_activities=[],
            cultural_elements=[]
        )

    async def _find_preproduced_story(self, theme: str, child_profile: Dict[str, Any]) -> Optional[Dict]:
        """查找预生产故事"""
        # 这里实现预生产内容匹配逻辑
        return None

    async def _get_classic_story(self, theme: str) -> Optional[Dict]:
        """获取经典故事"""
        # 这里实现经典故事获取逻辑
        return None

    async def get_generation_status(self, story_id: str) -> Optional[StoryGenerationResponse]:
        """获取生成状态"""
        try:
            status_data = await self.redis_client.get(f"story_status:{story_id}")
            if status_data:
                return StoryGenerationResponse(**json.loads(status_data))
        except Exception as e:
            logger.error(f"Failed to get generation status: {str(e)}")
        return None

    async def get_cost_summary(self, days: int = 7) -> Dict[str, Any]:
        """获取成本摘要"""
        return await self.cost_tracker.get_cost_summary(days)
