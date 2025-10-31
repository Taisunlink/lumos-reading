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
from .emotional_regulation import EmotionalRegulationFramework

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
    emotional_development: Optional[Dict[str, Any]] = None  # 情绪发展框架

class PsychologyExpert:
    """
    心理学专家Agent - 基于Claude
    专注于认知发展理论和神经多样性支持
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=config.anthropic_api_key)
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        self.cost_tracker = CostTracker(self.redis_client)
        self.emotional_framework = EmotionalRegulationFramework()

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

            # 新增：情绪发展框架生成
            emotional_framework = self.emotional_framework.generate_story_emotional_framework(
                child_profile,
                story_request
            )

            # 整合到教育框架中
            framework.emotional_development = emotional_framework
            
            # 将情绪调节的交互提示整合到CROWD策略中
            if emotional_framework.get('interaction_prompts'):
                for prompt in emotional_framework['interaction_prompts']:
                    if prompt['type'] == 'Completion':
                        framework.crowd_strategy.completion_prompts.append(prompt['prompt'])
                    elif prompt['type'] == 'Recall':
                        framework.crowd_strategy.recall_questions.append(prompt['prompt'])
                    elif prompt['type'] == 'Open_ended':
                        framework.crowd_strategy.open_ended_prompts.append(prompt['prompt'])

            # 缓存结果
            if config.enable_framework_cache:
                await self._cache_framework(cache_key, framework)

            # 记录成本
            await self.cost_tracker.record_usage(
                model=config.psychology_model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )

            logger.info(f"Generated framework with emotional support for child age {child_profile.get('age', 'unknown')}")
            return framework

        except Exception as e:
            logger.error(f"Framework generation failed: {str(e)}")
            # 返回基础框架作为后备
            return await self._get_fallback_framework(child_profile)

    # ========== 辅助方法：用于构建详细的心理学prompt ==========

    def _explain_plot_structure(self, structure_type: str) -> str:
        """解释情节结构类型"""
        explanations = {
            "single_linear": "单一主线，按时间顺序发展，因果关系直接明显",
            "dual_thread_simple": "两条故事线，简单交织，最后汇合",
            "multi_thread_complex": "多条故事线并行发展，复杂交织，多层伏笔"
        }
        return explanations.get(structure_type, structure_type)

    def _explain_time_structure(self, time_type: str) -> str:
        """解释时间结构"""
        explanations = {
            "linear_only": "纯线性时间，从头到尾顺序讲述",
            "linear_with_flashback": "主要线性，可以有1-2处简短回忆",
            "nonlinear_allowed": "允许倒叙、插叙、时间跳跃、多时空并行"
        }
        return explanations.get(time_type, time_type)

    def _explain_cause_effect(self, pattern: str) -> str:
        """解释因果关系模式"""
        explanations = {
            "immediate": "因果直接相连，A导致B立即发生",
            "delayed_single_step": "因果之间可以延迟一个事件，A→C→B",
            "complex_chain": "复杂因果链，多因多果，长链条因果关系"
        }
        return explanations.get(pattern, pattern)

    def _format_vocabulary_enrichment(self, enrichment: Dict) -> str:
        """格式化词汇丰富策略"""
        if not enrichment:
            return ""

        parts = []
        if 'new_words_per_story' in enrichment:
            nw = enrichment['new_words_per_story']
            parts.append(f"- 新词引入: 每个故事{nw.get('min', 0)}-{nw.get('max', 0)}个")
        if 'idioms_per_story' in enrichment:
            idioms = enrichment['idioms_per_story']
            if isinstance(idioms, dict):
                parts.append(f"- 成语使用: {idioms.get('min', 0)}-{idioms.get('max', 0)}个")
            elif idioms > 0:
                parts.append(f"- 成语使用: {idioms}个")
        if enrichment.get('metaphor_usage'):
            parts.append(f"- 比喻手法: {enrichment['metaphor_usage']}")

        return "\n".join(parts)

    def _format_moral_dilemma(self, dilemma_type: str) -> str:
        """格式化道德困境指导"""
        if dilemma_type == "simple_binary":
            return "\n- **道德选择**: 简单的对错判断(如: 诚实vs撒谎)"
        elif dilemma_type == "complex_gradient":
            return "\n- **道德困境**: 复杂的渐变判断，没有绝对对错，需权衡多方利益"
        return ""

    def _format_critical_thinking(self, critical: Dict) -> str:
        """格式化批判性思维要求"""
        if not critical:
            return ""

        parts = ["\n### 六、批判性思维培养"]
        if critical.get('perspective_taking'):
            parts.append("- 引导多视角思考: 从不同角色立场理解事件")
        if critical.get('cause_analysis') == 'multi_factor':
            parts.append("- 多因素分析: 探讨事件的多重原因")
        if critical.get('prediction_questions'):
            parts.append("- 预测性提问: 鼓励推测后续发展")
        if critical.get('ethical_discussion'):
            parts.append("- 伦理讨论: 探讨价值观和道德选择")

        return "\n".join(parts)

    def _get_common_char_threshold(self, percentage: int) -> int:
        """根据百分比返回常用字数量"""
        if percentage >= 95:
            return 500
        elif percentage >= 80:
            return 1500
        else:
            return 3000

    # ========== 重写的Psychology Prompt构建方法 ==========

    async def _build_psychology_prompt(
        self,
        child_profile: Dict[str, Any],
        story_request: Dict[str, Any]
    ) -> str:
        """构建科学细致的心理学提示词 - 基于年龄参数"""

        age = child_profile.get('age', 5)

        # 导入年龄参数
        from agents.psychology.age_parameters import AgeGroupParameters
        params = AgeGroupParameters.get_parameters(age)

        neuro_profile = child_profile.get('neuro_profile', {})
        preferences = child_profile.get('preferences', {})
        theme = story_request.get('theme', '友谊')

        prompt = f"""
