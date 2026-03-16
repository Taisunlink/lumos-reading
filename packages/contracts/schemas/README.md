# V2 Schemas

这些 schema 是 LumosReading V2 的正式共享契约。

## 当前权威 schema

- `story-package.v1.schema.json`
- `reading-event.v1.schema.json`
- `safety-audit.v1.schema.json`

## 适用范围

- `StoryPackage v1`
  用于儿童端运行时内容包分发和缓存。
- `ReadingEvent v1`
  用于儿童端阅读事件采集、分析和后续推荐输入。
- `SafetyAudit v1`
  用于内容审核、复审、下架、追踪和治理审计。

## 设计原则

- schema 优先于前后端临时类型
- schema 优先于 agent 输出格式
- 破坏性变更必须升版本
- 运行时只消费审核通过、可版本化的内容对象

## 关联文档

- `docs/v2/01-strategy-review-and-references.md`
- `docs/v2/02-v2-architecture-and-migration-blueprint.md`
