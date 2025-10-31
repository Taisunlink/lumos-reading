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
from .rhythm_analyzer import ChineseRhythmAnalyzer

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
        self.rhythm_analyzer = ChineseRhythmAnalyzer()
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

            # ✅ P1-3: 增强插图提示词（5要素详细化）
            overall_style = user_preferences.get('illustration_style', {}) if user_preferences else {}
            if not overall_style:
                overall_style = {
                    'illustration_style': 'watercolor',
                    'color_palette': 'warm and bright'
                }

            for page in story_content.pages:
                # 增强每页的插图提示词
                enhanced_prompt = self.enhance_illustration_prompt_for_page(
                    page_text=page.text,
                    page_number=page.page_number,
                    characters=story_content.characters,
                    overall_style=overall_style,
                    age_group=framework.age_group
                )
                # 将增强后的提示词与原提示词结合
                if page.illustration_prompt:
                    page.illustration_prompt = f"{page.illustration_prompt} {enhanced_prompt}"
                else:
                    page.illustration_prompt = enhanced_prompt

            logger.info(f"Enhanced illustration prompts for {len(story_content.pages)} pages")

            # 文学质量自检
            quality_report = await self._literature_quality_check(story_content, framework)

            # 如需改进则自动优化
            if quality_report.needs_revision:
                story_content = await self._revise_content(story_content, quality_report)
                # 再次质量检查
                quality_report = await self._literature_quality_check(story_content, framework)

            # 韵律质量检查
            target_age = framework.age_group
            full_text = ' '.join(page.text for page in story_content.pages)
            rhythm_score = self.rhythm_analyzer.analyze_text_rhythm(full_text, target_age)
            
            # 综合质量评分（原有质量 + 韵律质量）
            combined_quality_score = (
                quality_report.overall_score * 0.7 +
                rhythm_score.overall_score * 0.3
            )
            
            # 记录质量分数
            story_content.educational_value_score = combined_quality_score
            
            # 添加韵律分析元数据
            story_content.language_complexity_level = self._determine_language_complexity(rhythm_score, target_age)

            logger.info(f"Story created: {story_content.title}, Quality: {combined_quality_score:.2f}, Rhythm: {rhythm_score.overall_score:.2f}")
            return story_content

        except Exception as e:
            logger.error(f"Story creation failed: {str(e)}")
            # 返回模板故事作为后备
            return await self._get_template_story(theme, framework)

    # ========== 辅助方法：用于构建详细的文学创作prompt ==========

    def _generate_example_sentences(self, language_spec: Dict, age_group: str) -> str:
        """根据语言规格生成示例句子"""
        examples = []

        if "3-5" in age_group:
            examples = [
                "小兔子在花园里跳。(6字简单句)",
                "它看到了一只蝴蝶。(8字简单句)",
                "小兔子想和蝴蝶玩，但是蝴蝶飞走了。(16字复合句)"
            ]
        elif "6-8" in age_group:
            examples = [
                "小明和朋友们一起玩耍，他们非常开心。(15字复合句)",
                "虽然遇到了困难，但是大家互相帮助，最后解决了问题。(22字复杂句)",
                "这个故事告诉我们，真正的友谊需要互相理解和包容。(21字复杂句)"
            ]
        else:  # 9-11
            examples = [
                "十二岁的林晓站在阁楼的窗前，望着窗外淅淅沥沥的雨，心中涌起一股说不清的情绪。(32字复杂句)",
                "她知道，今天的选择将会改变很多事情，但她还是决定勇敢地迈出那一步。(29字复杂句)",
                "当她打开那扇尘封已久的木箱时，一个全新的世界在她眼前徐徐展开。(28字复杂句)"
            ]

        return "\n".join([f"   {ex}" for ex in examples])

    def _format_plot_point_guidance(self, plot_points: int, page_count: int) -> str:
        """生成情节点布局指导"""
        if plot_points <= 5:
            # 简单结构
            return f"""
第1页: 开篇引入 (介绍主角和环境)
第{page_count // 3}页左右: 问题出现
第{page_count // 2}页左右: 尝试解决
第{page_count * 2 // 3}页左右: 高潮转折
第{page_count}页: 圆满结局
"""
        elif plot_points <= 8:
            # 中等复杂度
            return f"""
第1-2页: 开篇引入 (主角、环境、日常)
第{page_count // 4}页: 冲突出现
第{page_count // 3}页: 第一次尝试
第{page_count // 2}页: 遇到挫折
第{page_count * 2 // 3}页: 关键发现/转机
第{page_count * 3 // 4}页: 高潮对决
第{page_count - 1}页: 问题解决
第{page_count}页: 升华主题
"""
        else:
            # 复杂结构
            return f"""
第1-3页: 多线索开篇 (主角、环境、伏笔)
第{page_count // 5}页: A线冲突
第{page_count // 4}页: B线引入
第{page_count // 3}页: 双线交织
第{page_count // 2}页: 重大挫折
第{page_count * 2 // 3}页: 关键线索
第{page_count * 3 // 4}页: 真相揭露
第{page_count * 4 // 5}页: 高潮冲突
第{page_count - 2}页: 余波处理
第{page_count}页: 深层主题升华
"""

    def _generate_illustration_5_elements_guide(self) -> str:
        """生成5要素插图指导"""
        return """
**插图5要素结构** (每页必须完整包含):

1. 场景 (Scene): 地点、时间(早晨/午后/夜晚)、天气、光线
   示例: "温暖的午后阳光洒在森林空地上，微风轻拂"

2. 角色 (Characters): 外貌、姿态、表情、服装 (必须与角色圣经一致!)
   示例: "小兔子(白色毛发，粉色长耳朵，大眼睛，穿蓝色背心)"

3. 动作 (Actions): 正在做什么，动态感
   示例: "正跳跃着追逐五彩蝴蝶，耳朵随风飘动"

4. 情绪 (Emotions): 通过表情和肢体语言传达
   示例: "表情充满好奇和快乐，眼睛里闪烁着兴奋的光芒"

5. 艺术风格 (Art Style): 画风、色调、构图、儿童友好性
   示例: "水彩插画风格，柔和明亮的暖色调，画面温馨，适合3-5岁儿童，无任何恐怖元素"

**完整示例**:
"温暖的午后阳光洒在森林空地上，小兔子(白色毛发，粉色长耳朵，大眼睛，穿蓝色背心)正跳跃着追逐五彩蝴蝶，表情充满好奇和快乐，眼睛里闪烁着兴奋的光芒。背景是翠绿的树木和五彩的野花。水彩插画风格，柔和明亮的暖色调，画面温馨，适合3-5岁儿童，无任何恐怖元素。"
"""

    def _generate_crowd_embedding_guide(self, crowd_strategy, page_count: int) -> str:
        """生成CROWD互动嵌入指导"""
        frequency = crowd_strategy.frequency if hasattr(crowd_strategy, 'frequency') else "每2页一次"
        distribution = crowd_strategy.distribution if hasattr(crowd_strategy, 'distribution') else {}

        return f"""
**CROWD互动嵌入规则**:

**频率**: {frequency}
**分布**: {json.dumps(distribution, ensure_ascii=False)}

**具体嵌入方案** (共{page_count}页):
{self._calculate_crowd_distribution(page_count, distribution)}

**每种类型的具体示例**:
- Completion: "{', '.join(crowd_strategy.completion_prompts[:3])}"
- Recall: "{', '.join(crowd_strategy.recall_questions[:3])}"
- Open_ended: "{', '.join(crowd_strategy.open_ended_prompts[:3])}"
- Wh_questions: "{', '.join(crowd_strategy.wh_questions[:3])}"
- Distancing: "{', '.join(crowd_strategy.distancing_connections[:3])}"

**重要**: 互动提示必须与当页内容紧密结合，自然流畅！
"""

    def _calculate_crowd_distribution(self, page_count: int, distribution: Dict) -> str:
        """计算CROWD在各页的分布"""
        if not distribution:
            return "均匀分布在各页"

        # 简化实现：建议在哪些页放哪种类型
        pages_with_crowd = []
        page_interval = max(1, page_count // 10)  # 每几页一个互动

        for i in range(1, page_count + 1, page_interval):
            if i <= page_count * 0.2:
                pages_with_crowd.append(f"第{i}页: Completion 或 Recall")
            elif i <= page_count * 0.5:
                pages_with_crowd.append(f"第{i}页: Wh_questions")
            elif i <= page_count * 0.8:
                pages_with_crowd.append(f"第{i}页: Open_ended 或 Distancing")
            else:
                pages_with_crowd.append(f"第{i}页: Recall 或 Open_ended")

        return "\n".join(pages_with_crowd)

    # ========== 重写的Literature Prompt构建方法 ==========

    async def _build_literature_prompt(
        self,
        framework: EducationalFramework,
        theme: str,
        series_bible: Optional[Dict],
        user_preferences: Optional[Dict]
    ) -> str:
        """构建科学精确的儿童文学创作提示词 - 基于教育框架"""

        # 从framework提取精确参数
        content_spec = framework.content_structure if hasattr(framework, 'content_structure') else {}
        language_spec = framework.language_specifications if hasattr(framework, 'language_specifications') else {}
        plot_spec = framework.plot_specifications if hasattr(framework, 'plot_specifications') else {}
        theme_spec = framework.theme_specifications if hasattr(framework, 'theme_specifications') else {}

        # 如果没有新格式，使用旧参数
        if not content_spec:
            content_spec = {
                'page_count': 12,
                'words_per_page': self._get_word_count_by_age(framework.age_group),
                'total_words': 12 * self._get_word_count_by_age(framework.age_group)
            }
        if not language_spec:
            language_spec = {
                'sentence_structure': {'simple_sentences': 70, 'compound_sentences': 25, 'complex_sentences': 5},
                'sentence_length': {'min': 6, 'max': 12, 'avg': 9}
            }
        if not plot_spec:
            plot_spec = {
                'structure_type': 'single_linear',
                'plot_points': 5,
                'character_count': 3
            }

        page_count = content_spec.get('page_count', 12)
        words_per_page = content_spec.get('words_per_page', 30)
        plot_points = plot_spec.get('plot_points', 5)

        # 构建详细的创作prompt
        prompt = f"""
你是曹文轩、秦文君级别的中国儿童文学作家，国际安徒生奖得主。

## 创作任务
**主题**: {theme}
**认知阶段**: {framework.cognitive_stage}
**目标年龄**: {framework.age_group}
**学习目标**: {', '.join(framework.learning_objectives)}

---

## 严格执行的创作参数 (不可违背！)

### 一、内容结构 (精确到数字)

**总页数**: 必须是 **{page_count}页** (不多不少!)

**每页字数**: 平均 **{words_per_page}字** (允许±10%, 即{int(words_per_page*0.9)}-{int(words_per_page*1.1)}字)

**故事总字数**: 约 **{content_spec.get('total_words', page_count * words_per_page)}字**

---

### 二、语言规格 (句句必查!)

#### 句式结构严格分布：
```
简单句: {language_spec.get('sentence_structure', {}).get('simple_sentences', 70)}%
复合句: {language_spec.get('sentence_structure', {}).get('compound_sentences', 25)}%
复杂句: {language_spec.get('sentence_structure', {}).get('complex_sentences', 5)}%
```

**如何统计**: 每创作完一页，立即统计该页的句式分布，确保符合比例！

#### 句子长度控制：
- **平均**: {language_spec.get('sentence_length', {}).get('avg', 9)}字/句
- **最短不少于**: {language_spec.get('sentence_length', {}).get('min', 6)}字
- **最长不超过**: {language_spec.get('sentence_length', {}).get('max', 12)}字

#### 示例句子 (严格模仿这个复杂度！):
{self._generate_example_sentences(language_spec, framework.age_group)}

#### 词汇难度要求：
{json.dumps(language_spec.get('vocabulary_level', {}), ensure_ascii=False, indent=2)}

---

### 三、情节设计 (结构清晰!)

**叙事结构**: {plot_spec.get('structure_type', 'single_linear')}

**情节点数量**: {plot_points}个关键转折

**情节点布局建议**:
{self._format_plot_point_guidance(plot_points, page_count)}

**角色设计**: {plot_spec.get('character_count', 3)}个角色
- 主角1个: 必须有成长弧线(开始→挑战→转变→成长)
- 配角{plot_spec.get('character_count', 3)-1}个: 推动情节发展，各有特点

**时间结构**: {plot_spec.get('time_structure', 'linear_only')}

**因果关系**: {plot_spec.get('cause_effect_pattern', 'immediate')}

---

### 四、插图描述 (每页必须包含5要素!)

{self._generate_illustration_5_elements_guide()}

---

### 五、CROWD互动嵌入

{self._generate_crowd_embedding_guide(framework.crowd_strategy, page_count)}

---

### 六、主题与情绪

**主题复杂度**: {theme_spec.get('complexity_level', '适龄')}

**情绪调色板**: 必须涵盖 {', '.join(theme_spec.get('emotion_palette', ['开心', '难过', '勇敢']))}

**教育目标**: {', '.join(theme_spec.get('educational_goals', ['传递正向价值']))}

---

### 七、文化价值观

- 体现中华文化优秀传统
- 传递积极正面的人生观
- 包容性和多样性
- 无性别刻板印象
- 尊重不同家庭结构

---

## JSON输出格式 (严格执行!)

```json
{{
    "title": "富有吸引力的故事标题",
    "moral_theme": "故事传达的核心价值",
    "pages": [
        {{
            "page_number": 1,
            "text": "正文({words_per_page}字左右，严格控制句长和句式)",
            "illustration_prompt": "完整5要素插图描述(场景+角色+动作+情绪+风格)",
            "crowd_prompt": {{
                "type": "Completion|Recall|Open_ended|Wh_questions|Distancing",
                "text": "与本页内容紧密结合的互动提示"
            }},
            "reading_time_seconds": 估算秒数,
            "word_count": 实际字数,
            "sentence_count": 句子数量,
            "complexity_check": {{
                "simple_sentences": 简单句数量,
                "compound_sentences": 复合句数量,
                "complex_sentences": 复杂句数量
            }}
        }},
        ...共{page_count}页
    ],
    "characters": [
        {{
            "name": "角色名字",
            "description": "详细背景故事",
            "personality": "性格特征(3-5个形容词)",
            "visual_description": "外貌详细描述(发型、眼睛、肤色、身高、服装、特征)",
            "role_in_story": "在故事中的作用",
            "character_arc": "成长变化(主角必填)"
        }}
    ],
    "vocabulary_targets": ["重点词汇15-25个"],
    "extension_activities": ["亲子活动建议3-5个"],
    "cultural_elements": ["文化元素3-5个"],
    "quality_self_assessment": {{
        "language_complexity_match": "是否符合{framework.age_group}(是/否/原因)",
        "plot_point_count": {plot_points},
        "actual_page_count": 实际页数,
        "avg_words_per_page": 实际平均字数,
        "sentence_structure_distribution": "实际百分比",
        "emotion_coverage": "涵盖的情绪种类",
        "self_score": "自评分数(1-10)"
    }}
}}
```

---

## 创作前自检清单 (请逐项确认!)

在开始创作前，你必须确认：
- [ ] 我理解了{framework.age_group}儿童的认知特点
- [ ] 我记住了{page_count}页的精确页数要求
- [ ] 我清楚{words_per_page}字/页的字数要求
- [ ] 我理解句式结构的百分比分布
- [ ] 我知道句子长度的控制标准
- [ ] 我规划好了{plot_points}个情节点的位置
- [ ] 我准备好了{plot_spec.get('character_count', 3)}个有血有肉的角色
- [ ] 我明白插图必须包含完整5要素
- [ ] 我清楚CROWD互动的嵌入要求

---

## 重要提醒

1. **每创作完一页，立即检查字数和句式是否符合要求！**
2. **插图描述必须详细，至少100字，包含完整5要素！**
3. **CROWD互动必须与内容紧密结合，不能生硬！**
4. **最后的quality_self_assessment必须诚实填写！**

**现在开始创作！严格按照以上所有参数执行！**
"""

        # 神经多样性适配
        if framework.neuro_adaptations:
            prompt += f"""

---

## 神经多样性友好设计

{self._format_neuro_adaptations(framework.neuro_adaptations)}
"""

        # Series Bible一致性要求
        if series_bible:
            prompt += f"""

---

## 系列一致性要求

**固定角色**:
{json.dumps(series_bible.get('characters', []), ensure_ascii=False, indent=2)}

**世界观**: {json.dumps(series_bible.get('world_settings', {}), ensure_ascii=False)}

**视觉风格**: {series_bible.get('visual_style', '保持统一')}

**重要**: 新故事必须与已有设定保持一致，角色外貌、性格不能改变！
"""

        # 用户偏好
        if user_preferences:
            prompt += f"""

---

## 用户偏好

{json.dumps(user_preferences, ensure_ascii=False, indent=2)}
"""

        return prompt

    def _get_word_count_by_age(self, age_group: str) -> int:
        """根据年龄组确定每页字数 - 使用科学参数"""
        # 导入年龄参数
        from agents.psychology.age_parameters import AgeGroupParameters

        # 从age_group提取年龄 (例如 "3-5" -> 4)
        if "3-5" in age_group:
            age = 4
        elif "6-8" in age_group:
            age = 7
        elif "9-11" in age_group:
            age = 10
        else:
            age = 6  # 默认6岁

        params = AgeGroupParameters.get_parameters(age)
        return params['words_per_page']['recommended']

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

    def _determine_language_complexity(self, rhythm_score, target_age: str) -> str:
        """根据韵律评分确定语言复杂度"""
        if target_age == '3-5':
            if rhythm_score.overall_score >= 0.8:
                return "简单优美"
            elif rhythm_score.overall_score >= 0.6:
                return "简单"
            else:
                return "需要优化"
        elif target_age == '6-8':
            if rhythm_score.overall_score >= 0.8:
                return "适中优美"
            elif rhythm_score.overall_score >= 0.6:
                return "适中"
            else:
                return "需要优化"
        else:  # 9-11
            if rhythm_score.overall_score >= 0.8:
                return "丰富优美"
            elif rhythm_score.overall_score >= 0.6:
                return "丰富"
            else:
                return "需要优化"

    async def analyze_story_rhythm(self, story_text: str, target_age: str) -> Dict[str, Any]:
        """分析故事韵律质量"""
        try:
            rhythm_score = self.rhythm_analyzer.analyze_text_rhythm(story_text, target_age)
            return {
                "overall_score": rhythm_score.overall_score,
                "rhythm_consistency": rhythm_score.rhythm_consistency,
                "tone_harmony": rhythm_score.tone_harmony,
                "reading_flow": rhythm_score.reading_flow,
                "age_appropriateness": rhythm_score.age_appropriateness,
                "improvement_suggestions": rhythm_score.improvement_suggestions
            }
        except Exception as e:
            logger.error(f"Rhythm analysis failed: {str(e)}")
            return {
                "overall_score": 0.5,
                "rhythm_consistency": 0.5,
                "tone_harmony": 0.5,
                "reading_flow": 0.5,
                "age_appropriateness": 0.5,
                "improvement_suggestions": ["韵律分析失败，建议人工检查"]
            }

    # ========== P1-3: 插图提示词增强方法 ==========

    def _extract_scene_elements(self, page_text: str) -> Dict[str, str]:
        """从页面文本中提取场景元素"""
        scene = {
            "location": "室内",
            "time_of_day": "白天",
            "weather": "晴朗",
            "lighting": "明亮温暖"
        }

        # 地点关键词
        if any(word in page_text for word in ["森林", "树", "草地"]):
            scene["location"] = "森林空地"
        elif any(word in page_text for word in ["家", "房间", "屋子"]):
            scene["location"] = "温馨的家中"
        elif any(word in page_text for word in ["学校", "教室", "操场"]):
            scene["location"] = "学校"
        elif any(word in page_text for word in ["公园", "花园"]):
            scene["location"] = "公园"
        elif any(word in page_text for word in ["海边", "沙滩"]):
            scene["location"] = "海边"

        # 时间关键词
        if any(word in page_text for word in ["早晨", "清晨", "太阳升起"]):
            scene["time_of_day"] = "清晨"
        elif any(word in page_text for word in ["中午", "正午"]):
            scene["time_of_day"] = "中午"
        elif any(word in page_text for word in ["傍晚", "夕阳", "日落"]):
            scene["time_of_day"] = "傍晚"
        elif any(word in page_text for word in ["夜晚", "晚上", "月亮", "星星"]):
            scene["time_of_day"] = "夜晚"

        # 天气关键词
        if any(word in page_text for word in ["雨", "下雨"]):
            scene["weather"] = "雨天"
            scene["lighting"] = "柔和阴沉"
        elif any(word in page_text for word in ["雪", "下雪"]):
            scene["weather"] = "雪天"
        elif any(word in page_text for word in ["风", "大风"]):
            scene["weather"] = "有风"
        elif any(word in page_text for word in ["阴天", "云"]):
            scene["weather"] = "多云"

        return scene

    def _extract_character_actions(self, page_text: str, characters: List[Character]) -> Dict[str, str]:
        """从页面文本中提取角色动作"""
        actions = {}

        # 动作关键词映射
        action_keywords = {
            "跳": "跳跃",
            "跑": "奔跑",
            "走": "行走",
            "坐": "坐着",
            "站": "站立",
            "笑": "微笑",
            "哭": "哭泣",
            "玩": "玩耍",
            "看": "观察",
            "听": "倾听",
            "说": "说话",
            "唱": "唱歌",
            "跳舞": "跳舞",
            "画": "绘画",
            "读": "阅读",
            "写": "书写",
            "吃": "进食",
            "睡": "休息",
            "追": "追逐",
            "躲": "躲藏",
            "抱": "拥抱",
            "握": "握手",
            "挥": "挥手"
        }

        for character in characters:
            char_name = character.name
            # 检查该角色是否在这页出现
            if char_name in page_text:
                # 提取该角色附近的动作
                for keyword, action in action_keywords.items():
                    if keyword in page_text:
                        # 简单启发式：如果角色名和动作词在同一句话
                        sentences = re.split('[。！？]', page_text)
                        for sentence in sentences:
                            if char_name in sentence and keyword in sentence:
                                actions[char_name] = action
                                break

                # 如果没找到动作，默认为"在场景中"
                if char_name not in actions:
                    actions[char_name] = "在场景中"

        return actions

    def _extract_emotions(self, page_text: str) -> Dict[str, str]:
        """从页面文本中提取情绪"""
        emotions = {}

        # 情绪关键词
        emotion_keywords = {
            "开心": ["开心", "高兴", "快乐", "喜悦", "兴奋", "笑"],
            "难过": ["难过", "伤心", "悲伤", "哭"],
            "生气": ["生气", "愤怒", "恼火"],
            "害怕": ["害怕", "恐惧", "担心", "紧张"],
            "惊讶": ["惊讶", "吃惊", "震惊"],
            "好奇": ["好奇", "疑惑", "想知道"],
            "勇敢": ["勇敢", "勇气", "不怕"],
            "温暖": ["温暖", "温馨", "舒服"],
            "感动": ["感动", "感激", "谢谢"],
            "骄傲": ["骄傲", "自豪"],
            "羞愧": ["羞愧", "不好意思", "脸红"]
        }

        detected_emotions = []
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in page_text for keyword in keywords):
                detected_emotions.append(emotion)

        # 返回主要情绪
        if detected_emotions:
            emotions["primary"] = detected_emotions[0]
            if len(detected_emotions) > 1:
                emotions["secondary"] = ", ".join(detected_emotions[1:3])
        else:
            emotions["primary"] = "平静"

        return emotions

    def _determine_overall_emotion(self, emotions: Dict[str, str]) -> str:
        """确定整体情绪氛围"""
        primary = emotions.get("primary", "平静")

        atmosphere_map = {
            "开心": "欢快愉悦的氛围，充满正能量",
            "难过": "略带忧伤的氛围，但不过分沉重",
            "生气": "紧张的氛围，但适合儿童理解",
            "害怕": "略显紧张的氛围，但不恐怖",
            "惊讶": "充满惊喜的氛围",
            "好奇": "探索发现的氛围",
            "勇敢": "鼓舞人心的氛围",
            "温暖": "温馨和谐的氛围",
            "感动": "感人至深的氛围",
            "骄傲": "积极自信的氛围",
            "羞愧": "反思成长的氛围",
            "平静": "平和温馨的氛围"
        }

        return atmosphere_map.get(primary, "温馨友好的氛围")

    def enhance_illustration_prompt_for_page(
        self,
        page_text: str,
        page_number: int,
        characters: List[Character],
        overall_style: Dict[str, Any],
        age_group: str
    ) -> str:
        """
        为每页生成5要素详细插图提示词

        Args:
            page_text: 页面文本内容
            page_number: 页码
            characters: 角色列表
            overall_style: 整体风格配置
            age_group: 目标年龄组

        Returns:
            完整的5要素插图提示词
        """

        # 1. 提取场景元素
        scene = self._extract_scene_elements(page_text)

        # 2. 提取角色动作
        actions = self._extract_character_actions(page_text, characters)

        # 3. 提取情绪
        emotions = self._extract_emotions(page_text)

        # 4. 构建5要素提示词
        prompt_parts = []

        # 要素1: 场景描述
        scene_desc = (
            f"{scene['time_of_day']}的{scene['weather']}，"
            f"在{scene['location']}，"
            f"{scene['lighting']}的光线"
        )
        prompt_parts.append(f"场景: {scene_desc}")

        # 要素2: 角色描述（保持视觉一致性）
        character_descs = []
        for character in characters:
            if character.name in page_text:
                action = actions.get(character.name, "在场景中")
                char_desc = (
                    f"{character.name}（{character.visual_description}）"
                    f"正在{action}"
                )
                character_descs.append(char_desc)

        if character_descs:
            prompt_parts.append(f"角色: {'; '.join(character_descs)}")

        # 要素3: 动作描述
        if actions:
            action_list = [f"{name}正在{action}" for name, action in actions.items()]
            prompt_parts.append(f"动作: {', '.join(action_list)}")

        # 要素4: 情绪氛围
        emotion_desc = self._determine_overall_emotion(emotions)
        primary_emotion = emotions.get("primary", "平静")
        prompt_parts.append(f"情绪: 角色表现出{primary_emotion}的情绪，{emotion_desc}")

        # 要素5: 艺术风格（根据年龄组调整）
        style = overall_style.get('illustration_style', 'watercolor')
        colors = overall_style.get('color_palette', 'warm and bright')

        # 根据年龄组调整风格描述
        if "3-5" in age_group:
            style_desc = (
                f"{style}儿童插画风格，{colors}色调，"
                "画面简洁清晰，色彩鲜艳明快，"
                "柔和的线条，卡通化的形象，"
                "适合3-5岁儿童，温馨友好，无任何恐怖或暴力元素"
            )
        elif "6-8" in age_group:
            style_desc = (
                f"{style}儿童绘本风格，{colors}色调，"
                "画面细节丰富但不杂乱，色彩和谐，"
                "流畅的线条，生动的表情，"
                "适合6-8岁儿童，富有想象力，安全友好"
            )
        else:  # 9-11
            style_desc = (
                f"{style}少儿文学插画风格，{colors}色调，"
                "画面层次丰富，色彩细腻，"
                "精致的细节，富有表现力的场景，"
                "适合9-11岁儿童，有一定艺术性，安全适龄"
            )

        prompt_parts.append(f"艺术风格: {style_desc}")

        # 组合为完整提示词
        full_prompt = "。".join(prompt_parts) + "。"

        logger.debug(f"Enhanced illustration prompt for page {page_number}: {full_prompt[:100]}...")
        return full_prompt