你是哈佛大学儿童发展心理学教授，专精皮亚杰和维果茨基理论，拥有20年临床经验。

## 儿童认知档案
- **年龄**: {age}岁
- **认知阶段**: {params['cognitive_stage']}
- **皮亚杰特征**: {', '.join(params['piaget_characteristics'])}
- **神经多样性**: {json.dumps(neuro_profile, ensure_ascii=False) if neuro_profile else '无特殊需求'}
- **阅读偏好**: {json.dumps(preferences, ensure_ascii=False) if preferences else '暂无数据'}

## 故事主题
{theme}

## 你的任务
基于 **{params['age_range']}** 儿童的认知发展水平，设计精确的教育心理学框架。

---

### 一、内容结构设计 (精确到数字！)

**页数规划**:
- 最少: {params['page_count']['min']}页
- 最多: {params['page_count']['max']}页
- **推荐**: {params['page_count']['recommended']}页 ← 必须采用此值！

**每页字数**:
- 最少: {params['words_per_page']['min']}字
- 最多: {params['words_per_page']['max']}字
- **推荐**: {params['words_per_page']['recommended']}字 ← 必须采用此值！

**总字数**: 约 {params['total_story_length']['recommended']}字

---

### 二、语言复杂度设计 (句句必符合！)

#### 句式结构分布 (严格百分比):
```
简单句 (主谓宾/主系表): {params['sentence_structure']['simple_sentences']}%
复合句 (因果/转折/并列): {params['sentence_structure']['compound_sentences']}%
复杂句 (多层从句/倒装): {params['sentence_structure']['complex_sentences']}%
```

#### 句子长度控制:
- 平均每句: {params['sentence_length']['avg']}字
- 最短: {params['sentence_length']['min']}字
- 最长: {params['sentence_length']['max']}字

#### 词汇难度分布:
```
常用字 (前{self._get_common_char_threshold(params['vocabulary_level']['common_chars'])}字表): {params['vocabulary_level']['common_chars']}%
进阶词 (成语/多义词/书面语): {params['vocabulary_level']['intermediate_chars']}%
高级词 (抽象概念/专业术语): {params['vocabulary_level']['advanced_chars']}%
```

{self._format_vocabulary_enrichment(params.get('vocabulary_enrichment', {}))}

---

### 三、情节复杂度设计 (结构清晰！)

**叙事结构**: {params['plot_structure']}
→ {self._explain_plot_structure(params['plot_structure'])}

**情节点数量**: {params['plot_points']['min']}-{params['plot_points']['max']}个关键转折

**角色设计**:
- 角色总数: {params['character_count']['min']}-{params['character_count']['max']}个
- 主角: 1个 (必须有成长弧线)
- 配角: {params['character_count']['min']-1}-{params['character_count']['max']-1}个

**时间结构**: {params['time_structure']}
→ {self._explain_time_structure(params['time_structure'])}

**因果关系**: {params['cause_effect_directness']}
→ {self._explain_cause_effect(params['cause_effect_directness'])}

**冲突类型**: {', '.join(params['conflict_types'])}

---

### 四、主题深度设计 (触及心灵！)

**复杂度级别**: {params['theme_complexity']}

**适合主题**: {', '.join(params['suitable_themes'][:5])} (可从中选择)

**情绪调色板**: {', '.join(params['emotion_types'])}
→ 故事必须自然展现这些情绪，通过情节和对话体现

{self._format_moral_dilemma(params.get('moral_dilemma', ''))}

---

