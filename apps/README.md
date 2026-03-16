# Apps

本目录同时包含两类内容：

- 当前遗留的 PoC 应用
- V2 目标架构的目录骨架

## 当前遗留应用

- `web/`
  现有前端 PoC。当前更接近 demo 阅读端，不再视为 V2 儿童主应用基线。
- `api/`
  现有 FastAPI PoC。保留为迁移参考，不直接视为 V2 最终服务边界。
- `ai-service/`
  现有 AI 编排与质量规则 PoC。保留其方法论和部分规则逻辑，逐步迁入 V2 内容供应链。

## V2 目标目录骨架

- `child-app/`
  未来的 iPad-first 儿童端 App。
- `caregiver-web/`
  未来的家长端 Web。
- `studio-web/`
  未来的内容编辑、审核、运营端 Web。
- `workers/`
  未来的异步任务与打包、审核、TTS、生成 worker。

## 开工顺序

以后每次开工先按下面顺序建立上下文：

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `packages/contracts/schemas/`
4. 本文件
5. `packages/contracts/README.md`

## 工作原则

- 先更新 schema，再写实现
- 新能力优先落到 V2 目标目录，不继续扩展 legacy 主链路
- legacy 目录中的代码只能作为迁移参考，不能默认当作最终设计依据
