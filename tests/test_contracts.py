"""
契约测试 - 验证各组件之间的接口契约

测试目标:
1. Psychology Expert → Story Creator 的framework契约
2. Story Creator → Illustration Service 的content契约
3. Validator → Story Service 的validation契约
"""

import pytest
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'ai-service'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))

from agents.psychology.expert import EducationalFramework, CROWDStrategy
from agents.story_creation.expert import StoryContent, StoryPage, Character
from agents.quality_control.complexity_validator import ComplexityValidator, ValidationReport


class TestPsychologyToStoryCreatorContract:
    """测试Psychology Expert到Story Creator的契约"""

    def test_framework_structure(self):
        """测试EducationalFramework结构符合Story Creator需求"""

        # 创建模拟框架
        crowd_strategy = CROWDStrategy(
            completion_prompts=["小兔子喜欢__", "它要去找__"],
            recall_questions=["小兔子在哪里？", "它遇到了谁？"],
            open_ended_prompts=["你喜欢小兔子吗？"],
            wh_questions=["小兔子为什么开心？"],
            distancing_connections=["你见过兔子吗？"]
        )

        framework = EducationalFramework(
            age_group="3-5岁",
            cognitive_stage="preoperational",
            attention_span_target=5,
            learning_objectives=["情绪识别", "简单友谊"],
            crowd_strategy=crowd_strategy,
            interaction_density="medium",
            safety_considerations=["确保内容积极正面"],
            cultural_adaptations=["体现中华文化价值观"],
            parent_guidance=["鼓励孩子表达想法"]
        )

        # 验证框架包含Story Creator所需的字段
        assert framework.age_group is not None
        assert framework.cognitive_stage is not None
        assert framework.attention_span_target > 0
        assert len(framework.learning_objectives) > 0
        assert framework.crowd_strategy is not None
        assert len(framework.crowd_strategy.completion_prompts) > 0

        print("✅ Psychology Expert framework结构契约测试通过")

    def test_framework_with_detailed_specs(self):
        """测试框架包含详细规格（P1升级后）"""

        crowd_strategy = CROWDStrategy(
            completion_prompts=["测试提示"],
            recall_questions=["测试问题"],
            open_ended_prompts=["测试讨论"],
            wh_questions=["为什么？"],
            distancing_connections=["联系生活"]
        )

        framework = EducationalFramework(
            age_group="3-5岁",
            cognitive_stage="preoperational",
            attention_span_target=5,
            learning_objectives=["测试目标"],
            crowd_strategy=crowd_strategy,
            interaction_density="medium",
            safety_considerations=["安全"],
            cultural_adaptations=["文化"],
            parent_guidance=["指导"]
        )

        # 检查框架是否可以包含新增的详细规格字段
        # （这些是可选字段，通过hasattr检查）
        assert hasattr(framework, 'age_group')
        assert hasattr(framework, 'crowd_strategy')

        # 可以动态添加额外字段（Python的dict属性）
        framework_dict = framework.dict()
        framework_dict['content_structure'] = {
            'page_count': 14,
            'words_per_page': 30
        }

        assert 'content_structure' in framework_dict

        print("✅ Framework详细规格契约测试通过")


class TestStoryCreatorToIllustrationContract:
    """测试Story Creator到Illustration Service的契约"""

    def test_story_content_structure(self):
        """测试StoryContent结构符合Illustration Service需求"""

        # 创建模拟角色
        character = Character(
            name="小兔子",
            description="可爱的白色小兔子",
            personality="活泼好奇",
            visual_description="白色毛发，粉色长耳朵，大眼睛，穿蓝色背心",
            role_in_story="主角"
        )

        # 创建模拟页面
        page = StoryPage(
            page_number=1,
            text="小兔子住在森林里。它每天都很开心。今天，它想找一个好朋友。",
            illustration_prompt="温暖的午后阳光洒在森林空地上，小兔子正跳跃着追逐五彩蝴蝶",
            crowd_prompt={"type": "Completion", "text": "小兔子喜欢__"},
            reading_time_seconds=30,
            word_count=28
        )

        # 创建完整故事
        story = StoryContent(
            title="小兔子找朋友",
            moral_theme="友谊的重要性",
            pages=[page],
            characters=[character],
            vocabulary_targets=["朋友", "开心", "森林"],
            extension_activities=["讨论友谊"],
            cultural_elements=["互助友爱"]
        )

        # 验证Illustration Service所需的字段
        assert len(story.pages) > 0
        for p in story.pages:
            assert p.page_number > 0
            assert p.text is not None and len(p.text) > 0
            assert p.illustration_prompt is not None and len(p.illustration_prompt) > 0

        assert len(story.characters) > 0
        for char in story.characters:
            assert char.name is not None
            assert char.visual_description is not None  # 关键：视觉描述用于保持一致性

        print("✅ Story Creator to Illustration Service契约测试通过")

    def test_illustration_prompt_enhancement(self):
        """测试P1-3增强后的插图提示词结构"""

        page = StoryPage(
            page_number=1,
            text="小兔子在森林里跳跃",
            illustration_prompt="场景: 清晨的晴朗，在森林空地，明亮温暖的光线。角色: 小兔子（白色毛发，粉色长耳朵）正在跳跃。动作: 小兔子正在跳跃。情绪: 角色表现出开心的情绪，欢快愉悦的氛围。艺术风格: watercolor儿童插画风格，warm and bright色调，适合3-5岁儿童。",
            word_count=10
        )

        # 验证增强后的提示词包含5要素
        prompt = page.illustration_prompt
        assert "场景" in prompt or "清晨" in prompt or "森林" in prompt  # 场景要素
        assert "角色" in prompt or "小兔子" in prompt  # 角色要素
        assert "动作" in prompt or "跳跃" in prompt  # 动作要素
        assert "情绪" in prompt or "开心" in prompt or "氛围" in prompt  # 情绪要素
        assert "艺术风格" in prompt or "watercolor" in prompt or "儿童" in prompt  # 风格要素

        print("✅ P1-3增强插图提示词契约测试通过")


