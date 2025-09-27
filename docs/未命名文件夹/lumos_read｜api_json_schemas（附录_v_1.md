# LumosRead｜API & JSON Schemas（附录 v1.0）

> 面向工程团队的可落地规范：用户档案、故事生成 I/O、插画一致性检查。遵循 JSON Schema Draft 2020-12；示例均可直接作为 Mock 数据使用。

---

## 0. 版本与通用约定
- **JSON Schema 版本**：`https://json-schema.org/draft/2020-12/schema`
- **命名**：`snake_case`（字段），`kebab-case`（URL 路由）。
- **i18n**：文本字段默认 `UTF-8`；`language` 使用 BCP-47（如 `zh-CN`, `en-US`）。
- **ID**：资源使用 `uuid`（v4）。
- **时间**：ISO-8601 UTC（示例：`2025-09-22T12:34:56Z`）。
- **分页**：cursor-based，参数 `cursor` 与 `limit`（默认 20，最大 100）。

---

## 1) 用户档案（User Profile）

### 1.1 Schema：`UserProfile`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://lumosread.app/schemas/user_profile.json",
  "title": "UserProfile",
  "type": "object",
  "required": ["user_id", "created_at", "guardian"],
  "properties": {
    "user_id": {"type": "string", "format": "uuid"},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "guardian": {
      "type": "object",
      "required": ["name", "email", "language"],
      "properties": {
        "name": {"type": "string", "minLength": 1, "maxLength": 80},
        "email": {"type": "string", "format": "email"},
        "phone": {"type": "string", "minLength": 6, "maxLength": 32},
        "language": {"type": "string", "pattern": "^[a-z]{2}(-[A-Z]{2})?$"},
        "timezone": {"type": "string", "default": "Asia/Shanghai"}
      }
    },
    "children": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["child_id", "nickname", "age", "language"],
        "properties": {
          "child_id": {"type": "string", "format": "uuid"},
          "nickname": {"type": "string", "minLength": 1, "maxLength": 40},
          "age": {"type": "integer", "minimum": 2, "maximum": 11},
          "gender": {"type": "string", "enum": ["male", "female", "unspecified"]},
          "language": {"type": "string", "pattern": "^[a-z]{2}(-[A-Z]{2})?$"},
          "reading_level": {"type": "string", "enum": ["pre-operational", "concrete-operational"]},
          "interests": {"type": "array", "items": {"type": "string"}, "maxItems": 10},
          "avoid_topics": {"type": "array", "items": {"type": "string"}, "maxItems": 15},
          "avoid_elements": {"type": "array", "items": {"type": "string"}, "maxItems": 15},
          "cognitive_notes": {"type": "string", "maxLength": 500}
        }
      }
    },
    "privacy": {
      "type": "object",
      "properties": {
        "data_minimization": {"type": "boolean", "default": true},
        "share_usage_for_improvement": {"type": "boolean", "default": false}
      }
    }
  }
}
```

### 1.2 示例（Minimal）
```json
{
  "user_id": "a2c1c1d9-3c4f-4d6e-b2ad-9e3f5f8a1234",
  "created_at": "2025-09-22T08:00:00Z",
  "guardian": {
    "name": "Ethan",
    "email": "ethan@example.com",
    "language": "zh-CN",
    "timezone": "Asia/Taipei"
  },
  "children": [
    {
      "child_id": "9d8b7c6a-5f4e-4a3b-9c2d-1e0fabc12345",
      "nickname": "可乐",
      "age": 5,
      "gender": "unspecified",
      "language": "zh-CN",
      "reading_level": "pre-operational",
      "interests": ["兔子", "太空"],
      "avoid_topics": ["死亡"],
      "avoid_elements": ["蜘蛛", "黑暗"]
    }
  ]
}
```

---

## 2) 故事生成（Story Generation）

### 2.1 输入 Schema：`StoryGenInput`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://lumosread.app/schemas/story_gen_input.json",
  "title": "StoryGenInput",
  "type": "object",
  "required": ["child_profile", "story_preferences", "safety_filters", "interaction_density"],
  "properties": {
    "child_profile": {
      "type": "object",
      "required": ["name", "age", "language", "cognitive_level"],
      "properties": {
        "name": {"type": "string", "minLength": 1, "maxLength": 40},
        "age": {"type": "integer", "minimum": 2, "maximum": 11},
        "gender": {"type": "string", "enum": ["male", "female", "unspecified"]},
        "language": {"type": "string", "pattern": "^[a-z]{2}(-[A-Z]{2})?$"},
        "cognitive_level": {"type": "string", "enum": ["pre-operational", "concrete-operational"]}
      }
    },
    "story_preferences": {
      "type": "object",
      "required": ["theme", "setting", "protagonist"],
      "properties": {
        "theme": {"type": "string", "enum": ["friendship", "courage", "sharing", "kindness", "perseverance"]},
        "setting": {"type": "string", "enum": ["forest", "ocean", "space", "castle", "city"]},
        "protagonist": {
          "type": "object",
          "required": ["type"],
          "properties": {
            "type": {"type": "string", "enum": ["animal", "child", "robot", "elf"]},
            "species": {"type": "string"},
            "traits": {"type": "array", "items": {"type": "string"}, "maxItems": 5}
          }
        },
        "companion": {"type": "string"},
        "reading_time_minutes": {"type": "integer", "minimum": 3, "maximum": 15}
      }
    },
    "safety_filters": {
      "type": "object",
      "properties": {
        "avoid_topics": {"type": "array", "items": {"type": "string"}},
        "avoid_elements": {"type": "array", "items": {"type": "string"}}
      }
    },
    "interaction_density": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
    "seed": {"type": "integer", "minimum": 0}
  }
}
```

