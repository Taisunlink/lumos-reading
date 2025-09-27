import asyncio
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging

from config import config
from utils.qwen_client import QwenClient
from utils.cost_tracker import CostTracker
from agents.psychology.expert import EducationalFramework
from agents.story_creation.expert import StoryContent

logger = logging.getLogger(__name__)

class SafetyCheck(BaseModel):
    """安全检查结果"""
    violence_level: float = 0.0
    inappropriate_content: bool = False
    age_appropriateness: float = 0.0
    cultural_sensitivity: float = 0.0
    overall_safety_score: float = 0.0
    safety_issues: List[str] = Field(default_factory=list)

class EducationalAlignment(BaseModel):
    """教育目标对齐度"""
    learning_objective_coverage: float = 0.0
    cognitive_development_support: float = 0.0
    attention_span_appropriateness: float = 0.0
    interaction_effectiveness: float = 0.0
    overall_educational_score: float = 0.0
    improvement_suggestions: List[str] = Field(default_factory=list)

class QualityControlReport(BaseModel):
    """质量控制报告"""
    overall_quality_score: float
    safety_check: SafetyCheck
    educational_alignment: EducationalAlignment
    language_quality: float
    narrative_coherence: float
    cultural_appropriateness: float
    approval_status: str  # approved, needs_revision, rejected
    revision_requirements: List[str] = Field(default_factory=list)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)

