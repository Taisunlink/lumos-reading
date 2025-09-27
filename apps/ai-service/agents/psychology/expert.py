import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from anthropic import AsyncAnthropic
import redis
import logging
import os

from config import config
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)

class NeuroAdaptation(BaseModel):
    """神经多样性适配配置"""
    attention_supports: Dict[str, Any] = Field(default_factory=dict)
    sensory_adjustments: Dict[str, Any] = Field(default_factory=dict)
    interaction_modifications: Dict[str, Any] = Field(default_factory=dict)
    cognitive_scaffolding: Dict[str, Any] = Field(default_factory=dict)

class CROWDStrategy(BaseModel):
    """CROWD对话式阅读策略"""
    completion_prompts: List[str] = Field(default_factory=list)
    recall_questions: List[str] = Field(default_factory=list)
    open_ended_prompts: List[str] = Field(default_factory=list)
    wh_questions: List[str] = Field(default_factory=list)
    distancing_connections: List[str] = Field(default_factory=list)

class EducationalFramework(BaseModel):
    """教育心理学框架"""
    age_group: str
    cognitive_stage: str
    attention_span_target: int  # 分钟
    learning_objectives: List[str]
    crowd_strategy: CROWDStrategy
    neuro_adaptations: Optional[NeuroAdaptation] = None
    interaction_density: str  # low/medium/high
    safety_considerations: List[str]
    cultural_adaptations: List[str]
    parent_guidance: List[str]

class PsychologyExpert:
    """
    心理学专家Agent - 基于Claude
    专注于认知发展理论和神经多样性支持
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=config.anthropic_api_key)
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        self.cost_tracker = CostTracker(self.redis_client)

    async def generate_educational_framework(
        self,
        child_profile: Dict[str, Any],
        story_request: Dict[str, Any]
    ) -> EducationalFramework:
        """
        生成个性化教育心理学框架
        """

        # 生成缓存键
        cache_key = self._get_cache_key(child_profile, story_request)

        # 检查缓存
        if config.enable_framework_cache:
            cached_framework = await self._get_cached_framework(cache_key)
            if cached_framework:
                logger.info(f"Framework cache hit: {cache_key}")
                return cached_framework

        # 构建专业心理学提示词
        prompt = await self._build_psychology_prompt(child_profile, story_request)

        try:
            # 调用Claude API
            response = await self.client.messages.create(
                model=config.psychology_model,
                max_tokens=config.max_framework_tokens,
                temperature=0.3,  # 保持专业一致性
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # 解析响应
            framework = await self._parse_framework_response(response.content[0].text)

            # 缓存结果
            if config.enable_framework_cache:
                await self._cache_framework(cache_key, framework)

            # 记录成本
            await self.cost_tracker.record_usage(
                model=config.psychology_model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )

            logger.info(f"Generated framework for child age {child_profile.get('age', 'unknown')}")
            return framework

        except Exception as e:
            logger.error(f"Framework generation failed: {str(e)}")
            # 返回基础框架作为后备
            return await self._get_fallback_framework(child_profile)

    async def _build_psychology_prompt(
        self,
        child_profile: Dict[str, Any],
        story_request: Dict[str, Any]
    ) -> str:
        """构建专业心理学提示词"""

        age = child_profile.get('age', 5)
        neuro_profile = child_profile.get('neuro_profile', {})
        preferences = child_profile.get('preferences', {})
        theme = story_request.get('theme', '友谊')

        base_prompt = f"""
你是世界顶级的儿童发展心理学专家，拥有哈佛大学心理学博士学位，专精于以下领域：
- 皮亚杰认知发展理论的现代应用
- 维果茨基最近发展区理论
- 神经多样性儿童的个性化支持
- 对话式阅读法(CROWD-PEER)的实施

儿童档案分析：
年龄: {age}岁
认知发展阶段: {self._determine_cognitive_stage(age)}
神经多样性特征: {json.dumps(neuro_profile, ensure_ascii=False)}
阅读偏好: {json.dumps(preferences, ensure_ascii=False)}

故事主题: {theme}

请基于以上信息，设计一个科学严谨的教育心理学框架，包含：

1. 认知适配策略 (基于皮亚杰理论)
2. 注意力管理机制 (考虑注意力发展特点)
3. CROWD对话式阅读嵌入 (5种提示类型的具体应用)
4. 神经多样性适配 (如有相关特征)
5. 情绪调节支持
6. 文化敏感性考虑
7. 家长指导要点

请以JSON格式输出，确保每个建议都有心理学理论依据：

{{
    "cognitive_stage": "具体认知发展阶段",
    "attention_span_target": "推荐注意力时长(分钟)",
    "learning_objectives": ["基于认知发展的学习目标"],
    "crowd_strategy": {{
        "completion_prompts": ["完成句子类互动"],
        "recall_questions": ["回忆性问题"],
        "open_ended_prompts": ["开放性讨论"],
        "wh_questions": ["5W1H问题设计"],
        "distancing_connections": ["联系现实经验"]
    }},
    "neuro_adaptations": {{
        "attention_supports": {{"注意力支持策略"}},
        "sensory_adjustments": {{"感官调节建议"}},
        "interaction_modifications": {{"互动方式调整"}},
        "cognitive_scaffolding": {{"认知支架策略"}}
    }},
    "interaction_density": "互动密度等级(low/medium/high)",
    "safety_considerations": ["心理安全要点"],
    "cultural_adaptations": ["文化适应建议"],
    "parent_guidance": ["家长指导要点"]
}}
        """

        # 根据神经多样性特征添加专门指导
        if neuro_profile.get('adhd_indicators'):
            base_prompt += """

