# LumosReading Phase 3 优化指令

## 概述

Phase 3 专家评审结果：**8.68/10 (条件通过)**

需要实施以下三项关键优化以达到 9.1+ 分数：

1. **情绪调节支持系统** (Psychology - 8.8→9.2)
2. **中文韵律感检测算法** (Literature - 8.5→9.1)
3. **成本控制精确实施机制** (Technical - 8.7→9.2)

---

## 优化 1: 情绪调节支持系统

### 文件创建

**文件路径**: `apps/ai-service/agents/psychology/emotional_regulation.py`

```python
"""
情绪调节支持模块
基于儿童情绪发展理论的调节框架
参考: Denham (2006) 情绪社会化理论
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class EmotionalDevelopmentStage(Enum):
    """情绪发展阶段"""
    EARLY_CHILDHOOD = "3-5"      # 早期儿童期
    MIDDLE_CHILDHOOD = "6-8"     # 中期儿童期
    LATE_CHILDHOOD = "9-11"      # 晚期儿童期

@dataclass
class EmotionalSkill:
    """情绪技能定义"""
    skill_name: str
    description: str
    age_appropriate: bool
    practice_methods: List[str]
    story_integration_hints: List[str]
    parent_guidance: str = ""

class EmotionalRegulationFramework:
    """
    基于儿童情绪发展理论的调节框架
    参考: Denham (2006) 情绪社会化理论
    """

    def __init__(self):
        self.emotion_skills_by_age = {
            EmotionalDevelopmentStage.EARLY_CHILDHOOD: [
                EmotionalSkill(
                    skill_name="情绪识别",
                    description="识别基本情绪表情和词汇",
                    age_appropriate=True,
                    practice_methods=["情绪脸谱游戏", "情绪词汇学习", "镜子表情练习"],
                    story_integration_hints=["角色表情明确描述", "情绪词汇重复出现"],
                    parent_guidance="与孩子一起指认故事中角色的表情，问'小熊现在感觉怎么样？'"
                ),
                EmotionalSkill(
                    skill_name="情绪表达",
                    description="用合适的方式表达自己的感受",
                    age_appropriate=True,
                    practice_methods=["情绪绘画", "情绪歌曲", "身体语言表达"],
                    story_integration_hints=["角色表达情绪的多种方式", "积极情绪表达范例"],
                    parent_guidance="鼓励孩子说出自己的感受，如'你像故事里的小兔子一样开心吗？'"
                ),
                EmotionalSkill(
                    skill_name="基础自我安慰",
                    description="简单的自我安慰技巧",
                    age_appropriate=True,
                    practice_methods=["深呼吸练习", "拥抱安慰物", "数数冷静"],
                    story_integration_hints=["角色使用安慰技巧", "安慰物品的积极作用"],
                    parent_guidance="当故事角色难过时，和孩子一起练习深呼吸"
                )
            ],

            EmotionalDevelopmentStage.MIDDLE_CHILDHOOD: [
                EmotionalSkill(
                    skill_name="情绪原因理解",
                    description="理解情绪产生的原因和背景",
                    age_appropriate=True,
                    practice_methods=["因果关系讨论", "情境分析", "换位思考练习"],
                    story_integration_hints=["情绪变化的明确原因", "多角度情绪呈现"],
                    parent_guidance="引导孩子思考'为什么小猪会生气？如果是你会怎么样？'"
                ),
                EmotionalSkill(
                    skill_name="情绪强度管理",
                    description="学会调节情绪的强度",
                    age_appropriate=True,
                    practice_methods=["情绪温度计", "渐进式放松", "注意力转移"],
                    story_integration_hints=["情绪强度的层次展示", "调节技巧的具体演示"],
                    parent_guidance="使用'情绪温度计'帮助孩子描述感受的强烈程度"
                ),
                EmotionalSkill(
                    skill_name="社交情绪认知",
                    description="理解他人的情绪和感受",
                    age_appropriate=True,
                    practice_methods=["角色扮演", "情绪猜测游戏", "共情练习"],
                    story_integration_hints=["多角色情绪互动", "情绪传染现象"],
                    parent_guidance="问孩子'你觉得故事里的朋友们现在心情如何？'"
                )
            ],

            EmotionalDevelopmentStage.LATE_CHILDHOOD: [
                EmotionalSkill(
                    skill_name="复杂情绪理解",
                    description="理解混合情绪和复杂感受",
                    age_appropriate=True,
                    practice_methods=["情绪日记", "复杂情境讨论", "情绪词汇扩展"],
                    story_integration_hints=["混合情绪的细腻描述", "情绪冲突的展现"],
                    parent_guidance="讨论角色可能同时感到开心和担心的复杂心情"
                ),
                EmotionalSkill(
                    skill_name="情绪调节策略",
                    description="掌握多种情绪调节方法",
                    age_appropriate=True,
                    practice_methods=["问题解决策略", "认知重构", "寻求帮助"],
                    story_integration_hints=["多种解决方案的对比", "策略选择的智慧"],
                    parent_guidance="和孩子一起分析故事角色的不同应对方式"
                ),
                EmotionalSkill(
                    skill_name="情绪的社会功能",
                    description="理解情绪在社交中的作用",
                    age_appropriate=True,
                    practice_methods=["社交情境分析", "情绪影响讨论", "关系维护练习"],
                    story_integration_hints=["情绪对关系的影响", "情绪沟通的价值"],
                    parent_guidance="探讨故事中情绪如何影响角色之间的友谊"
                )
            ]
        }

        # 神经多样性适配
        self.neuro_adaptations = {
            'ADHD': {
                'attention_regulation': {
                    'skills': ['情绪-注意力连接', '冲动控制', '情绪识别速度训练'],
                    'story_adaptations': ['情绪高亮提示', '简化情绪表达', '重复强化']
                },
                'executive_function': {
                    'skills': ['情绪计划', '情绪监控', '情绪回顾'],
                    'story_adaptations': ['结构化情绪流程', '预测性情绪提示']
                }
            },
            'ASD': {
                'emotional_understanding': {
                    'skills': ['情绪规则学习', '情绪脚本', '情绪预测'],
                    'story_adaptations': ['明确情绪标签', '情绪原因解释', '社交情绪脚本']
                },
                'sensory_emotional': {
                    'skills': ['感官-情绪连接', '情绪调节感官策略'],
                    'story_adaptations': ['感官情绪描述', '环境-情绪关联']
                }
            }
        }

    def get_age_appropriate_skills(self, age_group: str) -> List[EmotionalSkill]:
        """获取年龄适宜的情绪技能"""
        stage = self._age_to_stage(age_group)
        return self.emotion_skills_by_age.get(stage, [])

    def get_neuro_adapted_skills(self, age_group: str, neuro_profile: Dict[str, Any]) -> List[EmotionalSkill]:
        """获取神经多样性适配的情绪技能"""
        base_skills = self.get_age_appropriate_skills(age_group)

        if not neuro_profile:
            return base_skills

        # 根据神经多样性特征调整技能
        adapted_skills = []
        for skill in base_skills:
            adapted_skill = self._adapt_skill_for_neuro(skill, neuro_profile)
            adapted_skills.append(adapted_skill)

        # 添加特定的神经多样性技能
        neuro_specific_skills = self._get_neuro_specific_skills(neuro_profile)
        adapted_skills.extend(neuro_specific_skills)

        return adapted_skills

    def generate_story_emotional_framework(self, child_profile: Dict[str, Any], story_context: Dict[str, Any]) -> Dict[str, Any]:
        """为故事生成情绪发展框架"""
        age_group = child_profile.get('age_group', '6-8')
        neuro_profile = child_profile.get('neuro_profile', {})

        # 获取适合的情绪技能
        emotional_skills = self.get_neuro_adapted_skills(age_group, neuro_profile)

        # 选择2-3个核心技能融入故事
        primary_skills = self._select_primary_skills(emotional_skills, story_context)

        # 生成具体的故事集成指导
        framework = {
            'target_skills': [
                {
                    'skill_name': skill.skill_name,
                    'integration_points': skill.story_integration_hints,
                    'parent_guidance': skill.parent_guidance
                }
                for skill in primary_skills
            ],
            'emotional_arc': self._design_emotional_arc(primary_skills, story_context),
            'interaction_prompts': self._generate_interaction_prompts(primary_skills),
            'assessment_points': self._create_assessment_points(primary_skills)
        }

        return framework

    def _age_to_stage(self, age_group: str) -> EmotionalDevelopmentStage:
        """年龄组转换为发展阶段"""
        if age_group in ['3-5', '3-4', '4-5']:
            return EmotionalDevelopmentStage.EARLY_CHILDHOOD
        elif age_group in ['6-8', '6-7', '7-8']:
            return EmotionalDevelopmentStage.MIDDLE_CHILDHOOD
        else:
            return EmotionalDevelopmentStage.LATE_CHILDHOOD

    def _adapt_skill_for_neuro(self, skill: EmotionalSkill, neuro_profile: Dict[str, Any]) -> EmotionalSkill:
        """为神经多样性儿童适配情绪技能"""
        adapted_skill = EmotionalSkill(
            skill_name=skill.skill_name,
            description=skill.description,
            age_appropriate=skill.age_appropriate,
            practice_methods=skill.practice_methods.copy(),
            story_integration_hints=skill.story_integration_hints.copy(),
            parent_guidance=skill.parent_guidance
        )

        # ADHD适配
        if neuro_profile.get('ADHD'):
            adapted_skill.practice_methods.extend(['分步骤练习', '视觉提示卡', '动作结合'])
            adapted_skill.story_integration_hints.extend(['高频情绪提醒', '动作化情绪表达'])

        # 自闭谱系适配
        if neuro_profile.get('ASD'):
            adapted_skill.practice_methods.extend(['结构化练习', '情绪规则卡', '预测性提示'])
            adapted_skill.story_integration_hints.extend(['明确的情绪因果', '情绪规律说明'])

        return adapted_skill

    def _get_neuro_specific_skills(self, neuro_profile: Dict[str, Any]) -> List[EmotionalSkill]:
        """获取神经多样性特定技能"""
        specific_skills = []

        if neuro_profile.get('ADHD'):
            specific_skills.append(
                EmotionalSkill(
                    skill_name="情绪-注意力管理",
                    description="学会在情绪激动时保持注意力",
                    age_appropriate=True,
                    practice_methods=["情绪停顿法", "注意力锚点", "情绪-任务切换"],
                    story_integration_hints=["角色的注意力管理", "情绪中的专注技巧"],
                    parent_guidance="帮助孩子识别情绪对注意力的影响"
                )
            )

        if neuro_profile.get('ASD'):
            specific_skills.append(
                EmotionalSkill(
                    skill_name="社交情绪脚本",
                    description="学习标准的社交情绪反应",
                    age_appropriate=True,
                    practice_methods=["情绪脚本练习", "社交情绪地图", "预设回应"],
                    story_integration_hints=["标准化社交反应", "情绪脚本示范"],
                    parent_guidance="和孩子一起总结故事中的社交情绪规律"
                )
            )

        return specific_skills

    def _select_primary_skills(self, skills: List[EmotionalSkill], story_context: Dict[str, Any]) -> List[EmotionalSkill]:
        """选择故事的主要情绪技能(2-3个)"""
        # 基于故事主题和情节选择最相关的技能
        story_theme = story_context.get('theme', '')
        story_conflicts = story_context.get('conflicts', [])

        priority_scores = {}
        for skill in skills:
            score = 0

            # 基于主题匹配
            if '友谊' in story_theme and '社交' in skill.skill_name:
                score += 3
            if '挑战' in story_theme and '调节' in skill.skill_name:
                score += 3
            if '成长' in story_theme and '理解' in skill.skill_name:
                score += 2

            # 基于冲突类型匹配
            for conflict in story_conflicts:
                if '情绪冲突' in conflict and '管理' in skill.skill_name:
                    score += 2
                if '社交困难' in conflict and '社交' in skill.skill_name:
                    score += 2

            priority_scores[skill] = score

        # 选择得分最高的2-3个技能
        sorted_skills = sorted(skills, key=lambda s: priority_scores.get(s, 0), reverse=True)
        return sorted_skills[:3]

    def _design_emotional_arc(self, skills: List[EmotionalSkill], story_context: Dict[str, Any]) -> Dict[str, Any]:
        """设计故事的情绪发展弧线"""
        return {
            'beginning': {
                'emotional_state': '建立基础情绪状态',
                'skills_introduction': [skill.skill_name for skill in skills[:1]]
            },
            'middle': {
                'emotional_challenge': '引入情绪挑战和冲突',
                'skills_practice': [skill.skill_name for skill in skills[1:]]
            },
            'end': {
                'emotional_resolution': '展示技能应用和成长',
                'skills_mastery': [skill.skill_name for skill in skills]
            }
        }

    def _generate_interaction_prompts(self, skills: List[EmotionalSkill]) -> List[Dict[str, str]]:
        """生成CROWD-PEER交互提示"""
        prompts = []

        for skill in skills:
            prompts.extend([
                {
                    'type': 'Completion',
                    'prompt': f'当{skill.skill_name}的时候，我们可以...',
                    'skill_focus': skill.skill_name
                },
                {
                    'type': 'Recall',
                    'prompt': f'你还记得故事中谁使用了{skill.skill_name}吗？',
                    'skill_focus': skill.skill_name
                },
                {
                    'type': 'Open_ended',
                    'prompt': f'如果你遇到同样的情况，你会怎么{skill.skill_name}？',
                    'skill_focus': skill.skill_name
                }
            ])

        return prompts

    def _create_assessment_points(self, skills: List[EmotionalSkill]) -> List[Dict[str, Any]]:
        """创建技能评估点"""
        assessment_points = []

        for skill in skills:
            assessment_points.append({
                'skill': skill.skill_name,
                'assessment_method': 'observation',
                'indicators': [
                    '能够识别相关情绪',
                    '理解技能的应用场景',
                    '尝试在互动中应用技能'
                ],
                'parent_observation_guide': skill.parent_guidance
            })

        return assessment_points
```

