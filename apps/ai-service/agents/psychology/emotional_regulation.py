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
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "skill_name": self.skill_name,
            "description": self.description,
            "age_appropriate": self.age_appropriate,
            "practice_methods": self.practice_methods,
            "story_integration_hints": self.story_integration_hints,
            "parent_guidance": self.parent_guidance
        }

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
        for i, skill in enumerate(skills):
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

            priority_scores[i] = score

        # 选择得分最高的2-3个技能
        sorted_indices = sorted(range(len(skills)), key=lambda i: priority_scores.get(i, 0), reverse=True)
        return [skills[i] for i in sorted_indices[:3]]

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
