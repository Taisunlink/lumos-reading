# LumosReading｜生产依据与方法学 v1.0

> 适用对象：编辑、插画、工程、LLM 配置与审校团队  
> 目的：将“内容规格/心理学指引/LLM 专家矩阵与门控”系统化，形成可复用、可追踪、可验收的生产链路。

---

## 版本信息
- 版本：v1.0  
- 状态：可执行首版  
- 变更日志：
  - v1.0：整合用户画像、语言形态、故事分类、写作卡、门控矩阵、客户定制（主人公一致性/禁忌）

---

## 总体方法学（五层架构）
1. **基础规范层**：年龄分级、语言模式、故事分类（行业分类×SEL×叙事原型）。
2. **客户定制层**：品牌/口吻、**Series Bible（主人公与世界观）**、**禁忌/敏感控制**、地区文化适配矩阵。
3. **生产流水线层**：多角色 LLM 生成→专家门控→一致性与安全检查→插图引导卡。
4. **质量保障层**：自动化指标（词汇/句法/时长）+ 人工抽检 + 事实核查（科普/非虚构）。
5. **发布与运营层**：多设备适配、A/B 实验、阅读行为埋点与仪表盘。

---

## 客户定制规范（必须项）

### 1) 品牌与口吻（Brand Brief）
- 价值观与禁区：如“成长/合作/多元”，禁止“羞辱/恐吓式教育”。
- 文风：温暖/俏皮/纪实；幽默密度；节奏快慢。
- 语言：中文（简/繁）、英文（US/UK），或双语模式（对照/行内/交替）。

### 2) **Series Bible（系列设定文档）**
- **世界观**：时间/地点/规则（如魔法/科学设定）。
- **角色簇**：主角/配角的固定属性与可变属性（见下方“人物卡字段”）。
- **叙事调性**：冲突强度阈值、喜剧/抒情/探险比重。
- **一致性约束**：每集最大可变动条目，连续性缺口的补救原则（“上集回顾”的叙事钩子）。

**人物卡字段（建议）**
```yaml
character_id: string
name_cn: string
name_en: string
age: 6
traits: ["curious", "empathetic", "brave"]
fixed_assets: { pet: "豆豆", backpack_color: "yellow" }
changeable_traits_rules:
  - trait: bravery
    change_rate: "slow"  # slow / medium / fast
    allowed_events: ["help_friend", "face_small_fear"]
relationships:
  best_friend_id: char_102
  family: { mother: "温柔", father: "幽默" }
speech_style: { cn: "短句+拟声", en: "simple present+dialogue" }
visual_cues: { hair: "short", accessory: "star pin" }
```

### 3) **禁忌与敏感控制表（Age-Safe）**
> 原则：**可描写 ≠ 可模仿**。低龄段避免可模仿的危险情节；高龄段如涉及，必须“危害—纠正—安全”三段式呈现。

| 类目 | 3–4 岁 | 5–6 岁 | 7–9 岁 | 9–12 岁 | 备注 |
|---|---|---|---|---|---|
| 武器/暴力 | 禁止 | 禁止 | 轻度隐喻（不鼓励） | 冲突限度可控 | 不出现血腥/伤害细节 |
| 恐惧/惊吓 | 禁止强惊吓 | 轻惊吓+安抚 | 可有紧张情节 | 紧张后有复原 | 输出稳定策略 |
| 医疗/危险行为 | 禁止可模仿 | 禁止可模仿 | 如需出现→**安全指引** | 同左 | 不演示操作步骤 |
| 欺凌/歧视 | 不呈现 | 仅以“误会—道歉” | 可呈现→**反欺凌路径** | 同左 | 角色不被羞辱定型 |
| 商业植入 | 禁止 | 禁止 | 明示且稀疏 | 明示且稀疏 | 不影响叙事主线 |
| 文化敏感 | 本地化 | 本地化 | 多元呈现 | 多元呈现 | 见“地区文化适配矩阵” |

### 4) 地区文化适配矩阵（示例）
- 术语/节日：春节/中秋 ↔ Holidays（Christmas/Easter），同主题不同呈现。
- 单位/用语：米/千克 ↔ feet/pounds；“妈妈/爸比”↔“Mom/Dad”。
- 角色多元：家庭结构、肤色与服饰的包容性清单。

---

## 内容规格与“写作卡”（可直接投喂 LLM）

### 年龄段规格（摘要）
| 年龄/段 | 单册时长 | 总字数（CN/EN） | 句式 | 视觉占比 | 互动 |
|---|---|---|---|---|---|
| 3–4 | 5–6 min | 120–250 / 80–160 | 重复/押韵/短句 | 图≥70% | 每页 ≤1 引导 |
| 5–6 | 6–8 min | 250–450 / 160–300 | 简单复合/对话 | 图≈60% | 预测/情绪命名 |
| 7–9 | 8–12 min | 450–900 / 300–700 | 因果/转折/复合 | 图≈40–50% | 线索搜寻 |
| 9–12 | 10–15 min | 900–1500 / 700–1200 | 多从句/信息型 | 图≤40% | 观点表达 |

### 写作卡（Writer Card, YAML）
```yaml
project_id: lumosreading
series_id: "sprout_friends"
protagonist_id: "char_001"
release_locale: ["zh-CN", "en-US"]
age_band: "5-6"
language_mode: "BILINGUAL_INLINE"  # CN | EN | BILINGUAL_SIDE | BILINGUAL_INLINE | ALTERNATE
story_taxonomy:
  industry: ["Family", "Social_Emotions"]
  sel: ["SelfAwareness", "Relationship"]
  archetype: ["VoyageReturn"]
learning_targets:
  en_new_words: ["share", "brave"]  # ≤3，每词复现≥6次
  cn_keywords: ["分享", "勇敢"]
structure:
  pages: 12
  beats: ["设定", "小冲突", "尝试", "低谷", "解决", "余韵"]
constraints:
  max_sentence_len_en: 12
  max_subclauses: 1
  illustration_density: 0.6
  per_page_interaction: true
safety:
  forbidden_elements: ["weapon", "shaming", "danger_demo"]
  cultural_notes: ["春节元素", "同伴多元肤色"]
parent_cards: 4   # 结尾家长引导卡数量
```

