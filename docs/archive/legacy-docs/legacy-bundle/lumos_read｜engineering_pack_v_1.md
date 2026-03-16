# LumosRead｜Engineering Pack v1.0

> 本包为工程启动所需“开箱即用”文档：**OpenAPI 3.1 规范**、**TypeScript 类型与 Zod 校验**、**服务目录结构**、**环境变量与配置**、**CI/CD 基线**、**日志与观测**、**安全与合规清单**、**API 错误码与限流**、**版本化策略与发布节奏**、**示例工单模板**。

---

## 1. OpenAPI 3.1 (YAML)

保存为 `openapi/lumosread-api.v1.yaml`

```yaml
openapi: 3.1.0
info:
  title: LumosRead Public API
  version: 1.0.0
  summary: Smart Reading Companion (MVP)
  description: >-
    Public REST endpoints for user profiles, story generation, illustration consistency checks, and feedback loop.
servers:
  - url: https://api.lumosread.app
    description: Production
  - url: https://staging.api.lumosread.app
    description: Staging
security:
  - bearerAuth: []
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  parameters:
    Cursor:
      name: cursor
      in: query
      required: false
      schema: { type: string }
    Limit:
      name: limit
      in: query
      required: false
      schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
  responses:
    Unauthorized:
      description: JWT missing/invalid
    NotFound:
      description: Resource not found
    ValidationError:
      description: Request body failed validation
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }
  schemas:
    UUID:
      type: string
      format: uuid
    ISODate:
      type: string
      format: date-time
    LanguageTag:
      type: string
      pattern: '^[a-z]{2}(-[A-Z]{2})?$'
    Error:
      type: object
      required: [code, message]
      properties:
        code: { type: string }
        message: { type: string }
        details: { type: object, additionalProperties: true }
    UserProfile:
      type: object
      required: [user_id, created_at, guardian, children]
      properties:
        user_id: { $ref: '#/components/schemas/UUID' }
        created_at: { $ref: '#/components/schemas/ISODate' }
        updated_at: { $ref: '#/components/schemas/ISODate' }
        guardian:
          type: object
          required: [name, email, language]
          properties:
            name: { type: string, minLength: 1, maxLength: 80 }
            email: { type: string, format: email }
            phone: { type: string, minLength: 6, maxLength: 32 }
            language: { $ref: '#/components/schemas/LanguageTag' }
            timezone: { type: string, default: Asia/Taipei }
        children:
          type: array
          minItems: 1
          items:
            type: object
            required: [child_id, nickname, age, language]
            properties:
              child_id: { $ref: '#/components/schemas/UUID' }
              nickname: { type: string, minLength: 1, maxLength: 40 }
              age: { type: integer, minimum: 2, maximum: 11 }
              gender: { type: string, enum: [male, female, unspecified] }
              language: { $ref: '#/components/schemas/LanguageTag' }
              reading_level: { type: string, enum: [pre-operational, concrete-operational] }
              interests: { type: array, maxItems: 10, items: { type: string } }
              avoid_topics: { type: array, maxItems: 15, items: { type: string } }
              avoid_elements: { type: array, maxItems: 15, items: { type: string } }
              cognitive_notes: { type: string, maxLength: 500 }
        privacy:
          type: object
          properties:
            data_minimization: { type: boolean, default: true }
            share_usage_for_improvement: { type: boolean, default: false }
    StoryGenInput:
      type: object
      required: [child_profile, story_preferences, safety_filters, interaction_density]
      properties:
        child_profile:
          type: object
          required: [name, age, language, cognitive_level]
          properties:
            name: { type: string, minLength: 1, maxLength: 40 }
            age: { type: integer, minimum: 2, maximum: 11 }
            gender: { type: string, enum: [male, female, unspecified] }
            language: { $ref: '#/components/schemas/LanguageTag' }
            cognitive_level: { type: string, enum: [pre-operational, concrete-operational] }
        story_preferences:
          type: object
          required: [theme, setting, protagonist]
          properties:
            theme: { type: string, enum: [friendship, courage, sharing, kindness, perseverance] }
            setting: { type: string, enum: [forest, ocean, space, castle, city] }
            protagonist:
              type: object
              required: [type]
              properties:
                type: { type: string, enum: [animal, child, robot, elf] }
                species: { type: string }
                traits: { type: array, maxItems: 5, items: { type: string } }
            companion: { type: string }
            reading_time_minutes: { type: integer, minimum: 3, maximum: 15 }
        safety_filters:
          type: object
          properties:
            avoid_topics: { type: array, items: { type: string } }
            avoid_elements: { type: array, items: { type: string } }
        interaction_density: { type: string, enum: [low, medium, high], default: medium }
        seed: { type: integer, minimum: 0 }
    StoryPage:
      type: object
      required: [page_number, text]
      properties:
        page_number: { type: integer, minimum: 1 }
        text: { type: string }
        word_count: { type: integer, minimum: 1 }
        illustration:
          type: object
          properties:
            prompt: { type: string }
            key_elements: { type: array, items: { type: string } }
            color_palette: { type: array, items: { type: string } }
            character_consistency_id: { type: string }
            seed: { type: integer }
        interaction:
          type: object
          properties:
            type: { type: string, enum: [Completion, Recall, Open-ended, Wh-question, Distancing] }
            prompt: { type: string }
            timing: { type: string, enum: [during_reading, after_reading] }
            blank: { type: string }
            suggested_response: { type: string }
    StoryGenOutput:
      type: object
      required: [story_id, title, age_appropriateness, reading_time, pages, interaction_summary]
      properties:
        story_id: { $ref: '#/components/schemas/UUID' }
        title: { type: string, minLength: 1, maxLength: 80 }
        age_appropriateness: { type: string }
        reading_time: { type: string }
        language: { $ref: '#/components/schemas/LanguageTag' }
        pages: { type: array, minItems: 3, items: { $ref: '#/components/schemas/StoryPage' } }
        interaction_summary:
          type: object
          required: [total_prompts, prompt_types]
          properties:
            total_prompts: { type: integer, minimum: 0 }
            prompt_types: { type: object, additionalProperties: { type: integer, minimum: 0 } }
    CharacterBible:
      type: object
      required: [character_id, name, core_features, color_palette, proportions]
      properties:
        character_id: { type: string }
        name: { type: string }
        core_features: { type: array, minItems: 3, items: { type: string } }
        color_palette: { type: array, minItems: 3, items: { type: string } }
        proportions:
          type: object
          properties:
            head_body_ratio: { type: number, minimum: 0.1, maximum: 3.0 }
            eye_size_ratio: { type: number, minimum: 0.05, maximum: 0.6 }
        lora_model_ref: { type: string }
        style_adapter: { type: string }
    IllustrationAsset:
      type: object
      required: [image_id, url]
      properties:
        image_id: { type: string }
        url: { type: string, format: uri }
        features_detected: { type: array, items: { type: string } }
        dominant_colors: { type: array, items: { type: string } }
    IllustrationCheckInput:
      type: object
      required: [character_bible, image_assets]
      properties:
        character_bible: { $ref: '#/components/schemas/CharacterBible' }
        image_assets: { type: array, minItems: 1, items: { $ref: '#/components/schemas/IllustrationAsset' } }
    IllustrationCheckResult:
      type: object
      required: [character_id, overall_score, feature_scores, color_similarity, proportion_check, recommendations]
      properties:
        character_id: { type: string }
        overall_score: { type: number, minimum: 0, maximum: 1 }
        feature_scores: { type: object, additionalProperties: { type: number, minimum: 0, maximum: 1 } }
        color_similarity: { type: number, minimum: 0, maximum: 1 }
        proportion_check:
          type: object
          properties:
            head_body_ratio_deviation: { type: number }
            eye_size_ratio_deviation: { type: number }
        recommendations: { type: array, items: { type: string } }
        non_compliant_images: { type: array, items: { type: string } }
paths:
  /v1/users:
    post:
      summary: Create user profile (guardian+children)
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/UserProfile' }
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema: { $ref: '#/components/schemas/UserProfile' }
        '400': { $ref: '#/components/responses/ValidationError' }
  /v1/users/{user_id}:
    get:
      summary: Get user profile
      parameters:
        - name: user_id
          in: path
          required: true
          schema: { $ref: '#/components/schemas/UUID' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/UserProfile' }
        '401': { $ref: '#/components/responses/Unauthorized' }
        '404': { $ref: '#/components/responses/NotFound' }
  /v1/stories/generate:
    post:
      summary: Generate a story
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/StoryGenInput' }
      responses:
        '202':
          description: Accepted (async)
          content:
            application/json:
              schema:
                type: object
                properties:
                  job_id: { type: string }
        '200':
          description: Synchronous generation
          content:
            application/json:
              schema: { $ref: '#/components/schemas/StoryGenOutput' }
        '400': { $ref: '#/components/responses/ValidationError' }
  /v1/stories/{story_id}:
    get:
      summary: Get story by id
      parameters:
        - name: story_id
          in: path
          required: true
          schema: { $ref: '#/components/schemas/UUID' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/StoryGenOutput' }
        '404': { $ref: '#/components/responses/NotFound' }
  /v1/illustrations/consistency-check:
    post:
      summary: Check character consistency across images
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/IllustrationCheckInput' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema: { $ref: '#/components/schemas/IllustrationCheckResult' }
        '400': { $ref: '#/components/responses/ValidationError' }
  /v1/feedbacks/story:
    post:
      summary: Submit story feedback
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [story_id, child_id]
              properties:
                story_id: { $ref: '#/components/schemas/UUID' }
                child_id: { $ref: '#/components/schemas/UUID' }
                like_elements: { type: array, items: { type: string } }
                dislike_elements: { type: array, items: { type: string } }
                overall_mood: { type: string, enum: [delighted, engaged, neutral, bored] }
      responses:
        '204': { description: No Content }
        '400': { $ref: '#/components/responses/ValidationError' }
```
```

---

## 2. TypeScript 类型与 Zod 校验

保存为 `packages/types/src/index.ts`

```ts
// 基础类型
export type UUID = string;
export type ISODate = string;
export type LanguageTag = string; // e.g. 'zh-CN'

