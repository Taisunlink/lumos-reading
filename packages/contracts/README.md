# `@lumosreading/contracts`

这是 LumosReading V2 的共享契约包。

## 目的

该包承载跨端、跨服务共享的正式契约，优先级高于任何临时 prompt、mock 或页面数据结构。

当前纳入治理的第一批契约：

- `CaregiverDashboard v1`
- `CaregiverHousehold v1`
- `CaregiverChildren v1`
- `CaregiverPlan v1`
- `CaregiverProgress v1`
- `StoryPackage v1`
- `ReadingEvent v1`
- `SafetyAudit v1`

当前包同时导出：

- 原始 JSON Schema
- 对应的 TypeScript 类型与常量

## 读取顺序

在开始任何 V2 开发之前，先按下面顺序阅读：

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `packages/contracts/schemas/README.md`
4. `apps/README.md`
5. 本文件

## 变更规则

- 业务语义变化：先更新 `docs/v2/01-*`
- 架构、领域模型、接口或事件变化：先更新 `docs/v2/02-*`
- 契约字段变化：必须同步更新对应 schema
- 运行时对象禁止绕开 schema 直接新增字段
- 旧版本契约不得静默修改；有破坏性变更时，新增版本号

## 当前文件

- `schemas/caregiver-household.v1.schema.json`
- `schemas/caregiver-children.v1.schema.json`
- `schemas/caregiver-plan.v1.schema.json`
- `schemas/caregiver-progress.v1.schema.json`
- `schemas/caregiver-dashboard.v1.schema.json`
- `schemas/story-package.v1.schema.json`
- `schemas/reading-event.v1.schema.json`
- `schemas/safety-audit.v1.schema.json`