### 插图引导卡（Illustration Cue, 每页）
```yaml
page: 3
scene: "厨房准备便当"
characters: ["主角", "妈妈", "宠物豆豆"]
key_props: ["黄背包", "星星发卡"]
mood: "温暖、早晨光"
composition: "中景+45°俯视，食材呈半圆构图"
color_temp: "暖色偏金"
action: "主角犹豫要不要多装一个苹果，用于分享"
```

---

## LLM 生产—审校“专家矩阵”与门控

### 角色链（建议七步）
1. **叙事策划器（PM/Writer）**：三幕式大纲+每页要点+互动位点。  
2. **语言控制器（NLP）**：分级词表/句长约束；双语草案；标注新词复现位置。  
3. **心理/教育门（Psych/SEL）**：SEL 目标是否“行为化”；生成家长引导卡。  
4. **文化与多元门（DEI）**：包容性与刻板印象检查；地区化建议。  
5. **事实/科普门（SME）**：非虚构与科普事实核验；引用来源。  
6. **安全门（Safety）**：禁忌元素扫描；“可描写≠可模仿”规则；危险情节三段式。  
7. **一致性门（Continuity）**：与 Series Bible 比对；人物固定资产/口吻/视觉锚一致。

### 门控矩阵（摘要）
| Gate | 自动规则 | 人工抽检 | 通过条件 | 失败处理 |
|---|---|---|---|---|
| NLP | 新词≤3、复现≥6、句长≤阈值 | 10% 抽读 | 指标全绿 | 回写提示词并重生 |
| Psych | 每幕≥1 个可观察 SEL 行为 | 关键页验读 | 明确“识别→策略→复原” | 标注缺口并补写 |
| DEI | 多元标签齐全，无贬损词 | 角色/场景审图 | 清单通过 | 替换措辞/画面 |
| SME | 引用≥1（非虚构） | 医学/科学条目 | 引用真实可查 | 标注来源并更正 |
| Safety | 禁区零命中 | 高风险页全读 | 零命中 | 移除/改写情节 |
| Continuity | 人物卡一致性≥95% | 起始/结尾页 | 锚点吻合 | 走“回顾钩子”修正 |

---

## 元数据 Schema（含客户定制字段）
```json
{
  "id": "string",
  "title": {"cn": "string", "en": "string"},
  "age_band": "3-4|5-6|7-9|9-12",
  "reading_time_min": 8,
  "language_mode": "CN|EN|BILINGUAL_SIDE|BILINGUAL_INLINE|ALTERNATE",
  "themes": ["Family","Social_Emotions"],
  "sel_tags": ["SelfAwareness","Relationship"],
  "narrative_archetype": ["VoyageReturn"],
  "word_count": {"cn": 380, "en": 240},
  "sentence_stats": {"avg_len_en": 9, "max_subclauses": 1},
  "vocab_targets": {"en_new_words": ["share","brave"], "cn_keywords": ["分享","勇敢"]},
  "phonics": {"phase": "CVC", "review_graphemes": ["sh","br"]},
  "pinyin_enabled": true,
  "illustration_density": 0.6,
  "interaction": {"per_page_prompt": true, "parent_cards": 4},
  "audio": {"cn": true, "en": true, "speeds": ["slow","normal","fast"]},
  "localization": {"script": "SC|TC", "accent_en": "US|UK"},
  "continuity": {
    "series_id": "sprout_friends",
    "protagonist_id": "char_001",
    "series_bible_version": "1.0",
    "fixed_assets": {"backpack_color": "yellow"}
  },
  "safety": {
    "forbidden_elements": ["weapon","shaming","danger_demo"],
    "depiction_vs_endorsement": true,
    "age_safety_rule": "3-4_strict"
  },
  "copyright": {"author": "", "illustrator": ""}
}
```

---

## CI/CD 与验收
- **Schema 校验**：JSON Schema + 必填字段 + 枚举检查。
- **可读性**：自动统计新词、复现次数、英文句长、中文句段长度；TTS 试读时长应在目标±15%。
- **一致性**：比对 Series Bible；人物固定资产/口吻差异报警。
- **安全扫描**：禁忌词/图像标签库；危险动作识别；文化偏见词库。
- **人工抽检**：Gate 通过后抽 10–20%，重点页全审（冲突/低谷/转折）。

---

## 发布与运营
- **多设备适配**：移动端优先；离线包含音频与插图；弱网降级（仅音频/低清图）。
- **A/B 试验**：语言模式（纯中文 vs 混合）、互动密度（每页 vs 每两页）。
- **指标**：完成率、平均阅读时长、家长卡互动率、新词复现达标率、复述正确率。
- **仪表盘**：年龄/主题/语言模式的分布与留存。

---

## 附：提示词（Prompt）骨架（节选）
```markdown
系统：你是一名少儿绘本编剧与双语教育设计师。根据【写作卡】生成 12 页绘本，每页输出：中文正文、英文正文、插图要点、家长引导提示（≤1 条）。严格遵守年龄段字数/句长/新词阈值与安全清单。结尾输出家长卡 4–5 条（开放式问题 + 引导要点）。

用户：这是写作卡：
<writer_card_yaml>
```

> **执行要求**：以上条款为生产与验收依据；如需突破（如主题试验），须在工单中写明理由与回滚预案。