export interface Guardian {
  name: string;
  email: string;
  phone?: string;
  language: LanguageTag;
  timezone?: string; // default Asia/Taipei
}

export interface Child {
  child_id: UUID;
  nickname: string;
  age: number; // 2..11
  gender?: 'male' | 'female' | 'unspecified';
  language: LanguageTag;
  reading_level?: 'pre-operational' | 'concrete-operational';
  interests?: string[];
  avoid_topics?: string[];
  avoid_elements?: string[];
  cognitive_notes?: string;
}

export interface UserProfile {
  user_id: UUID;
  created_at: ISODate;
  updated_at?: ISODate;
  guardian: Guardian;
  children: Child[];
  privacy?: {
    data_minimization?: boolean;
    share_usage_for_improvement?: boolean;
  };
}

export type InteractionType =
  | 'Completion'
  | 'Recall'
  | 'Open-ended'
  | 'Wh-question'
  | 'Distancing';

export interface StoryGenInput {
  child_profile: {
    name: string;
    age: number;
    gender?: 'male' | 'female' | 'unspecified';
    language: LanguageTag;
    cognitive_level: 'pre-operational' | 'concrete-operational';
  };
  story_preferences: {
    theme: 'friendship' | 'courage' | 'sharing' | 'kindness' | 'perseverance';
    setting: 'forest' | 'ocean' | 'space' | 'castle' | 'city';
    protagonist: {
      type: 'animal' | 'child' | 'robot' | 'elf';
      species?: string;
      traits?: string[];
    };
    companion?: string;
    reading_time_minutes?: number;
  };
  safety_filters?: {
    avoid_topics?: string[];
    avoid_elements?: string[];
  };
  interaction_density?: 'low' | 'medium' | 'high';
  seed?: number;
}

