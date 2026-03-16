# LumosReading

LumosReading 当前正从 PoC 重构到 V2。

当前仓库的核心工作方式不再是“围绕旧实现补功能”，而是“围绕权威文档、共享契约和目标 monorepo 骨架推进重构”。

## Start Here

以后每次开工，统一按下面顺序建立上下文：

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `packages/contracts/schemas/README.md`
4. `apps/README.md`
5. `packages/contracts/README.md`

## 当前权威资产

- `docs/v2/`
  当前唯一活跃的战略与架构文档区。
- `packages/contracts/`
  当前唯一权威共享契约包。
- `apps/`
  同时包含 legacy PoC 资产和 V2 目标目录骨架。

## 当前状态

- `apps/web`、`apps/api`、`apps/ai-service` 仍然是 legacy PoC 资产
- `packages/contracts/schemas/` 已建立 V2 第一批正式 schema
- `docs/archive/` 已作为历史概念与 PoC 文档归档区

## V2 目标方向

- 儿童端：iPad-first App
- 家长端：Web
- 内容运营端：Web
- 运行时：Story Package 分发，不以完整实时生成作为主链路
- 开发方式：契约优先、归档隔离、增量迁移

## 文档治理

请先阅读 `docs/README.md`。

简化规则如下：

- 战略变化更新 `docs/v2/01-*`
- 架构与迁移变化更新 `docs/v2/02-*`
- 字段变化更新 `packages/contracts/schemas/*`
- `docs/archive/` 只做参考，不做当前实现依据