### 五、CROWD对话式阅读策略 (互动设计！)

**互动频率**: {params['crowd_frequency']}

**类型分布**:
- Completion (完成句子): {params['crowd_types_distribution']['Completion']}%
- Recall (回忆问题): {params['crowd_types_distribution']['Recall']}%
- Open-ended (开放讨论): {params['crowd_types_distribution']['Open_ended']}%
- Wh-questions (为什么/怎么): {params['crowd_types_distribution']['Wh_questions']}%
- Distancing (联系生活): {params['crowd_types_distribution']['Distancing']}%

**示例参考**:
{json.dumps(params.get('interaction_examples', {}), ensure_ascii=False, indent=2)}

{self._format_critical_thinking(params.get('critical_thinking', {}))}

---

## 输出格式 (严格JSON)

请输出完整的教育框架JSON，所有数值必须严格遵守上述标准！

```json
{{
    "age_group": "{params['age_range']}",
    "cognitive_stage": "{params['cognitive_stage']}",
    "attention_span_target": {max(3, age)},

    "content_structure": {{
        "page_count": {params['page_count']['recommended']},
        "words_per_page": {params['words_per_page']['recommended']},
        "total_words": {params['total_story_length']['recommended']}
    }},

    "language_specifications": {{
        "sentence_structure": {json.dumps(params['sentence_structure'])},
        "sentence_length": {json.dumps(params['sentence_length'])},
        "vocabulary_level": {json.dumps(params['vocabulary_level'])},
        "vocabulary_enrichment": {json.dumps(params.get('vocabulary_enrichment', {}))},
        "example_sentences": [
            "示例1: 符合句式和长度要求的句子",
            "示例2: ...",
            "示例3: ..."
        ]
    }},

    "plot_specifications": {{
        "structure_type": "{params['plot_structure']}",
        "plot_points": {(params['plot_points']['min'] + params['plot_points']['max']) // 2},
        "character_count": {(params['character_count']['min'] + params['character_count']['max']) // 2},
        "time_structure": "{params['time_structure']}",
        "cause_effect_pattern": "{params['cause_effect_directness']}",
        "conflict_types": {json.dumps(params.get('conflict_types', []))}
    }},

    "theme_specifications": {{
        "complexity_level": "{params['theme_complexity']}",
        "recommended_theme": "基于'{theme}'具体化的主题描述",
        "emotion_palette": {json.dumps(params['emotion_types'])},
        "educational_goals": ["具体学习目标1", "具体学习目标2", "具体学习目标3"]
    }},

    "crowd_strategy": {{
        "frequency": "{params['crowd_frequency']}",
        "distribution": {json.dumps(params['crowd_types_distribution'])},
        "completion_prompts": ["具体互动提示5-8个"],
        "recall_questions": ["具体回忆问题5-8个"],
        "open_ended_prompts": ["开放性讨论5-8个"],
        "wh_questions": ["为什么/怎么问题5-8个"],
        "distancing_connections": ["联系生活的引导5-8个"]
    }},

    "neuro_adaptations": {{
        "attention_supports": {{}},
        "sensory_adjustments": {{}},
        "interaction_modifications": {{}},
        "cognitive_scaffolding": {{}}
    }},

    "safety_considerations": [
        "心理安全要点1",
        "心理安全要点2"
    ],

    "parent_guidance": [
        "家长引导建议1",
        "家长引导建议2"
    ]
}}
```

**关键提醒**:
1. 页数、字数必须是推荐值，不要偏离！
2. 句式结构百分比必须精确匹配！
3. 所有CROWD互动必须给出5-8个具体示例！
4. 示例句子必须符合该年龄段的句长和复杂度要求！

现在开始设计框架！
"""

        # 神经多样性额外指导
        if neuro_profile.get('adhd_indicators'):
            prompt += """

## ADHD专项适配
- 每3-5页设置一个明显的"里程碑"奖励点
- 使用视觉锚点(图标/颜色)标记重要内容
- 句子短小精悍，避免长难句
- 提供明确的进度指示
"""

        if neuro_profile.get('autism_indicators'):
            prompt += """

## 自闭谱系专项适配
- 保持视觉风格高度一致
- 情绪变化需要明确标注("小明感到开心")
- 提供可预测的故事结构(开始-中间-结束明确)
- 避免突然的场景转换，需要过渡提示
"""

        return prompt

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
        
        # 生成基础情绪框架
        emotional_framework = self.emotional_framework.generate_story_emotional_framework(
            child_profile,
            {"theme": "友谊", "conflicts": []}
        )
        
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
            parent_guidance=["鼓励孩子表达想法", "耐心倾听孩子的回答", "创造轻松的阅读氛围"],
            emotional_development=emotional_framework
        )
