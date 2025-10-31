"""
整合测试 - 端到端测试完整的故事生成流程

测试目标:
1. 完整P0+P1+P2流程测试
2. 验证各个改进点实际效果
3. 性能基准测试
"""

import pytest
import sys
import os
import time
from typing import Dict, Any

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'ai-service'))

from agents.psychology.age_parameters import AgeGroupParameters
from agents.psychology.expert import EducationalFramework, CROWDStrategy
from agents.story_creation.expert import StoryContent, StoryPage, Character
from agents.quality_control.complexity_validator import ComplexityValidator


class TestAgeParametersIntegration:
    """测试P0-2: 年龄参数系统集成"""

    def test_age_parameters_coverage(self):
        """测试年龄参数覆盖所有年龄段"""

        print("\n📊 测试年龄参数系统")
        print("-" * 60)

        test_ages = [3, 4, 5, 6, 7, 8, 9, 10, 11]

        for age in test_ages:
            params = AgeGroupParameters.get_parameters(age)

            # 验证核心参数存在
            assert 'age_range' in params
            assert 'page_count' in params
            assert 'words_per_page' in params
            assert 'sentence_structure' in params
            assert 'sentence_length' in params

            # 验证数值合理性
            assert params['page_count']['recommended'] > 0
            assert params['words_per_page']['recommended'] > 0
            assert params['total_story_length']['recommended'] > 0

            print(f"✅ 年龄{age}岁: {params['age_range']}, "
                  f"{params['page_count']['recommended']}页, "
                  f"{params['words_per_page']['recommended']}字/页")

        print()

    def test_age_progression(self):
        """测试年龄递增时参数递增"""

        print("📈 测试年龄参数递增性")
        print("-" * 60)

        age_3_5 = AgeGroupParameters.get_parameters(4)
        age_6_8 = AgeGroupParameters.get_parameters(7)
        age_9_11 = AgeGroupParameters.get_parameters(10)

        # 页数递增
        assert age_3_5['page_count']['recommended'] < age_6_8['page_count']['recommended']
        assert age_6_8['page_count']['recommended'] < age_9_11['page_count']['recommended']

        # 字数递增
        assert age_3_5['words_per_page']['recommended'] < age_6_8['words_per_page']['recommended']
        assert age_6_8['words_per_page']['recommended'] < age_9_11['words_per_page']['recommended']

        # 复杂句占比递增
        assert age_3_5['sentence_structure']['complex_sentences'] <= age_6_8['sentence_structure']['complex_sentences']
        assert age_6_8['sentence_structure']['complex_sentences'] <= age_9_11['sentence_structure']['complex_sentences']

        print("✅ 年龄参数正确递增")
        print()


class TestStoryCreationIntegration:
    """测试P1: Story Creator集成"""

    def test_story_content_validation(self):
        """测试故事内容满足基本要求"""

        print("📖 测试故事内容生成")
        print("-" * 60)

        # 模拟一个符合标准的3-5岁故事
        params = AgeGroupParameters.get_parameters(4)

        characters = [
            Character(
                name="小兔子",
                description="活泼可爱的小兔子",
                personality="好奇、友善",
                visual_description="白色毛发，粉色长耳朵，大眼睛，穿蓝色背心",
                role_in_story="主角"
            )
        ]

        pages = []
        for i in range(14):  # 3-5岁推荐14页
            page = StoryPage(
                page_number=i + 1,
                text=f"这是第{i+1}页。小兔子很开心。它在森林里玩耍。" * 2,  # 约28字
                illustration_prompt=(
                    f"场景: 白天的晴朗，在森林空地，明亮温暖的光线。"
                    f"角色: 小兔子（白色毛发，粉色长耳朵，大眼睛，穿蓝色背心）正在玩耍。"
                    f"动作: 小兔子正在跳跃。"
                    f"情绪: 角色表现出开心的情绪，欢快愉悦的氛围，充满正能量。"
                    f"艺术风格: watercolor儿童插画风格，warm and bright色调，画面简洁清晰，"
                    f"色彩鲜艳明快，柔和的线条，卡通化的形象，适合3-5岁儿童，温馨友好。"
                ),
                crowd_prompt={"type": "Completion", "text": "小兔子喜欢__"} if i % 2 == 0 else None,
                reading_time_seconds=30,
                word_count=28
            )
            pages.append(page)

        story = StoryContent(
            title="小兔子的快乐一天",
            moral_theme="快乐与友谊",
            pages=pages,
            characters=characters,
            vocabulary_targets=["开心", "玩耍", "朋友"],
            extension_activities=["讨论快乐的来源"],
            cultural_elements=["友爱互助"]
        )

        # 验证基本结构
        assert story.title is not None
        assert len(story.pages) == 14
        assert len(story.characters) >= 1

        # 验证每页
        for page in story.pages:
            assert len(page.text) > 0
            assert len(page.illustration_prompt) > 100  # P1-3: 详细提示词
            assert page.word_count > 0

        # 验证角色描述
        for char in story.characters:
            assert len(char.visual_description) > 10  # 有详细视觉描述

        print(f"✅ 故事包含{len(story.pages)}页，{len(story.characters)}个角色")
        print(f"✅ 平均提示词长度: {sum(len(p.illustration_prompt) for p in story.pages) / len(story.pages):.0f}字")
        print()

        return story