export interface StoryPage {
  page_number: number;
  text: string;
  word_count?: number;
  illustration?: {
    prompt?: string;
    key_elements?: string[];
    color_palette?: string[];
    character_consistency_id?: string;
    seed?: number;
  };
  interaction?: {
    type?: InteractionType;
    prompt?: string;
    timing?: 'during_reading' | 'after_reading';
    blank?: string;
    suggested_response?: string;
  };
}

export interface StoryGenOutput {
  story_id: UUID;
  title: string;
  age_appropriateness: string; // e.g. 4-6岁
  reading_time: string; // e.g. 5-7分钟
  language?: LanguageTag;
  pages: StoryPage[];
  interaction_summary: {
    total_prompts: number;
    prompt_types: Record<string, number>;
  };
}

export interface CharacterBible {
  character_id: string;
  name: string;
  core_features: string[];
  color_palette: string[];
  proportions?: { head_body_ratio?: number; eye_size_ratio?: number };
  lora_model_ref?: string;
  style_adapter?: string;
}

export interface IllustrationAsset {
  image_id: string;
  url: string;
  features_detected?: string[];
  dominant_colors?: string[];
}

export interface IllustrationCheckInput {
  character_bible: CharacterBible;
  image_assets: IllustrationAsset[];
}

export interface IllustrationCheckResult {
  character_id: string;
  overall_score: number; // 0..1
  feature_scores: Record<string, number>;
  color_similarity: number; // 0..1
  proportion_check?: { head_body_ratio_deviation?: number; eye_size_ratio_deviation?: number };
  recommendations: string[];
  non_compliant_images?: string[];
}