### 2.2 输出 Schema：`StoryGenOutput`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://lumosread.app/schemas/story_gen_output.json",
  "title": "StoryGenOutput",
  "type": "object",
  "required": ["story_id", "title", "age_appropriateness", "reading_time", "pages", "interaction_summary"],
  "properties": {
    "story_id": {"type": "string", "format": "uuid"},
    "title": {"type": "string", "minLength": 1, "maxLength": 80},
    "age_appropriateness": {"type": "string", "pattern": "^\\d-\\d岁|\\d{1,2}-\\d{1,2}岁$"},
    "reading_time": {"type": "string", "pattern": "^\\d+-\\d+分钟$"},
    "language": {"type": "string", "pattern": "^[a-z]{2}(-[A-Z]{2})?$", "default": "zh-CN"},
    "pages": {
      "type": "array",
      "minItems": 3,
      "items": {
        "type": "object",
        "required": ["page_number", "text"],
        "properties": {
          "page_number": {"type": "integer", "minimum": 1},
          "text": {"type": "string", "minLength": 1},
          "word_count": {"type": "integer", "minimum": 1},
          "illustration": {
            "type": "object",
            "properties": {
              "prompt": {"type": "string"},
              "key_elements": {"type": "array", "items": {"type": "string"}},
              "color_palette": {"type": "array", "items": {"type": "string"}},
              "character_consistency_id": {"type": "string"},
              "seed": {"type": "integer"}
            }
          },
          "interaction": {
            "type": "object",
            "properties": {
              "type": {"type": "string", "enum": ["Completion", "Recall", "Open-ended", "Wh-question", "Distancing"]},
              "prompt": {"type": "string"},
              "timing": {"type": "string", "enum": ["during_reading", "after_reading"]},
              "blank": {"type": "string"},
              "suggested_response": {"type": "string"}
            }
          }
        }
      }
    },
    "interaction_summary": {
      "type": "object",
      "required": ["total_prompts", "prompt_types"],
      "properties": {
        "total_prompts": {"type": "integer", "minimum": 0},
        "prompt_types": {
          "type": "object",
          "additionalProperties": {"type": "integer", "minimum": 0}
        }
      }
    }
  }
}
```

### 2.3 请求示例（Input）
```json
{
  "child_profile": {"name": "小明", "age": 5, "language": "zh-CN", "cognitive_level": "pre-operational"},
  "story_preferences": {
    "theme": "friendship",
    "setting": "forest",
    "protagonist": {"type": "animal", "species": "rabbit", "traits": ["brave", "curious"]},
    "companion": "talking_owl",
    "reading_time_minutes": 6
  },
  "safety_filters": {"avoid_topics": ["死亡"], "avoid_elements": ["蜘蛛", "黑暗"]},
  "interaction_density": "medium",
  "seed": 42
}
```

### 2.4 返回示例（Output, 部分）
```json
{
  "story_id": "c3bb4a5e-4b7c-4f2d-8c9d-1d23456789ab",
  "title": "小兔子的森林冒险",
  "age_appropriateness": "4-6岁",
  "reading_time": "5-7分钟",
  "language": "zh-CN",
  "pages": [
    {
      "page_number": 1,
      "text": "在一片美丽的大森林里，住着一只勇敢的小兔子叫跳跳。",
      "word_count": 20,
      "illustration": {
        "prompt": "A brave little rabbit named Tiaotiao standing in a forest clearing, children's watercolor",
        "key_elements": ["rabbit", "forest", "morning_light"],
        "color_palette": ["green", "brown", "soft_yellow"],
        "character_consistency_id": "rabbit_tiaotiao_v1",
        "seed": 171
      }
    },
    {
      "page_number": 2,
      "text": "有一天早上，跳跳听到了一个奇怪的声音：‘咕咕，咕咕…’",
      "interaction": {
        "type": "Wh-question",
        "prompt": "宝贝，你觉得这个声音是从哪里来的呢？",
        "timing": "after_reading",
        "suggested_response": "引导孩子观察画面中的细节"
      }
    }
  ],
  "interaction_summary": {"total_prompts": 5, "prompt_types": {"Completion": 1, "Recall": 1, "Open-ended": 1, "Wh-question": 1, "Distancing": 1}}
}
```

---

## 3) 插画一致性检查（Illustration Consistency）

### 3.1 角色 Bible Schema：`CharacterBible`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://lumosread.app/schemas/character_bible.json",
  "title": "CharacterBible",
  "type": "object",
  "required": ["character_id", "name", "core_features", "color_palette", "proportions"],
  "properties": {
    "character_id": {"type": "string"},
    "name": {"type": "string"},
    "core_features": {"type": "array", "items": {"type": "string"}, "minItems": 3},
    "color_palette": {"type": "array", "items": {"type": "string"}, "minItems": 3},
    "proportions": {
      "type": "object",
      "properties": {
        "head_body_ratio": {"type": "number", "minimum": 0.1, "maximum": 3.0},
        "eye_size_ratio": {"type": "number", "minimum": 0.05, "maximum": 0.6}
      }
    },
    "lora_model_ref": {"type": "string"},
    "style_adapter": {"type": "string"}
  }
}
```

