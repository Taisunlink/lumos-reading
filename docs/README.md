# 文档治理

本仓库从现在开始采用“权威文档 + 契约优先 + 档案隔离”的文档治理机制。

## 权威文档

以下内容是当前唯一权威入口：

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `packages/contracts/schemas/`
4. `apps/README.md`
5. `packages/contracts/README.md`

## 规则

- 战略、市场、用户定义变化：更新 `docs/v2/01-*`
- 架构、领域模型、接口、事件和迁移变化：更新 `docs/v2/02-*`
- 字段与运行时对象变化：更新 `packages/contracts/schemas/*`
- 旧文档不再作为实现依据，统一归档到 `docs/archive/`

## 档案策略

- `docs/archive/legacy-docs/`
  归档旧的产品、方法学、实施与概念文档。
- `docs/archive/root-docs/`
  归档原本位于仓库根目录的阶段性报告、PoC 指南与临时说明。

## 开工顺序

以后每次开工都按下面顺序读取：

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `packages/contracts/schemas/README.md`
4. `apps/README.md`
5. `packages/contracts/README.md`

不按这个顺序建立上下文，后续讨论很容易又退回到 PoC 语境。