export interface StoryFeedbackInput {
  story_id: UUID;
  child_id: UUID;
  like_elements?: string[];
  dislike_elements?: string[];
  overall_mood?: 'delighted' | 'engaged' | 'neutral' | 'bored';
}
```
```

如需运行时校验，推荐 `zod` 与 `@anatine/zod-openapi` 生成双向：

```ts
import { z } from 'zod';

export const LanguageTag = z.string().regex(/^[a-z]{2}(-[A-Z]{2})?$/);
export const GuardianZ = z.object({
  name: z.string().min(1).max(80),
  email: z.string().email(),
  phone: z.string().min(6).max(32).optional(),
  language: LanguageTag,
  timezone: z.string().default('Asia/Taipei').optional()
});
// ...同理为各 Schema 定义 Zod 版本，并在网关用 zod.parse 校验
```

---

## 3. 服务目录结构（Monorepo 建议）

```
repo/
├─ openapi/
│  └─ lumosread-api.v1.yaml
├─ packages/
│  ├─ types/               # TS 类型 & Zod 校验
│  └─ sdk/                 # 由 OpenAPI 生成的前后端共享 SDK
├─ services/
│  ├─ gateway/             # API 网关（Express/Fastify）
│  ├─ story-gen/           # 故事生成微服务（LLM 调度）
│  ├─ art-gen/             # 插画生成（ComfyUI/LoRA 调用）
│  ├─ consistency/         # 一致性评分服务（CV）
│  └─ feedback/            # 反馈回传与画像更新
├─ infra/
│  ├─ terraform/           # IaC（VPC, DB, S3, CDN, MQ）
│  ├─ k8s/                 # Helm charts / manifests
│  └─ github-actions/      # CI/CD workflows
└─ apps/
   ├─ web-pwa/             # React + PWA 客户端
   └─ admin/               # 家长/运营后台
```

---

## 4. 环境变量与配置（`.env.example`）

