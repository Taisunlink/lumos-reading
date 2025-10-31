"""
复杂度验证器 - P2-1
验证生成的故事内容是否符合年龄参数要求
"""

import re
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ValidationIssue(BaseModel):
    """验证问题"""
    severity: str  # "error" / "warning" / "info"
    category: str  # "content_structure" / "language_complexity" / "plot_complexity"
    message: str
    actual_value: Any
    expected_value: Any
    suggestion: str


class ValidationReport(BaseModel):
    """验证报告"""
    overall_pass: bool
    overall_score: float  # 0-1之间
    content_structure_score: float
    language_complexity_score: float
    plot_complexity_score: float
    issues: List[ValidationIssue]
    suggestions: List[str]
    metadata: Dict[str, Any] = {}


class ComplexityValidator:
    """
    复杂度验证器

    验证三个维度:
    1. 内容结构 (页数、字数)
    2. 语言复杂度 (句式、词汇)
    3. 情节复杂度 (角色、情节点)
    """

    def __init__(self):
        """初始化验证器"""
        self.common_chars_500 = set()  # 简化版：实际应加载500常用字
        self.common_chars_1500 = set()  # 简化版：实际应加载1500常用字
        self.common_chars_3000 = set()  # 简化版：实际应加载3000常用字

    def validate_story_complexity(
        self,
        story_content: Dict[str, Any],
        target_framework: Dict[str, Any]
    ) -> ValidationReport:
        """
        验证故事复杂度

        Args:
            story_content: 生成的故事内容
            target_framework: 目标教育框架参数

        Returns:
            ValidationReport
        """

        issues = []

        # 1. 验证内容结构
        content_issues, content_score = self._validate_content_structure(
            story_content,
            target_framework.get('content_structure', {})
        )
        issues.extend(content_issues)

        # 2. 验证语言复杂度
        language_issues, language_score = self._validate_language_complexity(
            story_content,
            target_framework.get('language_specifications', {})
        )
        issues.extend(language_issues)

        # 3. 验证情节复杂度
        plot_issues, plot_score = self._validate_plot_complexity(
            story_content,
            target_framework.get('plot_specifications', {})
        )
        issues.extend(plot_issues)

        # 计算总分 (加权平均)
        overall_score = (
            content_score * 0.4 +
            language_score * 0.4 +
            plot_score * 0.2
        )

        # 判断是否通过 (总分>=0.7 且没有error级别问题)
        has_errors = any(issue.severity == "error" for issue in issues)
        overall_pass = overall_score >= 0.7 and not has_errors

        # 生成建议
        suggestions = self._generate_suggestions(issues)

        return ValidationReport(
            overall_pass=overall_pass,
            overall_score=overall_score,
            content_structure_score=content_score,
            language_complexity_score=language_score,
            plot_complexity_score=plot_score,
            issues=issues,
            suggestions=suggestions,
            metadata={
                "total_issues": len(issues),
                "errors": sum(1 for i in issues if i.severity == "error"),
                "warnings": sum(1 for i in issues if i.severity == "warning"),
                "info": sum(1 for i in issues if i.severity == "info")
            }
        )

    def _validate_content_structure(
        self,
        story: Dict[str, Any],
        target: Dict[str, Any]
    ) -> tuple[List[ValidationIssue], float]:
        """验证内容结构（页数、字数）"""
        issues = []
        score = 1.0

        pages = story.get('pages', [])
        page_count = len(pages)

        # 目标参数
        target_page_count = target.get('page_count', 12)
        target_words_per_page = target.get('words_per_page', 30)

        # 1. 验证页数
        page_deviation = abs(page_count - target_page_count) / target_page_count
        if page_deviation > 0.2:  # 超过20%偏差
            severity = "error" if page_deviation > 0.3 else "warning"
            issues.append(ValidationIssue(
                severity=severity,
                category="content_structure",
                message=f"页数偏差过大",
                actual_value=page_count,
                expected_value=target_page_count,
                suggestion=f"建议调整为{target_page_count}页左右"
            ))
            score -= 0.3 if severity == "error" else 0.15

        # 2. 验证每页字数
        if pages:
            word_counts = [page.get('word_count', len(page.get('text', ''))) for page in pages]
            avg_words = sum(word_counts) / len(word_counts)

            words_deviation = abs(avg_words - target_words_per_page) / target_words_per_page
            if words_deviation > 0.15:  # 超过15%偏差
                severity = "error" if words_deviation > 0.25 else "warning"
                issues.append(ValidationIssue(
                    severity=severity,
                    category="content_structure",
                    message=f"每页平均字数偏差过大",
                    actual_value=round(avg_words, 1),
                    expected_value=target_words_per_page,
                    suggestion=f"建议每页保持在{int(target_words_per_page * 0.9)}-{int(target_words_per_page * 1.1)}字"
                ))
                score -= 0.3 if severity == "error" else 0.15

            # 3. 检查字数分布均匀性
            if len(word_counts) > 1:
                import statistics
                std_dev = statistics.stdev(word_counts)
                cv = std_dev / avg_words if avg_words > 0 else 0
                if cv > 0.3:  # 变异系数>0.3说明分布不均
                    issues.append(ValidationIssue(
                        severity="info",
                        category="content_structure",
                        message=f"各页字数分布不够均匀",
                        actual_value=f"变异系数{cv:.2f}",
                        expected_value="<0.3",
                        suggestion="建议各页字数更加均衡"
                    ))
                    score -= 0.05

        return issues, max(0.0, score)

    def _validate_language_complexity(
        self,
        story: Dict[str, Any],
        target: Dict[str, Any]
    ) -> tuple[List[ValidationIssue], float]:
        """验证语言复杂度（句式、词汇）"""
        issues = []
        score = 1.0

        pages = story.get('pages', [])
        if not pages:
            return issues, 0.0

        # 目标参数
        target_sentence_structure = target.get('sentence_structure', {
            'simple_sentences': 70,
            'compound_sentences': 25,
            'complex_sentences': 5
        })
        target_sentence_length = target.get('sentence_length', {'min': 6, 'max': 12, 'avg': 9})

        # 统计所有页面的句子
        all_sentences = []
        for page in pages:
            text = page.get('text', '')
            sentences = self._split_sentences(text)
            all_sentences.extend(sentences)

        if not all_sentences:
            issues.append(ValidationIssue(
                severity="error",
                category="language_complexity",
                message="故事内容为空",
                actual_value=0,
                expected_value=">0",
                suggestion="需要生成有效的故事内容"
            ))
            return issues, 0.0

        # 1. 分析句式结构
        sentence_types = self._analyze_sentence_types(all_sentences)
        total = sum(sentence_types.values())

        if total > 0:
            actual_structure = {
                'simple_sentences': round(sentence_types['simple'] / total * 100, 1),
                'compound_sentences': round(sentence_types['compound'] / total * 100, 1),
                'complex_sentences': round(sentence_types['complex'] / total * 100, 1)
            }

            # 检查句式分布偏差
            for key in ['simple_sentences', 'compound_sentences', 'complex_sentences']:
                actual = actual_structure[key]
                expected = target_sentence_structure[key]

                if expected > 0:
                    deviation = abs(actual - expected) / expected
                    if deviation > 0.3:  # 偏差>30%
                        severity = "warning" if deviation < 0.5 else "error"
                        issues.append(ValidationIssue(
                            severity=severity,
                            category="language_complexity",
                            message=f"{key}占比偏差过大",
                            actual_value=f"{actual}%",
                            expected_value=f"{expected}%",
                            suggestion=f"建议调整为{expected}%左右"
                        ))
                        score -= 0.15 if severity == "warning" else 0.25

        # 2. 分析句子长度
        sentence_lengths = [len(s) for s in all_sentences]
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            min_length = min(sentence_lengths)
            max_length = max(sentence_lengths)

            # 检查平均长度
            target_avg = target_sentence_length.get('avg', 9)
            if abs(avg_length - target_avg) > target_avg * 0.3:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="language_complexity",
                    message="平均句长偏差较大",
                    actual_value=round(avg_length, 1),
                    expected_value=target_avg,
                    suggestion=f"建议句长控制在{target_sentence_length.get('min', 6)}-{target_sentence_length.get('max', 12)}字"
                ))
                score -= 0.1

            # 检查是否有过长或过短的句子
            target_max = target_sentence_length.get('max', 12)
            over_length_count = sum(1 for l in sentence_lengths if l > target_max * 1.5)
            if over_length_count > len(sentence_lengths) * 0.1:  # 超过10%的句子过长
                issues.append(ValidationIssue(
                    severity="info",
                    category="language_complexity",
                    message=f"部分句子过长",
                    actual_value=f"{over_length_count}个句子超长",
                    expected_value="<10%",
                    suggestion="建议拆分长句"
                ))
                score -= 0.05

        return issues, max(0.0, score)

    def _validate_plot_complexity(
        self,
        story: Dict[str, Any],
        target: Dict[str, Any]
    ) -> tuple[List[ValidationIssue], float]:
        """验证情节复杂度（角色、情节点）"""
        issues = []
        score = 1.0

        characters = story.get('characters', [])
        pages = story.get('pages', [])

        # 目标参数
        target_character_count = target.get('character_count', 3)
        target_plot_points = target.get('plot_points', 5)

        # 1. 验证角色数量
        char_count = len(characters)
        if isinstance(target_character_count, dict):
            min_chars = target_character_count.get('min', 1)
            max_chars = target_character_count.get('max', 5)
            expected_chars = (min_chars + max_chars) // 2
        else:
            min_chars = max(1, target_character_count - 1)
            max_chars = target_character_count + 1
            expected_chars = target_character_count

        if char_count < min_chars or char_count > max_chars:
            severity = "error" if (char_count < min_chars - 1 or char_count > max_chars + 1) else "warning"
            issues.append(ValidationIssue(
                severity=severity,
                category="plot_complexity",
                message="角色数量不符合要求",
                actual_value=char_count,
                expected_value=f"{min_chars}-{max_chars}个",
                suggestion=f"建议设置{expected_chars}个左右的角色"
            ))
            score -= 0.2 if severity == "error" else 0.1

        # 2. 检查角色描述完整性
        for i, char in enumerate(characters):
            if not char.get('visual_description'):
                issues.append(ValidationIssue(
                    severity="warning",
                    category="plot_complexity",
                    message=f"角色{i+1}缺少视觉描述",
                    actual_value="无描述",
                    expected_value="详细的外貌描述",
                    suggestion="需要添加角色的详细视觉描述以保证插图一致性"
                ))
                score -= 0.05

        # 3. 简化的情节点检测（基于CROWD提示分布）
        pages_with_crowd = sum(1 for page in pages if page.get('crowd_prompt'))
        if isinstance(target_plot_points, dict):
            expected_points = (target_plot_points.get('min', 3) + target_plot_points.get('max', 8)) // 2
        else:
            expected_points = target_plot_points

        # 情节点大致等于CROWD互动点
        if abs(pages_with_crowd - expected_points) > expected_points * 0.5:
            issues.append(ValidationIssue(
                severity="info",
                category="plot_complexity",
                message="互动点数量可能不够",
                actual_value=pages_with_crowd,
                expected_value=expected_points,
                suggestion=f"建议增加互动点到{expected_points}个左右"
            ))
            score -= 0.05

        return issues, max(0.0, score)

    # ========== 辅助方法 ==========

    def _split_sentences(self, text: str) -> List[str]:
        """将文本分割为句子"""
        # 按中文句号、问号、感叹号分割
        sentences = re.split(r'[。！？]', text)
        # 过滤空句子，去除首尾空格
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _analyze_sentence_types(self, sentences: List[str]) -> Dict[str, int]:
        """
        分析句子类型

        简化规则：
        - 简单句: 无连词，单一主谓宾
        - 复合句: 包含并列/转折/因果连词（和、但是、因为、所以）
        - 复杂句: 包含从句标志（虽然、如果、当、因为...所以）
        """
        result = {'simple': 0, 'compound': 0, 'complex': 0}

        # 复合句标志词
        compound_markers = ['和', '但是', '可是', '或者', '而且', '然后']
        # 复杂句标志词
        complex_markers = ['虽然', '如果', '因为', '当', '只要', '无论', '即使']

        for sentence in sentences:
            # 检查复杂句
            if any(marker in sentence for marker in complex_markers):
                result['complex'] += 1
            # 检查复合句
            elif any(marker in sentence for marker in compound_markers):
                result['compound'] += 1
            # 默认简单句
            else:
                result['simple'] += 1

        return result

    def _generate_suggestions(self, issues: List[ValidationIssue]) -> List[str]:
        """根据问题生成改进建议"""
        suggestions = []

        # 按严重程度和类别汇总
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]

        if errors:
            suggestions.append(f"发现{len(errors)}个严重问题，需要优先修复")
            for error in errors[:3]:  # 最多列出3个
                suggestions.append(f"- {error.message}: {error.suggestion}")

        if warnings:
            suggestions.append(f"发现{len(warnings)}个警告，建议改进")
            for warning in warnings[:2]:  # 最多列出2个
                suggestions.append(f"- {warning.message}: {warning.suggestion}")

        if not errors and not warnings:
            suggestions.append("故事质量良好，符合所有标准")

        return suggestions

    def get_summary_statistics(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """获取故事的统计摘要"""
        pages = story.get('pages', [])
        characters = story.get('characters', [])

        if not pages:
            return {"error": "故事内容为空"}

        # 统计字数
        word_counts = [page.get('word_count', len(page.get('text', ''))) for page in pages]
        total_words = sum(word_counts)
        avg_words = total_words / len(word_counts) if word_counts else 0

        # 统计句子
        all_sentences = []
        for page in pages:
            sentences = self._split_sentences(page.get('text', ''))
            all_sentences.extend(sentences)

        sentence_types = self._analyze_sentence_types(all_sentences)
        total_sentences = sum(sentence_types.values())

        return {
            "page_count": len(pages),
            "character_count": len(characters),
            "total_words": total_words,
            "avg_words_per_page": round(avg_words, 1),
            "total_sentences": total_sentences,
            "sentence_structure": {
                "simple": f"{sentence_types['simple']/total_sentences*100:.1f}%" if total_sentences > 0 else "0%",
                "compound": f"{sentence_types['compound']/total_sentences*100:.1f}%" if total_sentences > 0 else "0%",
                "complex": f"{sentence_types['complex']/total_sentences*100:.1f}%" if total_sentences > 0 else "0%"
            },
            "avg_sentence_length": round(sum(len(s) for s in all_sentences) / len(all_sentences), 1) if all_sentences else 0,
            "pages_with_illustration": sum(1 for p in pages if p.get('illustration_prompt') or p.get('illustration_url')),
            "pages_with_crowd": sum(1 for p in pages if p.get('crowd_prompt'))
        }
