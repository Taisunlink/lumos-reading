import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging

from config import config
from utils.qwen_client import QwenClient
from utils.cost_tracker import CostTracker
from agents.psychology.expert import EducationalFramework

logger = logging.getLogger(__name__)

class StoryPage(BaseModel):
    """故事页面结构"""
    page_number: int
    text: str
    illustration_prompt: str
    crowd_prompt: Optional[Dict[str, str]] = None
    reading_time_seconds: int = 30
    word_count: int = 0

class Character(BaseModel):
    """角色定义"""
    name: str
    description: str
    personality: str
    visual_description: str
    role_in_story: str

class StoryContent(BaseModel):
    """完整故事内容"""
    title: str
    moral_theme: str
    pages: List[StoryPage]
    characters: List[Character]
    vocabulary_targets: List[str]
    extension_activities: List[str]
    cultural_elements: List[str]
    educational_value_score: float = 0.0
    language_complexity_level: str = "适中"

class QualityReport(BaseModel):
    """文学质量报告"""
    overall_score: float
    language_appropriateness: float
    cultural_sensitivity: float
    narrative_coherence: float
    educational_value: float
    emotional_resonance: float
    needs_revision: bool = False
    revision_suggestions: List[str] = Field(default_factory=list)

class ChildrenLiteratureExpert:
    """
    儿童文学专家Agent - 基于通义千问
    专注于中文儿童文学创作和质量控制
    """

    def __init__(self, redis_client):
        self.qwen_client = QwenClient(
            api_key=config.qwen_api_key,
            base_url=config.qwen_api_url
        )
        self.redis_client = redis_client
        self.cost_tracker = CostTracker(redis_client)
        self.template_library = self._load_literature_templates()
        self.cultural_elements_db = self._load_cultural_elements()

    async def create_story_content(
        self,
        framework: EducationalFramework,
        theme: str,
        series_bible: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None
    ) -> StoryContent:
        """
        基于教育框架创作高质量故事内容
        """

        try:
            # 构建文学创作提示词
            prompt = await self._build_literature_prompt(
                framework, theme, series_bible, user_preferences
            )

            # 调用通义千问生成故事
            response = await self.qwen_client.generate(
                model=config.story_creation_model,
                prompt=prompt,
                max_tokens=config.max_story_tokens,
                temperature=0.7,  # 保持创意性
                top_k=50,
                top_p=0.8
            )

            # 解析故事内容
            story_content = await self._parse_story_response(response)

            # 文学质量自检
            quality_report = await self._literature_quality_check(story_content, framework)

            # 如需改进则自动优化
            if quality_report.needs_revision:
                story_content = await self._revise_content(story_content, quality_report)
                # 再次质量检查
                quality_report = await self._literature_quality_check(story_content, framework)

            # 记录质量分数
            story_content.educational_value_score = quality_report.overall_score

            logger.info(f"Story created: {story_content.title}, Quality: {quality_report.overall_score:.2f}")
            return story_content

        except Exception as e:
            logger.error(f"Story creation failed: {str(e)}")
            # 返回模板故事作为后备
            return await self._get_template_story(theme, framework)

    async def _build_literature_prompt(
        self,
        framework: EducationalFramework,
        theme: str,
        series_bible: Optional[Dict],
        user_preferences: Optional[Dict]
    ) -> str:
        """构建专业儿童文学创作提示词"""

        # 基础创作要求
        base_prompt = f"""
你是享誉国际的中文儿童文学作家，曾获得国际安徒生奖，专精于3-11岁儿童绘本创作。

创作任务：
主题: {theme}
认知发展阶段: {framework.cognitive_stage}
目标年龄: {framework.age_group}
注意力时长: {framework.attention_span_target}分钟
学习目标: {', '.join(framework.learning_objectives)}

文学创作要求：
1. 故事结构: 经典的"起承转合"结构，符合儿童认知节奏
2. 语言风格:
   - 生动形象，富有韵律感
   - 易于朗读，适合亲子共读
   - 词汇难度符合年龄特点
   - 句式长短搭配，节奏感强
3. 情感表达: 细腻丰富，帮助儿童理解和表达情感
4. 教育价值: 自然融入，避免生硬说教

页面规划：
- 总页数: 8-12页
- 每页字数: {self._get_word_count_by_age(framework.age_group)}
- 插图描述: 详细的视觉化描述，便于AI绘图

CROWD互动嵌入要求：
{self._format_crowd_strategy(framework.crowd_strategy)}

文化价值观要求：
- 体现中华文化优秀传统
- 传递积极正面的人生观
- 包容性和多样性
- 无性别刻板印象
- 尊重不同家庭结构

请创作完整故事，严格按照以下JSON格式输出：

{{
    "title": "富有吸引力的故事标题",
    "moral_theme": "故事传达的核心价值",
    "pages": [
        {{
            "page_number": 1,
            "text": "这一页的文字内容，注意韵律和节奏",
            "illustration_prompt": "详细的插图描述，包含场景、角色、情绪、色彩风格",
            "crowd_prompt": {{"type": "completion", "text": "互动提示语"}},
            "reading_time_seconds": 预估阅读时间,
            "word_count": 字数统计
        }}
    ],
    "characters": [
        {{
            "name": "角色名字",
            "description": "角色背景描述",
            "personality": "性格特点",
            "visual_description": "外观特征描述",
            "role_in_story": "在故事中的作用"
        }}
    ],
    "vocabulary_targets": ["故事中的重点词汇"],
    "extension_activities": ["延伸阅读活动建议"],
    "cultural_elements": ["体现的文化元素"]
}}
        """

        # 神经多样性适配
        if framework.neuro_adaptations:
            base_prompt += f"""

神经多样性友好设计：
{self._format_neuro_adaptations(framework.neuro_adaptations)}
            """

        # Series Bible一致性要求
        if series_bible:
            base_prompt += f"""

系列一致性要求：
- 固定角色设定: {json.dumps(series_bible.get('characters', {}), ensure_ascii=False)}
- 世界观背景: {json.dumps(series_bible.get('world_settings', {}), ensure_ascii=False)}
- 叙事风格: {series_bible.get('narrative_style', {})}
- 视觉风格: {series_bible.get('visual_style', {})}

请确保新故事与已有设定保持一致，同时带来新的情节发展。
            """

        # 用户偏好
        if user_preferences:
            base_prompt += f"""

用户偏好考虑：
{json.dumps(user_preferences, ensure_ascii=False)}
            """

        return base_prompt

    def _get_word_count_by_age(self, age_group: str) -> int:
        """根据年龄组确定每页字数"""
        if "3-5" in age_group:
            return 15
        elif "6-8" in age_group:
            return 25
        elif "9-11" in age_group:
            return 35
        else:
            return 20

    def _format_crowd_strategy(self, crowd_strategy) -> str:
        """格式化CROWD策略"""
        return f"""
- 完成句子类互动: {', '.join(crowd_strategy.completion_prompts[:3])}
- 回忆性问题: {', '.join(crowd_strategy.recall_questions[:3])}
- 开放性讨论: {', '.join(crowd_strategy.open_ended_prompts[:3])}
- 5W1H问题: {', '.join(crowd_strategy.wh_questions[:3])}
- 联系现实经验: {', '.join(crowd_strategy.distancing_connections[:3])}
        """

    def _format_neuro_adaptations(self, neuro_adaptations) -> str:
        """格式化神经多样性适配"""
        return f"""
- 注意力支持: {json.dumps(neuro_adaptations.attention_supports, ensure_ascii=False)}
- 感官调节: {json.dumps(neuro_adaptations.sensory_adjustments, ensure_ascii=False)}
- 互动调整: {json.dumps(neuro_adaptations.interaction_modifications, ensure_ascii=False)}
- 认知支架: {json.dumps(neuro_adaptations.cognitive_scaffolding, ensure_ascii=False)}
        """

    async def _parse_story_response(self, response: Dict[str, Any]) -> StoryContent:
        """解析故事响应"""
        try:
            text = response.get('text', '')
            
            # 提取JSON部分
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = text[json_start:json_end]
            story_data = json.loads(json_str)
            
            # 解析页面
            pages = []
            for page_data in story_data.get('pages', []):
                page = StoryPage(
                    page_number=page_data.get('page_number', 0),
                    text=page_data.get('text', ''),
                    illustration_prompt=page_data.get('illustration_prompt', ''),
                    crowd_prompt=page_data.get('crowd_prompt'),
                    reading_time_seconds=page_data.get('reading_time_seconds', 30),
                    word_count=page_data.get('word_count', 0)
                )
                pages.append(page)
            
            # 解析角色
            characters = []
            for char_data in story_data.get('characters', []):
                character = Character(
                    name=char_data.get('name', ''),
                    description=char_data.get('description', ''),
                    personality=char_data.get('personality', ''),
                    visual_description=char_data.get('visual_description', ''),
                    role_in_story=char_data.get('role_in_story', '')
                )
                characters.append(character)
            
            # 构建故事内容
            story_content = StoryContent(
                title=story_data.get('title', '未命名故事'),
                moral_theme=story_data.get('moral_theme', ''),
                pages=pages,
                characters=characters,
                vocabulary_targets=story_data.get('vocabulary_targets', []),
                extension_activities=story_data.get('extension_activities', []),
                cultural_elements=story_data.get('cultural_elements', [])
            )
            
            return story_content
            
        except Exception as e:
            logger.error(f"Failed to parse story response: {str(e)}")
            raise ValueError(f"Invalid story response format: {str(e)}")

    async def _literature_quality_check(
        self, 
        story_content: StoryContent, 
        framework: EducationalFramework
    ) -> QualityReport:
        """文学质量检查"""
        
        # 基础质量指标
        language_score = self._check_language_appropriateness(story_content, framework)
        cultural_score = self._check_cultural_sensitivity(story_content)
        narrative_score = self._check_narrative_coherence(story_content)
        educational_score = self._check_educational_value(story_content, framework)
        emotional_score = self._check_emotional_resonance(story_content)
        
        overall_score = (language_score + cultural_score + narrative_score + 
                        educational_score + emotional_score) / 5
        
        needs_revision = overall_score < 0.7
        revision_suggestions = []
        
        if language_score < 0.7:
            revision_suggestions.append("语言难度需要调整，确保符合目标年龄")
        if cultural_score < 0.7:
            revision_suggestions.append("文化敏感性需要改进")
        if narrative_score < 0.7:
            revision_suggestions.append("故事结构需要优化")
        if educational_score < 0.7:
            revision_suggestions.append("教育价值需要加强")
        if emotional_score < 0.7:
            revision_suggestions.append("情感共鸣需要提升")
        
        return QualityReport(
            overall_score=overall_score,
            language_appropriateness=language_score,
            cultural_sensitivity=cultural_score,
            narrative_coherence=narrative_score,
            educational_value=educational_score,
            emotional_resonance=emotional_score,
            needs_revision=needs_revision,
            revision_suggestions=revision_suggestions
        )

    def _check_language_appropriateness(self, story: StoryContent, framework: EducationalFramework) -> float:
        """检查语言适龄性"""
        # 简化的语言复杂度检查
        total_words = sum(page.word_count for page in story.pages)
        avg_words_per_page = total_words / len(story.pages) if story.pages else 0
        
        # 根据年龄组检查
        if "3-5" in framework.age_group:
            return 0.9 if avg_words_per_page <= 20 else 0.6
        elif "6-8" in framework.age_group:
            return 0.9 if 15 <= avg_words_per_page <= 30 else 0.6
        elif "9-11" in framework.age_group:
            return 0.9 if 25 <= avg_words_per_page <= 40 else 0.6
        else:
            return 0.8

    def _check_cultural_sensitivity(self, story: StoryContent) -> float:
        """检查文化敏感性"""
        # 检查是否包含文化元素
        if story.cultural_elements:
            return 0.9
        return 0.7

    def _check_narrative_coherence(self, story: StoryContent) -> float:
        """检查叙事连贯性"""
        if len(story.pages) < 6:
            return 0.6
        if not story.characters:
            return 0.5
        return 0.8

    def _check_educational_value(self, story: StoryContent, framework: EducationalFramework) -> float:
        """检查教育价值"""
        if story.moral_theme and story.vocabulary_targets:
            return 0.9
        return 0.6

    def _check_emotional_resonance(self, story: StoryContent) -> float:
        """检查情感共鸣"""
        # 检查是否包含情感词汇
        emotional_words = ['开心', '快乐', '难过', '害怕', '勇敢', '爱', '友谊', '帮助']
        text_content = ' '.join(page.text for page in story.pages)
        emotional_count = sum(1 for word in emotional_words if word in text_content)
        return min(0.9, 0.5 + emotional_count * 0.1)

    async def _revise_content(self, story: StoryContent, quality_report: QualityReport) -> StoryContent:
        """根据质量报告修订内容"""
        # 这里可以实现自动修订逻辑
        # 目前返回原内容
        logger.info(f"Content revision needed: {quality_report.revision_suggestions}")
        return story

    async def _get_template_story(self, theme: str, framework: EducationalFramework) -> StoryContent:
        """获取模板故事作为后备"""
        return StoryContent(
            title=f"关于{theme}的故事",
            moral_theme=theme,
            pages=[
                StoryPage(
                    page_number=1,
                    text=f"从前有一个关于{theme}的故事...",
                    illustration_prompt="温馨的童话场景",
                    reading_time_seconds=30,
                    word_count=15
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
            vocabulary_targets=[theme],
            extension_activities=["讨论故事主题"],
            cultural_elements=["中华文化元素"]
        )

    def _load_literature_templates(self) -> Dict[str, Any]:
        """加载文学模板库"""
        return {
            "story_structures": ["起承转合", "三幕式", "英雄之旅"],
            "character_archetypes": ["英雄", "导师", "伙伴", "反派"],
            "themes": ["友谊", "勇气", "诚实", "分享", "成长"]
        }

    def _load_cultural_elements(self) -> Dict[str, Any]:
        """加载文化元素数据库"""
        return {
            "festivals": ["春节", "中秋节", "端午节"],
            "values": ["孝道", "诚信", "和谐", "自强"],
            "symbols": ["龙", "凤凰", "熊猫", "竹子"]
        }