### 3.2 一致性检查输入：`IllustrationCheckInput`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://lumosread.app/schemas/illustration_check_input.json",
  "title": "IllustrationCheckInput",
  "type": "object",
  "required": ["character_bible", "image_assets"],
  "properties": {
    "character_bible": {"$ref": "https://lumosread.app/schemas/character_bible.json"},
    "image_assets": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["image_id", "url"],
        "properties": {
          "image_id": {"type": "string"},
          "url": {"type": "string", "format": "uri"},
          "features_detected": {"type": "array", "items": {"type": "string"}},
          "dominant_colors": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

### 3.3 一致性检查输出：`IllustrationCheckResult`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://lumosread.app/schemas/illustration_check_result.json",
  "title": "IllustrationCheckResult",
  "type": "object",
  "required": ["character_id", "overall_score", "feature_scores", "color_similarity", "proportion_check", "recommendations"],
  "properties": {
    "character_id": {"type": "string"},
    "overall_score": {"type": "number", "minimum": 0, "maximum": 1},
    "feature_scores": {
      "type": "object",
      "additionalProperties": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "color_similarity": {"type": "number", "minimum": 0, "maximum": 1},
    "proportion_check": {
      "type": "object",
      "properties": {
        "head_body_ratio_deviation": {"type": "number"},
        "eye_size_ratio_deviation": {"type": "number"}
      }
    },
    "recommendations": {"type": "array", "items": {"type": "string"}},
    "non_compliant_images": {"type": "array", "items": {"type": "string"}}
  }
}
```

### 3.4 API 端点建议
- `POST /v1/illustrations/consistency-check` → 输入 `IllustrationCheckInput`，返回 `IllustrationCheckResult`。
- `GET /v1/characters/{character_id}/bible` → 返回 `CharacterBible`。

---

## 4) REST API 设计（建议）

| Method | Path                                   | Req Body                 | Resp        | Notes |
|-------:|----------------------------------------|--------------------------|-------------|------|
|  POST  | /v1/users                               | UserProfile (minimal)    | UserProfile | 创建监护人与子女档案 |
|   GET  | /v1/users/{user_id}                     | –                        | UserProfile | 读取档案 |
|  POST  | /v1/stories/generate                    | StoryGenInput            | StoryGenOutput | 同步/异步均可；建议返回 `job_id` 支持轮询 |
|   GET  | /v1/stories/{story_id}                  | –                        | StoryGenOutput | 获取成品故事 |
|  POST  | /v1/illustrations/consistency-check     | IllustrationCheckInput   | IllustrationCheckResult | 角色一致性评分 |
|  POST  | /v1/feedbacks/story                     | StoryFeedbackInput*      | 204         | 反馈驱动个性化 |

> *`StoryFeedbackInput` 可包含：`story_id`, `child_id`, `like_elements[]`, `dislike_elements[]`, `overall_mood`。

---

## 5) 数据库草案（只列核心表）
- `users(id, name, email, phone, language, timezone, created_at)`
- `children(id, user_id, nickname, age, gender, language, reading_level, interests_json, avoid_topics_json, avoid_elements_json)`
- `stories(id, user_id, child_id, title, language, meta_json, interaction_summary_json, created_at)`
- `story_pages(id, story_id, page_number, text, word_count, illustration_json, interaction_json)`
- `characters(id, name, bible_json, lora_model_ref, style_adapter)`
- `feedbacks(id, story_id, child_id, like_elements_json, dislike_elements_json, rating, created_at)`

---

## 6) 校验要点与网关策略
- **请求过滤**：强制校验 `age`、`language`、敏感词黑名单；`avoid_*` 上限控制。
- **安全**：JWT + 家长角色；所有 `children` 资源必须隶属于 `user_id` 的租户边界。
- **审计**：落库请求与策略决策（例如过滤掉的元素）以满足合规追溯。

---

## 7) Mock / 合同测试建议
- 使用 `Prism` / `OpenAPI` 生成 Mock Server；
- 引入 `contract tests`（Pact）保证前后端独立迭代时接口不破坏；
- 以本附录为单一事实来源（SSOT）生成 TS 类型与后端校验器（zod / ajv）。

---

**附录完**