ADHD适配专项指导：
- 应用执行功能支持理论
- 实施注意力调节策略
- 设计即时反馈机制
- 考虑多感官学习通道
- 提供结构化预期
            """

        if neuro_profile.get('autism_indicators'):
            base_prompt += """

自闭谱系适配专项指导：
- 应用社交认知理论
- 实施感官处理支持
- 设计明确情绪标注
- 提供社交脚本指导
- 确保预测性结构
            """

        return base_prompt

    def _determine_cognitive_stage(self, age: int) -> str:
        """基于年龄确定认知发展阶段"""
        if age < 2:
            return "sensorimotor"
        elif age < 7:
            return "preoperational"
        elif age < 11:
            return "concrete_operational"
        else:
            return "formal_operational"

    async def _parse_framework_response(self, response_text: str) -> EducationalFramework:
        """解析Claude响应为教育框架"""
        try:
            # 提取JSON部分
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            framework_data = json.loads(json_str)
            
            # 构建CROWD策略
            crowd_data = framework_data.get('crowd_strategy', {})
            crowd_strategy = CROWDStrategy(
                completion_prompts=crowd_data.get('completion_prompts', []),
                recall_questions=crowd_data.get('recall_questions', []),
                open_ended_prompts=crowd_data.get('open_ended_prompts', []),
                wh_questions=crowd_data.get('wh_questions', []),
                distancing_connections=crowd_data.get('distancing_connections', [])
            )
            
            # 构建神经多样性适配
            neuro_data = framework_data.get('neuro_adaptations', {})
            neuro_adaptations = None
            if neuro_data:
                neuro_adaptations = NeuroAdaptation(
                    attention_supports=neuro_data.get('attention_supports', {}),
                    sensory_adjustments=neuro_data.get('sensory_adjustments', {}),
                    interaction_modifications=neuro_data.get('interaction_modifications', {}),
                    cognitive_scaffolding=neuro_data.get('cognitive_scaffolding', {})
                )
            
            # 构建完整框架
            framework = EducationalFramework(
                age_group=framework_data.get('age_group', '3-5'),
                cognitive_stage=framework_data.get('cognitive_stage', 'preoperational'),
                attention_span_target=framework_data.get('attention_span_target', 5),
                learning_objectives=framework_data.get('learning_objectives', []),
                crowd_strategy=crowd_strategy,
                neuro_adaptations=neuro_adaptations,
                interaction_density=framework_data.get('interaction_density', 'medium'),
                safety_considerations=framework_data.get('safety_considerations', []),
                cultural_adaptations=framework_data.get('cultural_adaptations', []),
                parent_guidance=framework_data.get('parent_guidance', [])
            )
            
            return framework
            
        except Exception as e:
            logger.error(f"Failed to parse framework response: {str(e)}")
            raise ValueError(f"Invalid framework response format: {str(e)}")

    def _get_cache_key(self, child_profile: Dict[str, Any], story_request: Dict[str, Any]) -> str:
        """生成缓存键"""
        cache_data = {
            "age": child_profile.get('age'),
            "neuro_profile": child_profile.get('neuro_profile', {}),
            "theme": story_request.get('theme'),
            "preferences": child_profile.get('preferences', {})
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"psychology_framework:{hashlib.md5(cache_str.encode()).hexdigest()}"

    async def _get_cached_framework(self, cache_key: str) -> Optional[EducationalFramework]:
        """从缓存获取框架"""
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                framework_data = json.loads(cached_data)
                return EducationalFramework(**framework_data)
        except Exception as e:
            logger.warning(f"Cache read error: {str(e)}")
        return None

    async def _cache_framework(self, cache_key: str, framework: EducationalFramework):
        """缓存框架"""
        try:
            framework_data = framework.dict()
            cache_ttl = config.cache_ttl_hours * 3600
            await self.redis_client.setex(
                cache_key, 
                cache_ttl, 
                json.dumps(framework_data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache write error: {str(e)}")

    async def _get_fallback_framework(self, child_profile: Dict[str, Any]) -> EducationalFramework:
        """获取后备框架"""
        age = child_profile.get('age', 5)
        cognitive_stage = self._determine_cognitive_stage(age)
        
        return EducationalFramework(
            age_group=f"{age}-{age+2}",
            cognitive_stage=cognitive_stage,
            attention_span_target=max(3, age),
            learning_objectives=["基础认知发展", "语言能力提升", "情感表达"],
            crowd_strategy=CROWDStrategy(
                completion_prompts=["然后小兔子...", "故事告诉我们..."],
                recall_questions=["刚才发生了什么？", "你记得小兔子做了什么吗？"],
                open_ended_prompts=["你觉得这个故事怎么样？", "如果你是故事里的角色..."],
                wh_questions=["为什么小兔子会这样做？", "什么时候发生的事？"],
                distancing_connections=["你有没有遇到过类似的情况？", "这让你想起了什么？"]
            ),
            interaction_density="medium",
            safety_considerations=["确保内容积极正面", "避免恐怖或暴力元素"],
            cultural_adaptations=["体现中华文化价值观", "尊重多元文化背景"],
            parent_guidance=["鼓励孩子表达想法", "耐心倾听孩子的回答", "创造轻松的阅读氛围"]
        )
