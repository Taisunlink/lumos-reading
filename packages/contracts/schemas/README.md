# V2 Schemas

这些 schema 是 LumosReading V2 的正式共享契约。

## 当前权威 schema

- `caregiver-household.v1.schema.json`
- `caregiver-children.v1.schema.json`
- `caregiver-plan.v1.schema.json`
- `caregiver-progress.v1.schema.json`
- `caregiver-dashboard.v1.schema.json`
- `story-package.v1.schema.json`
- `reading-event.v1.schema.json`
- `safety-audit.v1.schema.json`

## 适用范围

- `CaregiverHousehold v1`
  Read model for the household operating surface, featured package selection, queue visibility, and top-level caregiver metrics.
- `CaregiverChildren v1`
  Read model for caregiver child assignments with embedded current package context.
- `CaregiverPlan v1`
  Read model for caregiver weekly plan entries with embedded package payloads.
- `CaregiverProgress v1`
  Read model for caregiver progress review with typed events plus child and package labels.
- `CaregiverDashboard v1`
  用于 caregiver surface 的家庭聚合读模型，承载包队列、儿童摘要、计划、事件与进展指标。
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