class TestQualityValidationIntegration:
    """测试P2: 质量验证集成"""

    def test_validator_on_good_story(self):
        """测试验证器对符合标准的故事"""

        print("✅ 测试质量验证器（符合标准的故事）")
        print("-" * 60)

        validator = ComplexityValidator()

        # 创建符合标准的故事
        story_content = {
            "title": "小兔子找朋友",
            "pages": [
                {
                    "page_number": i + 1,
                    "text": "小兔子很开心。它在森林里玩。今天天气真好。" * 2,
                    "illustration_prompt": "详细的插图描述" * 20,
                    "crowd_prompt": {"type": "Completion", "text": "测试"} if i % 2 == 0 else None,
                    "word_count": 30
                }
                for i in range(14)
            ],
            "characters": [
                {
                    "name": "小兔子",
                    "description": "可爱的小兔子",
                    "personality": "活泼",
                    "visual_description": "白色毛发，粉色长耳朵，大眼睛，穿蓝色背心",
                    "role_in_story": "主角"
                },
                {
                    "name": "小鸟",
                    "description": "友善的小鸟",
                    "personality": "热心",
                    "visual_description": "黄色羽毛，小小的嘴巴，明亮的眼睛",
                    "role_in_story": "配角"
                }
            ]
        }

        target_framework = {
            "content_structure": {
                "page_count": 14,
                "words_per_page": 30,
                "total_words": 420
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

        # 显示结果
        print(f"   总分: {report.overall_score:.2f}")
        print(f"   内容结构分: {report.content_structure_score:.2f}")
        print(f"   语言复杂度分: {report.language_complexity_score:.2f}")
        print(f"   情节复杂度分: {report.plot_complexity_score:.2f}")
        print(f"   问题数量: {len(report.issues)}")
        print(f"   是否通过: {report.overall_pass}")

        if report.issues:
            print("\n   发现的问题:")
            for issue in report.issues[:3]:
                print(f"   - [{issue.severity}] {issue.message}")

        print()

        return report

    def test_validator_on_bad_story(self):
        """测试验证器对不符合标准的故事"""

        print("⚠️  测试质量验证器（不符合标准的故事）")
        print("-" * 60)

        validator = ComplexityValidator()

        # 创建明显不符合标准的故事（只有5页，字数过少）
        story_content = {
            "title": "测试",
            "pages": [
                {
                    "page_number": i + 1,
                    "text": "短文本。",
                    "word_count": 5
                }
                for i in range(5)
            ],
            "characters": []
        }

        target_framework = {
            "content_structure": {
                "page_count": 14,
                "words_per_page": 30
            },
            "language_specifications": {
                "sentence_structure": {"simple_sentences": 90, "compound_sentences": 10, "complex_sentences": 0}
            },
            "plot_specifications": {
                "character_count": 2
            }
        }

        report = validator.validate_story_complexity(story_content, target_framework)

        print(f"   总分: {report.overall_score:.2f}")
        print(f"   是否通过: {report.overall_pass}")
        print(f"   问题数量: {len(report.issues)}")

        # 应该检测到多个问题
        assert len(report.issues) > 0
        assert not report.overall_pass  # 应该不通过

        print("\n   检测到的问题:")
        for issue in report.issues:
            print(f"   - [{issue.severity}] {issue.message}: {issue.suggestion}")

        print("\n✅ 验证器正确检测到不合格内容")
        print()


class TestEndToEndIntegration:
    """端到端集成测试"""

    def test_complete_flow_simulation(self):
        """模拟完整的生成和验证流程"""

        print("\n" + "="*60)
        print("🔄 端到端完整流程测试")
        print("="*60 + "\n")

        start_time = time.time()

        # Step 1: 获取年龄参数
        print("步骤 1: 获取年龄参数")
        age = 4
        params = AgeGroupParameters.get_parameters(age)
        print(f"✅ 获取到{params['age_range']}参数: "
              f"{params['page_count']['recommended']}页, "
              f"{params['words_per_page']['recommended']}字/页\n")

        # Step 2: 模拟Psychology Expert生成框架
        print("步骤 2: Psychology Expert生成框架")
        crowd_strategy = CROWDStrategy(
            completion_prompts=["小兔子喜欢__"] * 5,
            recall_questions=["小兔子在哪里？"] * 5,
            open_ended_prompts=["你喜欢小兔子吗？"] * 5,
            wh_questions=["为什么？"] * 5,
            distancing_connections=["你见过兔子吗？"] * 5
        )

        framework = EducationalFramework(
            age_group=params['age_range'],
            cognitive_stage=params['cognitive_stage'],
            attention_span_target=5,
            learning_objectives=["情绪识别", "简单友谊"],
            crowd_strategy=crowd_strategy,
            interaction_density="medium",
            safety_considerations=["积极正面"],
            cultural_adaptations=["中华文化"],
            parent_guidance=["鼓励表达"]
        )
        print("✅ 框架生成完成\n")

        # Step 3: 模拟Story Creator生成故事
        print("步骤 3: Story Creator生成故事")

        characters = [
            Character(
                name="小兔子",
                description="可爱的白色小兔子",
                personality="活泼好奇",
                visual_description="白色毛发，粉色长耳朵，大眼睛，穿蓝色背心",
                role_in_story="主角"
            )
        ]

        pages = []
        target_pages = params['page_count']['recommended']
        target_words = params['words_per_page']['recommended']

        for i in range(target_pages):
            # 生成约目标字数的文本
            text = f"小兔子住在森林里。它每天都很开心。今天它想去探险。" * (target_words // 20 + 1)
            text = text[:target_words + 5]  # 约目标字数

            # P1-3: 增强后的插图提示词（5要素）
            illustration_prompt = (
                f"场景: {'清晨' if i < 5 else '午后'}的晴朗，在森林空地，明亮温暖的光线。"
                f"角色: 小兔子（白色毛发，粉色长耳朵，大眼睛，穿蓝色背心）正在{'跳跃' if i % 2 == 0 else '玩耍'}。"
                f"动作: 小兔子正在{'追逐蝴蝶' if i % 3 == 0 else '探索森林'}。"
                f"情绪: 角色表现出开心的情绪，欢快愉悦的氛围，充满正能量。"
                f"艺术风格: watercolor儿童插画风格，warm and bright色调，画面简洁清晰，"
                f"色彩鲜艳明快，柔和的线条，卡通化的形象，适合3-5岁儿童，温馨友好，无任何恐怖或暴力元素。"
            )

            page = StoryPage(
                page_number=i + 1,
                text=text,
                illustration_prompt=illustration_prompt,
                crowd_prompt={"type": "Completion", "text": framework.crowd_strategy.completion_prompts[i % 5]} if i % 2 == 0 else None,
                reading_time_seconds=30,
                word_count=len(text)
            )
            pages.append(page)

        story = StoryContent(
            title="小兔子的森林探险",
            moral_theme="勇气与探索",
            pages=pages,
            characters=characters,
            vocabulary_targets=["森林", "探险", "勇气"],
            extension_activities=["讨论勇气的重要性"],
            cultural_elements=["勇于探索未知"]
        )

        print(f"✅ 故事生成完成: {story.title}")
        print(f"   - 页数: {len(story.pages)}")
        print(f"   - 角色数: {len(story.characters)}")
        print(f"   - 平均字数/页: {sum(p.word_count for p in story.pages) / len(story.pages):.1f}")
        print(f"   - 平均提示词长度: {sum(len(p.illustration_prompt) for p in story.pages) / len(story.pages):.0f}字\n")

        # Step 4: 质量验证
        print("步骤 4: 质量验证")
        validator = ComplexityValidator()

        story_dict = {
            "title": story.title,
            "pages": [p.dict() for p in story.pages],
            "characters": [c.dict() for c in story.characters]
        }

        framework_dict = {
            "content_structure": {
                "page_count": params['page_count']['recommended'],
                "words_per_page": params['words_per_page']['recommended']
            },
            "language_specifications": {
                "sentence_structure": params['sentence_structure'],
                "sentence_length": params['sentence_length']
            },
            "plot_specifications": {
                "character_count": params['character_count'],
                "plot_points": params['plot_points']
            }
        }

        report = validator.validate_story_complexity(story_dict, framework_dict)

        print(f"✅ 验证完成:")
        print(f"   - 总分: {report.overall_score:.2f}")
        print(f"   - 内容结构: {report.content_structure_score:.2f}")
        print(f"   - 语言复杂度: {report.language_complexity_score:.2f}")
        print(f"   - 情节复杂度: {report.plot_complexity_score:.2f}")
        print(f"   - 是否通过: {'✅ 通过' if report.overall_pass else '❌ 不通过'}")
        print(f"   - 问题数量: {len(report.issues)}")

        if report.issues:
            print("\n   发现的问题:")
            for issue in report.issues[:3]:
                print(f"   - [{issue.severity}] {issue.message}")

        # Step 5: 获取统计摘要
        print("\n步骤 5: 统计摘要")
        stats = validator.get_summary_statistics(story_dict)
        print(f"   - 总页数: {stats['page_count']}")
        print(f"   - 总字数: {stats['total_words']}")
        print(f"   - 平均字数/页: {stats['avg_words_per_page']}")
        print(f"   - 句式分布: 简单{stats['sentence_structure']['simple']}, "
              f"复合{stats['sentence_structure']['compound']}, "
              f"复杂{stats['sentence_structure']['complex']}")
        print(f"   - 平均句长: {stats['avg_sentence_length']}字")
        print(f"   - 带插图页数: {stats['pages_with_illustration']}")
        print(f"   - 带互动页数: {stats['pages_with_crowd']}")

        elapsed_time = time.time() - start_time
        print(f"\n⏱️  总耗时: {elapsed_time:.2f}秒")

        print("\n" + "="*60)
        print("✅ 端到端测试完成！")
        print("="*60)


def run_all_integration_tests():
    """运行所有整合测试"""

    print("\n" + "="*70)
    print("🧪 开始整合测试")
    print("="*70)

    try:
        # Test 1: 年龄参数
        test_age = TestAgeParametersIntegration()
        test_age.test_age_parameters_coverage()
        test_age.test_age_progression()

        # Test 2: Story创建
        test_story = TestStoryCreationIntegration()
        test_story.test_story_content_validation()

        # Test 3: 质量验证
        test_quality = TestQualityValidationIntegration()
        test_quality.test_validator_on_good_story()
        test_quality.test_validator_on_bad_story()

        # Test 4: 端到端
        test_e2e = TestEndToEndIntegration()
        test_e2e.test_complete_flow_simulation()

        print("\n" + "="*70)
        print("✅✅✅ 所有整合测试通过！ ✅✅✅")
        print("="*70 + "\n")

        return True

    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ 测试失败: {str(e)}")
        print("="*70 + "\n")
        raise


if __name__ == "__main__":
    run_all_integration_tests()
