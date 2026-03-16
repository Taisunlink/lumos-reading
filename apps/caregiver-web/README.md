# caregiver-web

这是 LumosReading V2 的家长端 Web 最小壳。

## 当前目标

- 作为未来家长侧入口，而不是儿童阅读端
- 直接消费 `@lumosreading/contracts`
- 围绕阅读计划、进展、家庭管理和订阅展开

## 当前实现

- Next.js App Router 多路由最小壳
- 路由包括 `Home`、`Children`、`Plans`、`Progress`、`Settings`
- 直接消费 `@lumosreading/contracts` 中的 schema 常量与 TypeScript 类型
- 通过 `@lumosreading/sdk` 访问 `/api/v2`
- 内置一个面向 `/api/v2` 的最小 API workbench，用于手动验证 story package 与 reading session

## 当前工作边界

- `apps/web` 仅作为 legacy demo 参考，不再承接新家长端功能
- 新能力优先围绕 `packages/contracts` 和 `/api/v2` 演进
- 儿童主阅读体验未来落到 iPad-first 的 `child-app`

## 开发前先读

1. `docs/v2/01-strategy-review-and-references.md`
2. `docs/v2/02-v2-architecture-and-migration-blueprint.md`
3. `packages/contracts/schemas/README.md`
4. `apps/README.md`
5. `packages/contracts/README.md`