### 集成修改

**修改文件**: `apps/ai-service/agents/psychology/expert.py`

在 `PsychologyExpert` 类中添加情绪调节支持：

```python
from .emotional_regulation import EmotionalRegulationFramework

class PsychologyExpert:
    def __init__(self):
        # 现有代码...
        self.emotional_framework = EmotionalRegulationFramework()

    async def generate_educational_framework(self, child_profile: Dict[str, Any], story_request: Dict[str, Any]) -> EducationalFramework:
        # 现有代码...

        # 新增：情绪发展框架生成
        emotional_framework = self.emotional_framework.generate_story_emotional_framework(
            child_profile,
            story_request
        )

        # 整合到教育框架中
        framework.emotional_development = emotional_framework
        framework.crowd_prompts.extend(emotional_framework['interaction_prompts'])

        return framework
```

---

## 优化 2: 中文韵律感检测算法

### 文件创建

**文件路径**: `apps/ai-service/agents/story_creation/rhythm_analyzer.py`

```python
"""
中文儿童文学韵律感检测模块
基于汉语音韵学理论和儿童认知规律
"""

import re
import jieba
import pypinyin
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class RhythmPattern(Enum):
    """韵律模式分类"""
    SIMPLE_RHYTHM = "简单韵律"      # 3-5岁：AA BB式
    COMPOUND_RHYTHM = "复合韵律"    # 6-8岁：ABAB, AABA式
    COMPLEX_RHYTHM = "复杂韵律"     # 9-11岁：多变化韵律

@dataclass
class SyllableUnit:
    """音节单元"""
    character: str
    pinyin: str
    tone: int
    is_rhyme: bool = False
    stress_level: float = 0.0

@dataclass
class RhythmScore:
    """韵律评分"""
    overall_score: float
    rhythm_consistency: float
    tone_harmony: float
    reading_flow: float
    age_appropriateness: float
    improvement_suggestions: List[str]

class ChineseRhythmAnalyzer:
    """
    中文韵律分析器
    基于《汉语音韵学》理论和儿童语言发展规律
    """

    def __init__(self):
        # 声调协调度权重矩阵
        self.tone_harmony_matrix = {
            (1, 1): 0.9, (1, 2): 0.7, (1, 3): 0.6, (1, 4): 0.8,
            (2, 1): 0.7, (2, 2): 0.9, (2, 3): 0.8, (2, 4): 0.6,
            (3, 1): 0.6, (3, 2): 0.8, (3, 3): 0.9, (3, 4): 0.7,
            (4, 1): 0.8, (4, 2): 0.6, (4, 3): 0.7, (4, 4): 0.9
        }

        # 年龄段韵律特征期望
        self.age_rhythm_preferences = {
            '3-5': {
                'preferred_patterns': [RhythmPattern.SIMPLE_RHYTHM],
                'sentence_length': (4, 8),      # 字数
                'tone_variation': 'low',         # 声调变化度
                'rhyme_frequency': 0.6           # 押韵频率
            },
            '6-8': {
                'preferred_patterns': [RhythmPattern.SIMPLE_RHYTHM, RhythmPattern.COMPOUND_RHYTHM],
                'sentence_length': (6, 12),
                'tone_variation': 'medium',
                'rhyme_frequency': 0.4
            },
            '9-11': {
                'preferred_patterns': [RhythmPattern.COMPOUND_RHYTHM, RhythmPattern.COMPLEX_RHYTHM],
                'sentence_length': (8, 16),
                'tone_variation': 'high',
                'rhyme_frequency': 0.3
            }
        }

    def analyze_text_rhythm(self, text: str, target_age: str) -> RhythmScore:
        """
        分析文本韵律质量

        Args:
            text: 待分析文本
            target_age: 目标年龄段 ('3-5', '6-8', '9-11')

        Returns:
            RhythmScore: 韵律评分和建议
        """
        # 1. 文本预处理和分句
        sentences = self._split_sentences(text)

        # 2. 音节分析
        syllable_analysis = []
        for sentence in sentences:
            syllables = self._extract_syllables(sentence)
            syllable_analysis.append(syllables)

        # 3. 韵律模式识别
        rhythm_patterns = self._identify_rhythm_patterns(syllable_analysis)

        # 4. 声调协调度计算
        tone_harmony = self._calculate_tone_harmony(syllable_analysis)

        # 5. 阅读流畅度评估
        reading_flow = self._assess_reading_flow(syllable_analysis, target_age)

        # 6. 年龄适宜性检查
        age_appropriateness = self._check_age_appropriateness(
            rhythm_patterns, syllable_analysis, target_age
        )

        # 7. 韵律一致性计算
        rhythm_consistency = self._calculate_rhythm_consistency(rhythm_patterns)

        # 8. 综合评分
        overall_score = self._calculate_overall_score(
            rhythm_consistency, tone_harmony, reading_flow, age_appropriateness
        )

        # 9. 生成改进建议
        suggestions = self._generate_improvement_suggestions(
            rhythm_consistency, tone_harmony, reading_flow, age_appropriateness, target_age
        )

        return RhythmScore(
            overall_score=overall_score,
            rhythm_consistency=rhythm_consistency,
            tone_harmony=tone_harmony,
            reading_flow=reading_flow,
            age_appropriateness=age_appropriateness,
            improvement_suggestions=suggestions
        )

    def _split_sentences(self, text: str) -> List[str]:
        """分句处理"""
        # 中文标点符号分句
        sentence_endings = re.compile(r'[。！？；\n]')
        sentences = sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_syllables(self, sentence: str) -> List[SyllableUnit]:
        """提取音节信息"""
        # 分词
        words = jieba.lcut(sentence)
        syllables = []

        for word in words:
            for char in word:
                if '\u4e00' <= char <= '\u9fff':  # 中文字符
                    pinyin_list = pypinyin.pinyin(char, style=pypinyin.TONE_NUM)
                    if pinyin_list:
                        pinyin_str = pinyin_list[0][0]
                        tone = self._extract_tone(pinyin_str)
                        syllable = SyllableUnit(
                            character=char,
                            pinyin=pinyin_str,
                            tone=tone
                        )
                        syllables.append(syllable)

        return syllables

    def _extract_tone(self, pinyin: str) -> int:
        """提取声调"""
        if pinyin[-1].isdigit():
            return int(pinyin[-1])
        return 0  # 轻声

    def _identify_rhythm_patterns(self, syllable_analysis: List[List[SyllableUnit]]) -> List[RhythmPattern]:
        """识别韵律模式"""
        patterns = []

        for sentence_syllables in syllable_analysis:
            if len(sentence_syllables) <= 6:
                # 短句倾向于简单韵律
                pattern = RhythmPattern.SIMPLE_RHYTHM
            elif len(sentence_syllables) <= 12:
                # 中等长度句子检查是否有复合韵律
                if self._has_compound_rhythm(sentence_syllables):
                    pattern = RhythmPattern.COMPOUND_RHYTHM
                else:
                    pattern = RhythmPattern.SIMPLE_RHYTHM
            else:
                # 长句可能有复杂韵律
                if self._has_complex_rhythm(sentence_syllables):
                    pattern = RhythmPattern.COMPLEX_RHYTHM
                elif self._has_compound_rhythm(sentence_syllables):
                    pattern = RhythmPattern.COMPOUND_RHYTHM
                else:
                    pattern = RhythmPattern.SIMPLE_RHYTHM

            patterns.append(pattern)

        return patterns

    def _has_compound_rhythm(self, syllables: List[SyllableUnit]) -> bool:
        """检测复合韵律(ABAB模式等)"""
        if len(syllables) < 4:
            return False

        # 检查ABAB声调模式
        tone_pattern = [s.tone for s in syllables[:4]]
        if len(set(tone_pattern)) == 2 and tone_pattern[0] == tone_pattern[2] and tone_pattern[1] == tone_pattern[3]:
            return True

        # 检查韵母重复模式
        rhyme_pattern = [self._get_rhyme(s.pinyin) for s in syllables[:4]]
        if len(set(rhyme_pattern)) == 2 and rhyme_pattern[0] == rhyme_pattern[2] and rhyme_pattern[1] == rhyme_pattern[3]:
            return True

        return False

    def _has_complex_rhythm(self, syllables: List[SyllableUnit]) -> bool:
        """检测复杂韵律"""
        if len(syllables) < 8:
            return False

        # 检查多层次韵律变化
        tone_changes = 0
        for i in range(1, len(syllables)):
            if syllables[i].tone != syllables[i-1].tone:
                tone_changes += 1

        # 声调变化超过60%认为是复杂韵律
        return tone_changes / len(syllables) > 0.6

    def _get_rhyme(self, pinyin: str) -> str:
        """提取韵母"""
        # 简化版韵母提取
        consonants = 'bcdfghjklmnpqrstwxyz'
        for i, char in enumerate(pinyin):
            if char.lower() not in consonants:
                return pinyin[i:].rstrip('1234')
        return pinyin.rstrip('1234')

    def _calculate_tone_harmony(self, syllable_analysis: List[List[SyllableUnit]]) -> float:
        """计算声调协调度"""
        total_harmony = 0.0
        total_pairs = 0

        for sentence_syllables in syllable_analysis:
            for i in range(len(sentence_syllables) - 1):
                tone1 = sentence_syllables[i].tone
                tone2 = sentence_syllables[i + 1].tone

                if tone1 in self.tone_harmony_matrix and tone2 in self.tone_harmony_matrix:
                    harmony = self.tone_harmony_matrix.get((tone1, tone2), 0.5)
                    total_harmony += harmony
                    total_pairs += 1

        return total_harmony / total_pairs if total_pairs > 0 else 0.5

    def _assess_reading_flow(self, syllable_analysis: List[List[SyllableUnit]], target_age: str) -> float:
        """评估阅读流畅度"""
        age_prefs = self.age_rhythm_preferences[target_age]
        min_len, max_len = age_prefs['sentence_length']

        # 句长适宜性
        length_scores = []
        for sentence_syllables in syllable_analysis:
            length = len(sentence_syllables)
            if min_len <= length <= max_len:
                length_score = 1.0
            elif length < min_len:
                length_score = length / min_len
            else:
                length_score = max_len / length
            length_scores.append(length_score)

        avg_length_score = sum(length_scores) / len(length_scores) if length_scores else 0

        # 节奏变化适宜性
        rhythm_variation = self._calculate_rhythm_variation(syllable_analysis)
        target_variation = age_prefs['tone_variation']

        if target_variation == 'low':
            variation_score = 1.0 - min(rhythm_variation, 0.5) * 2
        elif target_variation == 'medium':
            variation_score = 1.0 - abs(rhythm_variation - 0.5) * 2
        else:  # high
            variation_score = min(rhythm_variation * 2, 1.0)

        return (avg_length_score + variation_score) / 2

    def _calculate_rhythm_variation(self, syllable_analysis: List[List[SyllableUnit]]) -> float:
        """计算韵律变化度"""
        if not syllable_analysis:
            return 0.0

        total_variations = 0
        total_positions = 0

        for sentence_syllables in syllable_analysis:
            for i in range(len(sentence_syllables) - 1):
                if sentence_syllables[i].tone != sentence_syllables[i + 1].tone:
                    total_variations += 1
                total_positions += 1

        return total_variations / total_positions if total_positions > 0 else 0

    def _check_age_appropriateness(self, rhythm_patterns: List[RhythmPattern],
                                 syllable_analysis: List[List[SyllableUnit]],
                                 target_age: str) -> float:
        """检查年龄适宜性"""
        age_prefs = self.age_rhythm_preferences[target_age]
        preferred_patterns = age_prefs['preferred_patterns']

        # 韵律模式适宜性
        pattern_match_count = sum(1 for pattern in rhythm_patterns if pattern in preferred_patterns)
        pattern_score = pattern_match_count / len(rhythm_patterns) if rhythm_patterns else 0

        # 整体复杂度适宜性
        avg_sentence_length = sum(len(s) for s in syllable_analysis) / len(syllable_analysis) if syllable_analysis else 0
        min_len, max_len = age_prefs['sentence_length']

        if min_len <= avg_sentence_length <= max_len:
            complexity_score = 1.0
        else:
            complexity_score = 0.5

        return (pattern_score + complexity_score) / 2

    def _calculate_rhythm_consistency(self, rhythm_patterns: List[RhythmPattern]) -> float:
        """计算韵律一致性"""
        if not rhythm_patterns:
            return 0.0

        # 统计各种韵律模式的比例
        pattern_counts = {}
        for pattern in rhythm_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # 计算一致性：主要模式占比
        max_count = max(pattern_counts.values())
        consistency = max_count / len(rhythm_patterns)

        return consistency

    def _calculate_overall_score(self, rhythm_consistency: float, tone_harmony: float,
                               reading_flow: float, age_appropriateness: float) -> float:
        """计算综合评分"""
        weights = {
            'rhythm_consistency': 0.25,
            'tone_harmony': 0.25,
            'reading_flow': 0.30,
            'age_appropriateness': 0.20
        }

        overall = (
            rhythm_consistency * weights['rhythm_consistency'] +
            tone_harmony * weights['tone_harmony'] +
            reading_flow * weights['reading_flow'] +
            age_appropriateness * weights['age_appropriateness']
        )

        return min(overall, 1.0)

    def _generate_improvement_suggestions(self, rhythm_consistency: float, tone_harmony: float,
                                        reading_flow: float, age_appropriateness: float,
                                        target_age: str) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if rhythm_consistency < 0.7:
            suggestions.append("建议保持韵律模式的一致性，避免在同一段落中混用过多不同的韵律风格")

        if tone_harmony < 0.6:
            suggestions.append("声调搭配需要优化，建议避免连续使用冲突的声调组合（如一声接三声）")

        if reading_flow < 0.6:
            age_prefs = self.age_rhythm_preferences[target_age]
            min_len, max_len = age_prefs['sentence_length']
            suggestions.append(f"句子长度建议控制在{min_len}-{max_len}个字，以提高阅读流畅度")

        if age_appropriateness < 0.7:
            if target_age == '3-5':
                suggestions.append("建议使用更简单的韵律模式，多采用重复和对称结构")
            elif target_age == '6-8':
                suggestions.append("可以适当增加韵律变化，但保持整体结构清晰")
            else:
                suggestions.append("可以使用更复杂的韵律结构，增加文学表现力")

        if not suggestions:
            suggestions.append("韵律质量良好，保持当前风格")

        return suggestions

# 集成到儿童文学专家代理中
class EnhancedChildrenLiteratureExpert:
    """
    增强版儿童文学专家（集成韵律分析）
    """

    def __init__(self):
        self.rhythm_analyzer = ChineseRhythmAnalyzer()
        # ... 其他初始化代码

    async def generate_story_with_rhythm_check(self, story_request: Dict[str, Any]) -> Dict[str, Any]:
        """生成故事并进行韵律检查"""
        # 1. 原有故事生成逻辑
        story_content = await self._generate_base_story(story_request)

        # 2. 韵律质量检查
        target_age = story_request.get('child_profile', {}).get('age_group', '6-8')
        rhythm_score = self.rhythm_analyzer.analyze_text_rhythm(
            story_content['text'],
            target_age
        )

        # 3. 质量判断和优化
        if rhythm_score.overall_score < 0.7:
            # 自动优化或降级处理
            optimized_content = await self._optimize_story_rhythm(
                story_content,
                rhythm_score.improvement_suggestions,
                target_age
            )

            # 重新检查
            new_rhythm_score = self.rhythm_analyzer.analyze_text_rhythm(
                optimized_content['text'],
                target_age
            )

            if new_rhythm_score.overall_score > rhythm_score.overall_score:
                story_content = optimized_content
                rhythm_score = new_rhythm_score

        # 4. 添加韵律质量元数据
        story_content['quality_metrics']['rhythm_analysis'] = {
            'overall_score': rhythm_score.overall_score,
            'rhythm_consistency': rhythm_score.rhythm_consistency,
            'tone_harmony': rhythm_score.tone_harmony,
            'reading_flow': rhythm_score.reading_flow,
            'age_appropriateness': rhythm_score.age_appropriateness,
            'suggestions': rhythm_score.improvement_suggestions
        }

        return story_content
```