```
NODE_ENV=development
PORT=8080
JWT_ISSUER=lumosread
JWT_AUDIENCE=public
JWT_PUBLIC_KEY=---base64---
JWT_PRIVATE_KEY=---base64---
DB_URL=postgres://user:pass@host:5432/lumos
REDIS_URL=redis://host:6379
OBJECT_STORE_BUCKET=lumos-artifacts
OPENAI_API_KEY=sk-***
COMFYUI_BASE_URL=http://localhost:8188
RATE_LIMIT_RPM=120
CORS_ALLOWED_ORIGINS=https://app.lumosread.app,https://staging.lumosread.app
LOG_LEVEL=info
```

配置策略：12-factor、分环境覆盖（dev/staging/prod），严禁将密钥提交至仓库。

---

## 5. CI/CD 基线与质量门禁
- **检测**：`eslint` + `prettier` + `tsc --noEmit` + `zod` 运行时校验（轻 e2e）
- **安全**：`npm audit`/`snyk test`，Trivy 扫描镜像
- **测试**：单测 (Jest) 覆盖率 >= 80%；契约测试（Pact）
- **构建**：OpenAPI 生成 SDK（`openapi-typescript` / `orval`）
- **发布**：语义化版本（semver），tag 触发构建；staging 自动部署，prod 需人工批准

---

## 6. 日志与观测（Observability）
- **结构化日志**：pino / winston；含 `trace_id`、`user_id`、`child_id`
- **APM**：OpenTelemetry（HTTP/DB/MQ trace），Grafana Tempo + Loki + Prometheus
- **仪表盘**：故事生成时延、插画一致性平均分、错误率、限流命中率

---

## 7. 安全与合规清单（MVP）
- JWT + RBAC（家长/管理员）
- **多租户边界**：`user_id` 作为租户域过滤
- **输入校验**：AJV/Zod + 黑名单（敏感主题）
- **数据最小化**：不采集不必要 PII；日志脱敏
- **儿童合规**：未成年人模式、时长阈值、内容过滤、家长可控
- **隐私**：PIPL 对齐；提供数据导出与删除 API（后续版本）

---

## 8. API 错误码与限流

| code                | http | 说明 |
|---------------------|------|-----|
| `validation_error`  | 400  | 请求体验证失败 |
| `unauthorized`      | 401  | 缺少/无效 JWT |
| `forbidden`         | 403  | 权限不足 |
| `not_found`         | 404  | 资源不存在 |
| `rate_limited`      | 429  | 触发限流 |
| `conflict`          | 409  | 资源冲突/幂等冲突 |
| `server_error`      | 500  | 未处理异常 |

**限流**：默认 120 req/min 每 `user_id` + IP；生成类接口可单独配置（如 30 req/min）。

---

## 9. 版本化与发布节奏
- **API 版本**：URL 前缀（`/v1`）；破坏性变更以 `/v2` 新增并平滑迁移
- **发布节奏**：MVP 周发布；稳定后双周发布；紧急修复走 hotfix 分支

---

## 10. 示例工单模板（GitHub Issues）

```
[Feature] StoryGen 同步/异步双模网关
背景：高峰期避免长轮询阻塞；
验收标准：
- POST /v1/stories/generate 支持 `Prefer: respond-async`
- 同步时 95% 请求 < 3s；异步返回 job_id 并可查询状态
测试：
- 合同测试 Pact 覆盖成功/排队/失败三状态
风险：
- 队列拥塞；建议 MQ + 超时重试
```

---

## 11. 快速开始（本地开发）

```
# 1) 安装依赖
pnpm i

# 2) 生成 SDK
pnpm dlx openapi-typescript openapi/lumosread-api.v1.yaml -o packages/sdk/src/gen.ts

# 3) 启动服务
pnpm -r --filter services/gateway dev
pnpm -r --filter apps/web-pwa dev
```

---

**Engineering Pack v1.0 完成**