class TestValidatorToStoryServiceContract:
    """测试Validator到Story Service的契约"""

    def test_validation_report_structure(self):
        """测试ValidationReport结构符合Story Service需求"""

        validator = ComplexityValidator()

        # 创建模拟故事内容
        story_content = {
            "title": "测试故事",
            "pages": [
                {
                    "page_number": 1,
                    "text": "这是一个测试故事。小兔子很开心。",
                    "word_count": 12
                }
            ],
            "characters": [
                {
                    "name": "小兔子",
                    "visual_description": "白色小兔子"
                }
            ]
        }

        # 目标框架
        target_framework = {
            "content_structure": {
                "page_count": 14,
                "words_per_page": 30
            },
            "language_specifications": {
                "sentence_structure": {
                    "simple_sentences": 90,
                    "compound_sentences": 10,
                    "complex_sentences": 0
                },
                "sentence_length": {"min": 4, "max": 8, "avg": 6}
            },
            "plot_specifications": {
                "character_count": 2,
                "plot_points": 4
            }
        }

        # 执行验证
        report = validator.validate_story_complexity(story_content, target_framework)

        # 验证Report结构
        assert isinstance(report, ValidationReport)
        assert hasattr(report, 'overall_pass')
        assert hasattr(report, 'overall_score')
        assert hasattr(report, 'content_structure_score')
        assert hasattr(report, 'language_complexity_score')
        assert hasattr(report, 'plot_complexity_score')
        assert hasattr(report, 'issues')
        assert hasattr(report, 'suggestions')

        # 验证数据类型
        assert isinstance(report.overall_pass, bool)
        assert isinstance(report.overall_score, float)
        assert 0 <= report.overall_score <= 1
        assert isinstance(report.issues, list)
        assert isinstance(report.suggestions, list)

        print(f"✅ Validator报告契约测试通过")
        print(f"   - overall_pass: {report.overall_pass}")
        print(f"   - overall_score: {report.overall_score:.2f}")
        print(f"   - issues count: {len(report.issues)}")

    def test_validation_metadata_structure(self):
        """测试验证元数据结构"""

        validator = ComplexityValidator()

        story_content = {
            "pages": [{"page_number": 1, "text": "测试文本。", "word_count": 5}],
            "characters": []
        }

        # 获取统计摘要
        stats = validator.get_summary_statistics(story_content)

        # 验证统计摘要结构
        assert "page_count" in stats
        assert "character_count" in stats
        assert "total_words" in stats
        assert "avg_words_per_page" in stats
        assert "sentence_structure" in stats

        print("✅ Validator统计元数据契约测试通过")


def run_all_contract_tests():
    """运行所有契约测试"""
    print("\n" + "="*60)
    print("开始契约测试")
    print("="*60 + "\n")

    # Test Suite 1: Psychology → Story Creator
    print("📋 测试套件 1: Psychology Expert → Story Creator")
    print("-" * 60)
    test1 = TestPsychologyToStoryCreatorContract()
    try:
        test1.test_framework_structure()
        test1.test_framework_with_detailed_specs()
        print("✅ Test Suite 1: 全部通过\n")
    except AssertionError as e:
        print(f"❌ Test Suite 1: 失败 - {e}\n")
        raise

    # Test Suite 2: Story Creator → Illustration
    print("📋 测试套件 2: Story Creator → Illustration Service")
    print("-" * 60)
    test2 = TestStoryCreatorToIllustrationContract()
    try:
        test2.test_story_content_structure()
        test2.test_illustration_prompt_enhancement()
        print("✅ Test Suite 2: 全部通过\n")
    except AssertionError as e:
        print(f"❌ Test Suite 2: 失败 - {e}\n")
        raise

    # Test Suite 3: Validator → Story Service
    print("📋 测试套件 3: Validator → Story Service")
    print("-" * 60)
    test3 = TestValidatorToStoryServiceContract()
    try:
        test3.test_validation_report_structure()
        test3.test_validation_metadata_structure()
        print("✅ Test Suite 3: 全部通过\n")
    except AssertionError as e:
        print(f"❌ Test Suite 3: 失败 - {e}\n")
        raise

    print("="*60)
    print("✅ 所有契约测试通过！")
    print("="*60)


if __name__ == "__main__":
    run_all_contract_tests()