### 集成修改

**修改文件**: `apps/ai-service/agents/story_creation/expert.py`

```python
from .rhythm_analyzer import ChineseRhythmAnalyzer

class ChildrenLiteratureExpert:
    def __init__(self):
        # 现有代码...
        self.rhythm_analyzer = ChineseRhythmAnalyzer()

    async def create_story(self, request):
        # 现有生成逻辑...

        # 新增：韵律质量检查
        target_age = request.child_profile.age_group
        rhythm_score = self.rhythm_analyzer.analyze_text_rhythm(
            story_content, target_age
        )

        # 质量评分更新
        story_data['quality_score'] = (
            existing_quality_score * 0.7 +
            rhythm_score.overall_score * 0.3
        )

        return story_data
```

---

## 优化 3: 成本控制精确实施机制

### 文件创建

**文件路径**: `apps/ai-service/core/cost_control.py`

```python
"""
AI服务成本控制精确实施机制
包含预算检查、成本预测、自动降级等功能
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import redis
import json

class CostLevel(Enum):
    """成本等级"""
    MINIMAL = "最低成本"     # 预生产内容 + 通义千问
    STANDARD = "标准成本"    # 模板 + 通义千问/GPT-3.5
    PREMIUM = "高级成本"     # 定制 + Claude/GPT-4
    EMERGENCY = "紧急模式"   # 仅预生产库

class BudgetStatus(Enum):
    """预算状态"""
    SAFE = "安全"           # <70%预算
    WARNING = "警告"        # 70-90%预算
    CRITICAL = "临界"       # 90-100%预算
    EXCEEDED = "超支"       # >100%预算

@dataclass
class CostEstimate:
    """成本估算"""
    total_tokens: int
    estimated_cost: float
    processing_time: float
    confidence: float
    breakdown: Dict[str, float]

@dataclass
class BudgetInfo:
    """预算信息"""
    daily_limit: float
    monthly_limit: float
    current_daily_usage: float
    current_monthly_usage: float
    remaining_daily: float
    remaining_monthly: float
    status: BudgetStatus

class EnhancedCostController:
    """
    增强版成本控制器
    支持预算预检查、智能降级、成本优化
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)

        # 模型成本配置 (每1000 tokens)
        self.model_costs = {
            'claude-3-opus': {'input': 0.15, 'output': 0.75},
            'claude-3-sonnet': {'input': 0.03, 'output': 0.15},
            'gpt-4-turbo': {'input': 0.10, 'output': 0.30},
            'gpt-3.5-turbo': {'input': 0.01, 'output': 0.02},
            'qwen-max': {'input': 0.008, 'output': 0.008},
            'qwen-plus': {'input': 0.004, 'output': 0.004}
        }

        # 预算限制配置
        self.budget_limits = {
            'free': {'daily': 5.0, 'monthly': 100.0},
            'standard': {'daily': 20.0, 'monthly': 500.0},
            'premium': {'daily': 100.0, 'monthly': 2000.0},
            'family': {'daily': 150.0, 'monthly': 3000.0}
        }

        # 降级策略配置
        self.fallback_strategies = {
            CostLevel.PREMIUM: [
                ('claude-3-opus', 'claude-3-sonnet'),
                ('gpt-4-turbo', 'gpt-3.5-turbo'),
                ('qwen-max', 'qwen-plus')
            ],
            CostLevel.STANDARD: [
                ('claude-3-sonnet', 'qwen-max'),
                ('gpt-3.5-turbo', 'qwen-plus')
            ],
            CostLevel.MINIMAL: [
                ('qwen-plus', 'preproduced')
            ]
        }

    async def pre_request_budget_check(self, user_id: str, request_details: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        请求前预算检查

        Args:
            user_id: 用户ID
            request_details: 请求详情 (包含模型、内容长度等)

        Returns:
            (是否允许请求, 决策信息)
        """
        # 1. 获取用户预算信息
        budget_info = await self._get_budget_info(user_id)

        # 2. 估算请求成本
        cost_estimate = self._estimate_request_cost(request_details)

        # 3. 预算充足性检查
        can_proceed = self._check_budget_sufficiency(budget_info, cost_estimate)

        # 4. 生成决策信息
        decision_info = {
            'can_proceed': can_proceed,
            'budget_status': budget_info.status.value,
            'estimated_cost': cost_estimate.estimated_cost,
            'remaining_budget': budget_info.remaining_daily,
            'suggested_action': None,
            'alternative_options': []
        }

        # 5. 如果预算不足，提供替代方案
        if not can_proceed:
            alternatives = await self._generate_alternatives(request_details, budget_info)
            decision_info['alternative_options'] = alternatives
            decision_info['suggested_action'] = '预算不足，建议选择替代方案'

        # 6. 如果预算警告，提供优化建议
        elif budget_info.status in [BudgetStatus.WARNING, BudgetStatus.CRITICAL]:
            optimization = await self._suggest_cost_optimization(request_details)
            decision_info['suggested_action'] = '预算紧张，建议成本优化'
            decision_info['optimization_suggestions'] = optimization

        return can_proceed, decision_info

    async def _get_budget_info(self, user_id: str) -> BudgetInfo:
        """获取用户预算信息"""
        # 获取用户订阅等级
        user_tier = await self._get_user_tier(user_id)
        limits = self.budget_limits[user_tier]

        # 获取当前使用情况
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')

        daily_key = f"cost:daily:{user_id}:{today}"
        monthly_key = f"cost:monthly:{user_id}:{month}"

        current_daily = float(self.redis.get(daily_key) or 0)
        current_monthly = float(self.redis.get(monthly_key) or 0)

        # 计算剩余预算
        remaining_daily = max(0, limits['daily'] - current_daily)
        remaining_monthly = max(0, limits['monthly'] - current_monthly)

        # 确定预算状态
        daily_usage_ratio = current_daily / limits['daily']
        if daily_usage_ratio >= 1.0:
            status = BudgetStatus.EXCEEDED
        elif daily_usage_ratio >= 0.9:
            status = BudgetStatus.CRITICAL
        elif daily_usage_ratio >= 0.7:
            status = BudgetStatus.WARNING
        else:
            status = BudgetStatus.SAFE

        return BudgetInfo(
            daily_limit=limits['daily'],
            monthly_limit=limits['monthly'],
            current_daily_usage=current_daily,
            current_monthly_usage=current_monthly,
            remaining_daily=remaining_daily,
            remaining_monthly=remaining_monthly,
            status=status
        )

    def _estimate_request_cost(self, request_details: Dict[str, Any]) -> CostEstimate:
        """估算请求成本"""
        model = request_details.get('model', 'qwen-plus')
        content_length = request_details.get('content_length', 1000)
        request_type = request_details.get('type', 'story_generation')

        # 基于内容长度估算 token 数量
        if request_type == 'story_generation':
            # 故事生成：输入较少，输出较多
            input_tokens = min(content_length * 0.5, 2000)  # 输入提示词
            output_tokens = content_length * 2              # 生成的故事内容
        elif request_type == 'illustration':
            # 插画生成：固定成本
            input_tokens = 500
            output_tokens = 100
        else:
            # 其他类型：均衡估算
            input_tokens = content_length * 0.8
            output_tokens = content_length * 0.3

        # 计算成本
        if model in self.model_costs:
            cost_config = self.model_costs[model]
            input_cost = (input_tokens / 1000) * cost_config['input']
            output_cost = (output_tokens / 1000) * cost_config['output']
            total_cost = input_cost + output_cost
        else:
            # 未知模型，使用平均成本
            total_cost = ((input_tokens + output_tokens) / 1000) * 0.05

        # 添加处理时间估算
        processing_time = self._estimate_processing_time(model, input_tokens + output_tokens)

        # 置信度：基于历史数据的准确性（简化版）
        confidence = 0.85

        return CostEstimate(
            total_tokens=int(input_tokens + output_tokens),
            estimated_cost=round(total_cost, 4),
            processing_time=processing_time,
            confidence=confidence,
            breakdown={
                'input_cost': round(input_cost, 4),
                'output_cost': round(output_cost, 4),
                'model': model
            }
        )

    def _estimate_processing_time(self, model: str, total_tokens: int) -> float:
        """估算处理时间（秒）"""
        # 不同模型的处理速度（tokens/秒）
        model_speeds = {
            'claude-3-opus': 20,
            'claude-3-sonnet': 40,
            'gpt-4-turbo': 30,
            'gpt-3.5-turbo': 60,
            'qwen-max': 50,
            'qwen-plus': 80
        }

        speed = model_speeds.get(model, 40)
        base_time = total_tokens / speed

        # 添加网络延迟和处理开销
        overhead = 2.0  # 2秒基础开销
        return base_time + overhead

    def _check_budget_sufficiency(self, budget_info: BudgetInfo, cost_estimate: CostEstimate) -> bool:
        """检查预算充足性"""
        # 保守检查：确保有余量应对估算误差
        safety_margin = 1.2  # 20%安全边际
        required_budget = cost_estimate.estimated_cost * safety_margin

        # 检查日预算和月预算
        daily_sufficient = budget_info.remaining_daily >= required_budget
        monthly_sufficient = budget_info.remaining_monthly >= required_budget

        return daily_sufficient and monthly_sufficient

    async def _generate_alternatives(self, request_details: Dict[str, Any], budget_info: BudgetInfo) -> List[Dict[str, Any]]:
        """生成替代方案"""
        alternatives = []
        original_model = request_details.get('model', 'qwen-plus')

        # 1. 模型降级方案
        for fallback_model in self._get_fallback_models(original_model):
            alt_request = request_details.copy()
            alt_request['model'] = fallback_model
            alt_cost = self._estimate_request_cost(alt_request)

            if self._check_budget_sufficiency(budget_info, alt_cost):
                alternatives.append({
                    'type': 'model_downgrade',
                    'description': f'使用 {fallback_model} 替代 {original_model}',
                    'cost_saving': request_details.get('estimated_cost', 0) - alt_cost.estimated_cost,
                    'new_cost': alt_cost.estimated_cost,
                    'parameters': alt_request
                })

        # 2. 内容长度减少方案
        original_length = request_details.get('content_length', 1000)
        for reduction_ratio in [0.8, 0.6, 0.4]:
            alt_request = request_details.copy()
            alt_request['content_length'] = int(original_length * reduction_ratio)
            alt_cost = self._estimate_request_cost(alt_request)

            if self._check_budget_sufficiency(budget_info, alt_cost):
                alternatives.append({
                    'type': 'content_reduction',
                    'description': f'内容长度减少 {int((1-reduction_ratio)*100)}%',
                    'cost_saving': request_details.get('estimated_cost', 0) - alt_cost.estimated_cost,
                    'new_cost': alt_cost.estimated_cost,
                    'parameters': alt_request
                })

        # 3. 预生产内容方案
        if budget_info.remaining_daily >= 0.5:  # 预生产内容的小额成本
            alternatives.append({
                'type': 'preproduced',
                'description': '使用预生产内容库',
                'cost_saving': request_details.get('estimated_cost', 0) - 0.1,
                'new_cost': 0.1,
                'parameters': {'type': 'preproduced', 'fallback': True}
            })

        return sorted(alternatives, key=lambda x: x['cost_saving'], reverse=True)

    def _get_fallback_models(self, original_model: str) -> List[str]:
        """获取降级模型列表"""
        fallback_chain = {
            'claude-3-opus': ['claude-3-sonnet', 'qwen-max', 'qwen-plus'],
            'claude-3-sonnet': ['qwen-max', 'qwen-plus'],
            'gpt-4-turbo': ['gpt-3.5-turbo', 'qwen-max', 'qwen-plus'],
            'gpt-3.5-turbo': ['qwen-plus'],
            'qwen-max': ['qwen-plus'],
            'qwen-plus': []
        }

        return fallback_chain.get(original_model, ['qwen-plus'])

    async def _suggest_cost_optimization(self, request_details: Dict[str, Any]) -> Dict[str, Any]:
        """建议成本优化方案"""
        optimizations = {
            'immediate_savings': [],
            'workflow_optimizations': [],
            'subscription_suggestions': []
        }

        # 即时节省建议
        current_model = request_details.get('model', 'qwen-plus')
        if current_model in ['claude-3-opus', 'gpt-4-turbo']:
            optimizations['immediate_savings'].append({
                'action': '使用高效模型',
                'description': f'将 {current_model} 替换为 claude-3-sonnet 或 qwen-max',
                'potential_saving': '节省 60-80% 成本，质量损失 <10%'
            })

        # 工作流优化建议
        optimizations['workflow_optimizations'].extend([
            {
                'action': '批量处理',
                'description': '将多个请求合并处理，减少API调用次数',
                'potential_saving': '节省 20-30% 成本'
            },
            {
                'action': '智能缓存',
                'description': '启用相似内容缓存，避免重复生成',
                'potential_saving': '节省 40-60% 重复成本'
            }
        ])

        # 订阅建议（基于当前使用模式）
        current_usage = request_details.get('daily_requests', 1)
        if current_usage > 10:
            optimizations['subscription_suggestions'].append({
                'suggestion': '升级到高级版',
                'reason': '高频使用用户享受更高预算和优先处理',
                'benefit': '每日预算从 ¥20 提升到 ¥100'
            })

        return optimizations

    async def record_actual_cost(self, user_id: str, request_details: Dict[str, Any], actual_cost: float):
        """记录实际成本"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')

        # 更新使用统计
        daily_key = f"cost:daily:{user_id}:{today}"
        monthly_key = f"cost:monthly:{user_id}:{month}"

        # 原子性更新
        pipe = self.redis.pipeline()
        pipe.incrbyfloat(daily_key, actual_cost)
        pipe.expire(daily_key, 86400 * 2)  # 2天过期
        pipe.incrbyfloat(monthly_key, actual_cost)
        pipe.expire(monthly_key, 86400 * 35)  # 35天过期
        pipe.execute()

        # 记录详细使用日志
        usage_log = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'model': request_details.get('model'),
            'type': request_details.get('type'),
            'actual_cost': actual_cost,
            'estimated_cost': request_details.get('estimated_cost'),
            'accuracy': actual_cost / request_details.get('estimated_cost', actual_cost)
        }

        log_key = f"cost:log:{user_id}:{today}"
        self.redis.lpush(log_key, json.dumps(usage_log))
        self.redis.expire(log_key, 86400 * 7)  # 7天日志保留

        self.logger.info(f"Cost recorded for user {user_id}: ${actual_cost}")

    async def get_cost_analytics(self, user_id: str) -> Dict[str, Any]:
        """获取成本分析报告"""
        today = datetime.now().strftime('%Y-%m-%d')

        # 获取最近7天的详细日志
        analytics = {
            'daily_breakdown': {},
            'model_usage': {},
            'cost_trends': {},
            'efficiency_metrics': {}
        }

        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            log_key = f"cost:log:{user_id}:{date}"
            logs = self.redis.lrange(log_key, 0, -1)

            daily_cost = 0
            model_usage = {}

            for log_data in logs:
                log = json.loads(log_data)
                daily_cost += log['actual_cost']
                model = log['model']
                model_usage[model] = model_usage.get(model, 0) + log['actual_cost']

            analytics['daily_breakdown'][date] = daily_cost
            if date == today:
                analytics['model_usage'] = model_usage

        return analytics

    async def _get_user_tier(self, user_id: str) -> str:
        """获取用户订阅等级（简化版）"""
        # 这里应该从数据库获取，暂时返回默认值
        tier_key = f"user:tier:{user_id}"
        tier = self.redis.get(tier_key)
        return tier.decode() if tier else 'standard'

# 自动降级装饰器
def with_cost_control(cost_controller: EnhancedCostController):
    """成本控制装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 提取用户信息和请求详情
            user_id = kwargs.get('user_id') or args[0] if args else None
            request_details = kwargs.get('request_details', {})

            # 预算检查
            can_proceed, decision_info = await cost_controller.pre_request_budget_check(
                user_id, request_details
            )

            if not can_proceed:
                # 尝试自动降级
                alternatives = decision_info.get('alternative_options', [])
                if alternatives:
                    best_alternative = alternatives[0]
                    kwargs['request_details'] = best_alternative['parameters']
                    cost_controller.logger.warning(
                        f"Auto-fallback for user {user_id}: {best_alternative['description']}"
                    )
                else:
                    raise BudgetExceededException("预算不足且无可用替代方案")

            # 执行原始函数
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                # 记录成功的成本
                actual_cost = result.get('actual_cost', request_details.get('estimated_cost', 0))
                await cost_controller.record_actual_cost(user_id, request_details, actual_cost)
                return result
            except Exception as e:
                # 记录失败（部分成本可能已产生）
                processing_time = (datetime.now() - start_time).total_seconds()
                partial_cost = min(processing_time * 0.01, request_details.get('estimated_cost', 0) * 0.3)
                await cost_controller.record_actual_cost(user_id, request_details, partial_cost)
                raise e

        return wrapper
    return decorator

class BudgetExceededException(Exception):
    """预算超支异常"""
    pass
```

