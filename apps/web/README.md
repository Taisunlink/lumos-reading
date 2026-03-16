# legacy-web-demo

`apps/web` 已被明确降级为 legacy demo。

## 角色

- 保留原型阅读端与旧实现参考
- 作为迁移时的代码素材来源
- 不再作为 V2 正式开发入口

## 当前开发规则

- 新功能不要继续落到这里
- 家长端能力落到 `apps/caregiver-web`
- 儿童端能力未来落到 `apps/child-app`
- 共享字段契约统一读取 `packages/contracts`

## 开工顺序

请先阅读：

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `packages/contracts/schemas/README.md`
4. `apps/README.md`
