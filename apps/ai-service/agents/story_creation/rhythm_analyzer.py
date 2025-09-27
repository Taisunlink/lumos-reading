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
                    pinyin_list = pypinyin.pinyin(char, style=pypinyin.Style.TONE3)
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
