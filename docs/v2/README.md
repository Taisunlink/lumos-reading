# V2 Active Docs

本目录是 LumosReading 当前唯一活跃文档区。

## 当前文档

- `01-strategy-review-and-references.md`
  V2 的战略判断、市场研究、当前代码成熟度判断与参考资料。
- `02-v2-architecture-and-migration-blueprint.md`
  V2 的目标架构、领域模型、契约草案、迁移蓝图与 6 个月路线图。

## 与 schema 的关系

- 文档定义业务语义和架构边界
- `packages/contracts/schemas/` 定义正式共享字段契约
- 二者冲突时，先修文档，再修 schema，再修实现