class QualityController:
    """
    质量控制器Agent - 基于通义千问
    专注于内容安全、教育价值和整体质量评估
    """

    def __init__(self, redis_client):
        self.qwen_client = QwenClient(
            api_key=config.qwen_api_key,
            base_url=config.qwen_api_url
        )
        self.redis_client = redis_client
        self.cost_tracker = CostTracker(redis_client)
        self.safety_keywords = self._load_safety_keywords()
        self.educational_standards = self._load_educational_standards()

    async def comprehensive_quality_check(
        self,
        story_content: StoryContent,
        framework: EducationalFramework,
        child_profile: Dict[str, Any]
    ) -> QualityControlReport:
        """
        综合质量检查
        """

        try:
            # 并行执行多个检查
            safety_task = self._safety_check(story_content, child_profile)
            educational_task = self._educational_alignment_check(story_content, framework)
            language_task = self._language_quality_check(story_content, framework)
            narrative_task = self._narrative_coherence_check(story_content)
            cultural_task = self._cultural_appropriateness_check(story_content)

            # 等待所有检查完成
            results = await asyncio.gather(
                safety_task, educational_task, language_task, 
                narrative_task, cultural_task, return_exceptions=True
            )

            safety_check = results[0] if not isinstance(results[0], Exception) else SafetyCheck()
            educational_alignment = results[1] if not isinstance(results[1], Exception) else EducationalAlignment()
            language_quality = results[2] if not isinstance(results[2], Exception) else 0.5
            narrative_coherence = results[3] if not isinstance(results[3], Exception) else 0.5
            cultural_appropriateness = results[4] if not isinstance(results[4], Exception) else 0.5

            # 计算总体质量分数
            overall_score = (
                safety_check.overall_safety_score * 0.3 +
                educational_alignment.overall_educational_score * 0.25 +
                language_quality * 0.2 +
                narrative_coherence * 0.15 +
                cultural_appropriateness * 0.1
            )

            # 确定审批状态
            approval_status = self._determine_approval_status(
                overall_score, safety_check, educational_alignment
            )

            # 生成修订要求
            revision_requirements = self._generate_revision_requirements(
                safety_check, educational_alignment, overall_score
            )

            # 构建质量指标
            quality_metrics = {
                "safety_score": safety_check.overall_safety_score,
                "educational_score": educational_alignment.overall_educational_score,
                "language_score": language_quality,
                "narrative_score": narrative_coherence,
                "cultural_score": cultural_appropriateness,
                "overall_score": overall_score
            }

            report = QualityControlReport(
                overall_quality_score=overall_score,
                safety_check=safety_check,
                educational_alignment=educational_alignment,
                language_quality=language_quality,
                narrative_coherence=narrative_coherence,
                cultural_appropriateness=cultural_appropriateness,
                approval_status=approval_status,
                revision_requirements=revision_requirements,
                quality_metrics=quality_metrics
            )

            logger.info(f"Quality check completed: {approval_status}, Score: {overall_score:.2f}")
            return report

        except Exception as e:
            logger.error(f"Quality check failed: {str(e)}")
            # 返回基础质量报告
            return self._get_fallback_quality_report()

    async def _safety_check(self, story: StoryContent, child_profile: Dict[str, Any]) -> SafetyCheck:
        """安全检查"""
        
        # 构建安全检查提示词
        prompt = f"""
你是专业的儿童内容安全审核专家，请对以下故事内容进行安全检查：

故事标题: {story.title}
故事内容: {self._extract_story_text(story)}
目标年龄: {child_profile.get('age', 5)}岁

请检查以下安全指标：
1. 暴力内容等级 (0-1分，0为无暴力，1为严重暴力)
2. 不当内容检测 (是否有性暗示、恐怖、血腥等)
3. 年龄适宜性 (内容是否适合目标年龄)
4. 文化敏感性 (是否包含不当文化内容)

请以JSON格式输出检查结果：
{{
    "violence_level": 0.0,
    "inappropriate_content": false,
    "age_appropriateness": 0.9,
    "cultural_sensitivity": 0.8,
    "safety_issues": ["具体的安全问题列表"]
}}
        """

        try:
            response = await self.qwen_client.generate(
                model=config.quality_control_model,
                prompt=prompt,
                max_tokens=config.max_quality_tokens,
                temperature=0.1  # 保持严格性
            )

            # 解析响应
            safety_data = self._parse_json_response(response.get('text', '{}'))
            
            # 计算总体安全分数
            overall_safety = (
                (1 - safety_data.get('violence_level', 0)) * 0.3 +
                (0 if safety_data.get('inappropriate_content', False) else 1) * 0.3 +
                safety_data.get('age_appropriateness', 0.5) * 0.2 +
                safety_data.get('cultural_sensitivity', 0.5) * 0.2
            )

            return SafetyCheck(
                violence_level=safety_data.get('violence_level', 0),
                inappropriate_content=safety_data.get('inappropriate_content', False),
                age_appropriateness=safety_data.get('age_appropriateness', 0.5),
                cultural_sensitivity=safety_data.get('cultural_sensitivity', 0.5),
                overall_safety_score=overall_safety,
                safety_issues=safety_data.get('safety_issues', [])
            )

        except Exception as e:
            logger.error(f"Safety check failed: {str(e)}")
            return SafetyCheck(overall_safety_score=0.5)

    async def _educational_alignment_check(
        self, 
        story: StoryContent, 
        framework: EducationalFramework
    ) -> EducationalAlignment:
        """教育目标对齐检查"""
        
        prompt = f"""
你是儿童教育专家，请评估以下故事的教育价值：

故事内容: {self._extract_story_text(story)}
教育框架: {framework.dict()}

请评估：
1. 学习目标覆盖度 (故事是否支持设定的学习目标)
2. 认知发展支持 (是否促进目标认知阶段发展)
3. 注意力时长适宜性 (是否符合目标注意力时长)
4. 互动有效性 (CROWD策略是否有效嵌入)

请以JSON格式输出：
{{
    "learning_objective_coverage": 0.8,
    "cognitive_development_support": 0.7,
    "attention_span_appropriateness": 0.9,
    "interaction_effectiveness": 0.8,
    "improvement_suggestions": ["改进建议列表"]
}}
        """

        try:
            response = await self.qwen_client.generate(
                model=config.quality_control_model,
                prompt=prompt,
                max_tokens=config.max_quality_tokens,
                temperature=0.2
            )

            edu_data = self._parse_json_response(response.get('text', '{}'))
            
            overall_educational = (
                edu_data.get('learning_objective_coverage', 0.5) * 0.3 +
                edu_data.get('cognitive_development_support', 0.5) * 0.3 +
                edu_data.get('attention_span_appropriateness', 0.5) * 0.2 +
                edu_data.get('interaction_effectiveness', 0.5) * 0.2
            )

            return EducationalAlignment(
                learning_objective_coverage=edu_data.get('learning_objective_coverage', 0.5),
                cognitive_development_support=edu_data.get('cognitive_development_support', 0.5),
                attention_span_appropriateness=edu_data.get('attention_span_appropriateness', 0.5),
                interaction_effectiveness=edu_data.get('interaction_effectiveness', 0.5),
                overall_educational_score=overall_educational,
                improvement_suggestions=edu_data.get('improvement_suggestions', [])
            )

        except Exception as e:
            logger.error(f"Educational alignment check failed: {str(e)}")
            return EducationalAlignment(overall_educational_score=0.5)

    async def _language_quality_check(self, story: StoryContent, framework: EducationalFramework) -> float:
        """语言质量检查"""
        # 简化的语言质量检查
        total_words = sum(page.word_count for page in story.pages)
        avg_words_per_page = total_words / len(story.pages) if story.pages else 0
        
        # 检查词汇丰富度
        all_text = ' '.join(page.text for page in story.pages)
        unique_words = len(set(all_text.split()))
        vocabulary_richness = min(1.0, unique_words / 50)
        
        # 检查年龄适宜性
        age_appropriateness = self._check_age_appropriate_language(story, framework.age_group)
        
        return (vocabulary_richness + age_appropriateness) / 2

    async def _narrative_coherence_check(self, story: StoryContent) -> float:
        """叙事连贯性检查"""
        if len(story.pages) < 3:
            return 0.3
        
        # 检查故事结构
        has_beginning = any('从前' in page.text or '很久很久以前' in page.text for page in story.pages[:2])
        has_ending = any('从此' in page.text or '最后' in page.text for page in story.pages[-2:])
        
        structure_score = 0.5
        if has_beginning:
            structure_score += 0.25
        if has_ending:
            structure_score += 0.25
        
        return min(1.0, structure_score)

    async def _cultural_appropriateness_check(self, story: StoryContent) -> float:
        """文化适宜性检查"""
        if not story.cultural_elements:
            return 0.6
        
        # 检查是否包含积极的文化元素
        positive_elements = ['友谊', '帮助', '诚实', '勇敢', '爱', '分享']
        text_content = ' '.join(page.text for page in story.pages)
        positive_count = sum(1 for element in positive_elements if element in text_content)
        
        return min(1.0, 0.5 + positive_count * 0.1)

    def _extract_story_text(self, story: StoryContent) -> str:
        """提取故事文本"""
        return ' '.join(page.text for page in story.pages)

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return {}
            
            json_str = text[json_start:json_end]
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"JSON parsing failed: {str(e)}")
            return {}

    def _check_age_appropriate_language(self, story: StoryContent, age_group: str) -> float:
        """检查年龄适宜的语言"""
        # 简化的年龄适宜性检查
        if "3-5" in age_group:
            return 0.9  # 假设内容适合
        elif "6-8" in age_group:
            return 0.8
        elif "9-11" in age_group:
            return 0.7
        else:
            return 0.5

    def _determine_approval_status(
        self, 
        overall_score: float, 
        safety_check: SafetyCheck, 
        educational_alignment: EducationalAlignment
    ) -> str:
        """确定审批状态"""
        if safety_check.inappropriate_content or safety_check.overall_safety_score < 0.3:
            return "rejected"
        elif overall_score < 0.6 or educational_alignment.overall_educational_score < 0.4:
            return "needs_revision"
        else:
            return "approved"

    def _generate_revision_requirements(
        self, 
        safety_check: SafetyCheck, 
        educational_alignment: EducationalAlignment, 
        overall_score: float
    ) -> List[str]:
        """生成修订要求"""
        requirements = []
        
        if safety_check.safety_issues:
            requirements.extend(safety_check.safety_issues)
        
        if educational_alignment.improvement_suggestions:
            requirements.extend(educational_alignment.improvement_suggestions)
        
        if overall_score < 0.7:
            requirements.append("整体质量需要提升")
        
        return requirements

    def _get_fallback_quality_report(self) -> QualityControlReport:
        """获取后备质量报告"""
        return QualityControlReport(
            overall_quality_score=0.5,
            safety_check=SafetyCheck(overall_safety_score=0.5),
            educational_alignment=EducationalAlignment(overall_educational_score=0.5),
            language_quality=0.5,
            narrative_coherence=0.5,
            cultural_appropriateness=0.5,
            approval_status="needs_revision",
            revision_requirements=["需要人工审核"]
        )

    def _load_safety_keywords(self) -> Dict[str, List[str]]:
        """加载安全关键词库"""
        return {
            "violence": ["打", "杀", "死", "血", "暴力"],
            "inappropriate": ["恐怖", "鬼", "恶魔", "诅咒"],
            "positive": ["爱", "友谊", "帮助", "分享", "诚实"]
        }

    def _load_educational_standards(self) -> Dict[str, Any]:
        """加载教育标准"""
        return {
            "age_appropriate_vocabulary": {
                "3-5": ["简单词汇", "重复句式"],
                "6-8": ["基础词汇", "简单句子"],
                "9-11": ["丰富词汇", "复杂句式"]
            }
        }
