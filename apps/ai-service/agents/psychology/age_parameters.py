"""
科学的儿童阅读发展参数
基于:
- 皮亚杰认知发展理论
- 中国儿童阅读能力发展标准
- 国内外优秀儿童绘本分析
"""

from typing import Dict, List, Any

class AgeGroupParameters:
    """年龄分组阅读参数"""

    AGE_3_5 = {
        "age_range": "3-5岁",
        "cognitive_stage": "preoperational",
        "piaget_characteristics": [
            "自我中心思维",
            "泛灵论",
            "直觉思维",
            "符号功能出现"
        ],

        # ========== 内容结构参数 ==========
        "page_count": {
            "min": 12,
            "max": 16,
            "recommended": 14
        },
        "words_per_page": {
            "min": 20,
            "max": 50,
            "recommended": 30
        },
        "total_story_length": {
            "min": 240,
            "max": 800,
            "recommended": 420
        },

        # ========== 语言参数 ==========
        "sentence_structure": {
            "simple_sentences": 90,      # 简单句占90%
            "compound_sentences": 10,    # 复合句占10%
            "complex_sentences": 0       # 无复杂句
        },
        "sentence_length": {
            "min": 4,
            "max": 8,
            "avg": 6
        },
        "vocabulary_level": {
            "common_chars": 95,          # 95%常用字(500字表)
            "intermediate_chars": 5,
            "advanced_chars": 0
        },
        "vocabulary_enrichment": {
            "new_words_per_story": {"min": 3, "max": 8},
            "idioms_per_story": 0,
            "metaphor_usage": "避免抽象比喻"
        },

        # ========== 情节参数 ==========
        "plot_structure": "single_linear",  # 单一线性
        "plot_points": {"min": 3, "max": 5},
        "character_count": {"min": 1, "max": 3},
        "time_structure": "linear_only",
        "cause_effect_directness": "immediate",
        "conflict_types": ["简单问题", "日常挑战"],

        # ========== 主题参数 ==========
        "theme_complexity": "concrete_observable",
        "suitable_themes": [
            "日常生活", "情绪识别", "颜色形状",
            "动物特征", "家庭关系", "简单友谊",
            "分享玩具", "基础礼貌", "睡前仪式"
        ],
        "emotion_types": ["开心", "难过", "生气", "害怕"],

        # ========== CROWD互动 ==========
        "crowd_frequency": "每2-3页一次",
        "crowd_types_distribution": {
            "Completion": 40,
            "Recall": 30,
            "Wh_questions": 20,
            "Open_ended": 5,
            "Distancing": 5
        },
        "interaction_examples": {
            "Completion": ["小兔子喜欢__", "它要去找__"],
            "Recall": ["小兔子在哪里？", "它遇到了谁？"],
            "Wh_questions": ["小兔子为什么开心？"],
            "Open_ended": ["你喜欢小兔子吗？"],
            "Distancing": ["你见过兔子吗？"]
        }
    }

    AGE_6_8 = {
        "age_range": "6-8岁",
        "cognitive_stage": "concrete_operational_early",
        "piaget_characteristics": [
            "守恒概念形成",
            "可逆性思维",
            "去中心化",
            "分类能力发展",
            "逻辑推理初步"
        ],

        # ========== 内容结构参数 ==========
        "page_count": {
            "min": 16,
            "max": 24,
            "recommended": 20
        },
        "words_per_page": {
            "min": 50,
            "max": 120,
            "recommended": 80
        },
        "total_story_length": {
            "min": 800,
            "max": 2880,
            "recommended": 1600
        },

        # ========== 语言参数 ==========
        "sentence_structure": {
            "simple_sentences": 50,
            "compound_sentences": 40,
            "complex_sentences": 10
        },
        "sentence_length": {
            "min": 8,
            "max": 15,
            "avg": 11
        },
        "vocabulary_level": {
            "common_chars": 80,          # 1500字常用字
            "intermediate_chars": 18,
            "advanced_chars": 2
        },
        "vocabulary_enrichment": {
            "new_words_per_story": {"min": 5, "max": 10},
            "idioms_per_story": {"min": 2, "max": 5},
            "metaphor_usage": "简单具体比喻",
            "synonym_introduction": True
        },

        # ========== 情节参数 ==========
        "plot_structure": "dual_thread_simple",  # 双线叙事
        "plot_points": {"min": 5, "max": 8},
        "character_count": {"min": 3, "max": 5},
        "time_structure": "linear_with_flashback",
        "cause_effect_directness": "delayed_single_step",
        "conflict_types": [
            "人物间冲突",
            "内心冲突(简单)",
            "环境挑战",
            "目标追求"
        ],

        # ========== 主题参数 ==========
        "theme_complexity": "social_moral",
        "suitable_themes": [
            "友谊冲突与和解", "诚实与谎言", "勇气与恐惧",
            "合作竞争", "责任感", "换位思考", "规则意识",
            "自然探索", "基础科学", "文化传统", "家乡情怀"
        ],
        "emotion_types": [
            "开心", "难过", "生气", "害怕",
            "嫉妒", "骄傲", "羞愧", "同情", "感激"
        ],
        "moral_dilemma": "simple_binary",

        # ========== CROWD互动 ==========
        "crowd_frequency": "每1-2页一次",
        "crowd_types_distribution": {
            "Recall": 30,
            "Wh_questions": 30,
            "Open_ended": 20,
            "Distancing": 15,
            "Completion": 5
        },
        "interaction_examples": {
            "Recall": ["故事开始时发生了什么？", "小明为什么生气？"],
            "Wh_questions": ["为什么朋友会误会他？", "你觉得他应该怎么做？"],
            "Open_ended": ["如果是你会怎么办？", "这个故事让你想到了什么？"],
            "Distancing": ["你和朋友吵过架吗？", "你是怎么和好的？"],
            "Completion": ["要做个诚实的__", "友谊需要__"]
        }
    }

    AGE_9_11 = {
        "age_range": "9-11岁",
        "cognitive_stage": "concrete_operational_late",
        "piaget_characteristics": [
            "逻辑推理成熟",
            "系统分类能力",
            "空间时间概念完善",
            "守恒概念全面",
            "抽象思维萌芽"
        ],

        # ========== 内容结构参数 ==========
        "page_count": {
            "min": 24,
            "max": 40,
            "recommended": 32
        },
        "words_per_page": {
            "min": 100,
            "max": 250,
            "recommended": 150
        },
        "total_story_length": {
            "min": 2400,
            "max": 10000,
            "recommended": 4800
        },

        # ========== 语言参数 ==========
        "sentence_structure": {
            "simple_sentences": 20,
            "compound_sentences": 50,
            "complex_sentences": 30
        },
        "sentence_length": {
            "min": 12,
            "max": 25,
            "avg": 16
        },
        "vocabulary_level": {
            "common_chars": 60,          # 3000字常用字
            "intermediate_chars": 30,
            "advanced_chars": 10
        },
        "vocabulary_enrichment": {
            "new_words_per_story": {"min": 15, "max": 25},
            "idioms_per_story": {"min": 8, "max": 15},
            "metaphor_usage": "抽象比喻鼓励",
            "technical_terms": "年龄适当的专业词汇"
        },

        # ========== 情节参数 ==========
        "plot_structure": "multi_thread_complex",  # 多线交织
        "plot_points": {"min": 8, "max": 15},
        "character_count": {"min": 5, "max": 10},
        "character_development": "dynamic_arc",
        "time_structure": "nonlinear_allowed",
        "cause_effect_directness": "complex_chain",
        "conflict_types": [
            "人物间复杂冲突",
            "内心道德困境",
            "社会规则冲突",
            "理想与现实",
            "多方利益平衡"
        ],
        "foreshadowing": "multiple_layers",
        "plot_twists": {"min": 1, "max": 3},

        # ========== 主题参数 ==========
        "theme_complexity": "abstract_philosophical",
        "suitable_themes": [
            "正义与公平", "自由与责任", "个人与集体",
            "成长与迷茫", "理想与坚持", "失败与韧性",
            "多元文化", "历史传承", "科学探索", "环境保护",
            "复杂人际关系", "道德两难", "身份认同", "价值选择"
        ],
        "emotion_types": [
            "开心", "难过", "生气", "害怕",
            "嫉妒", "骄傲", "羞愧", "同情", "感激",
            "孤独", "矛盾", "迷茫", "释然", "遗憾", "敬畏"
        ],
        "moral_dilemma": "complex_gradient",
        "philosophical_questions": True,

        # ========== CROWD互动 ==========
        "crowd_frequency": "每1页一次",
        "crowd_types_distribution": {
            "Wh_questions": 35,
            "Open_ended": 30,
            "Distancing": 20,
            "Recall": 10,
            "Completion": 5
        },
        "critical_thinking": {
            "perspective_taking": True,
            "cause_analysis": "multi_factor",
            "prediction_questions": True,
            "ethical_discussion": True
        },
        "interaction_examples": {
            "Wh_questions": [
                "为什么主角会做出这样的选择？背后的原因可能有哪些？",
                "如果情况不同，结果会怎样？"
            ],
            "Open_ended": [
                "你认为什么是真正的正义？",
                "这个故事让你思考了什么人生问题？"
            ],
            "Distancing": [
                "在你的生活中，有没有遇到过类似的两难选择？",
                "你会如何平衡个人利益和集体利益？"
            ]
        }
    }

    @classmethod
    def get_parameters(cls, age: int) -> Dict[str, Any]:
        """
        根据年龄获取对应参数

        Args:
            age: 儿童年龄

        Returns:
            对应年龄段的完整参数字典
        """
        if age < 6:
            return cls.AGE_3_5
        elif age < 9:
            return cls.AGE_6_8
        else:
            return cls.AGE_9_11

    @classmethod
    def get_age_range_from_age(cls, age: int) -> str:
        """获取年龄范围字符串"""
        params = cls.get_parameters(age)
        return params['age_range']

    @classmethod
    def validate_story_structure(cls, age: int, page_count: int, words_per_page: float) -> Dict:
        """
        验证故事结构是否符合年龄标准

        Returns:
            {
                "valid": bool,
                "issues": List[str],
                "suggestions": List[str]
            }
        """
        params = cls.get_parameters(age)
        issues = []
        suggestions = []

        # 验证页数
        page_spec = params['page_count']
        if page_count < page_spec['min']:
            issues.append(f"页数过少: {page_count} < {page_spec['min']}")
            suggestions.append(f"建议增加到 {page_spec['recommended']} 页")
        elif page_count > page_spec['max']:
            issues.append(f"页数过多: {page_count} > {page_spec['max']}")
            suggestions.append(f"建议减少到 {page_spec['recommended']} 页")

        # 验证字数
        words_spec = params['words_per_page']
        if words_per_page < words_spec['min']:
            issues.append(f"每页字数过少: {words_per_page:.0f} < {words_spec['min']}")
            suggestions.append(f"建议增加到 {words_spec['recommended']} 字/页")
        elif words_per_page > words_spec['max']:
            issues.append(f"每页字数过多: {words_per_page:.0f} > {words_spec['max']}")
            suggestions.append(f"建议减少到 {words_spec['recommended']} 字/页")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