### 集成修改

**修改文件**: `apps/ai-service/core/ai_orchestrator.py`

```python
from .cost_control import EnhancedCostController, with_cost_control

class AIOrchestrator:
    def __init__(self):
        # 现有代码...
        self.cost_controller = EnhancedCostController(self.redis_client)

    @with_cost_control
    async def process_request(self, user_id: str, request_details: Dict[str, Any]):
        # 现有处理逻辑...
        pass
```

**修改专家代理使用成本控制**:

```python
# 在每个专家代理中添加
class PsychologyExpert:
    async def generate_framework(self, request):
        # 预算检查
        can_proceed, decision = await self.cost_controller.pre_request_budget_check(
            request.user_id,
            {'model': 'claude-3-sonnet', 'content_length': 1500, 'type': 'psychology_framework'}
        )

        if not can_proceed:
            # 使用降级方案或抛出异常
            alternatives = decision.get('alternative_options', [])
            if alternatives:
                fallback_params = alternatives[0]['parameters']
                return await self._generate_with_fallback(request, fallback_params)
            else:
                raise BudgetExceededException("预算不足")

        # 正常处理...
```

---

## 实施顺序

1. **首先创建情绪调节支持系统文件**
2. **然后创建中文韵律感检测算法文件**
3. **最后创建成本控制精确实施机制文件**
4. **按照集成指令修改现有文件**
5. **运行测试验证所有功能正常**

完成这三项优化后，Phase 3 预期评分将从 8.68 提升到 9.1+，满足通过标准。

---

## 预期结果

### 优化后的专家评分预期：

- **Dr. Sarah Chen (Psychology)**: 8.8 → 9.2 (情绪调节支持完善)
- **Prof. Li Ming (Literature)**: 8.5 → 9.1 (韵律感检测算法)
- **Alex Wang (Technical)**: 8.7 → 9.2 (成本控制精确化)

**总体评分**: 8.68 → 9.17 ✅ **通过标准**