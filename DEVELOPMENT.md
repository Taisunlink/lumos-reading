# LumosReading 开发指南

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.9+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### 开发环境设置

1. **克隆仓库**
```bash
git clone https://github.com/Taisunlink/lumos-reading.git
cd lumos-reading
```

2. **安装依赖**
```bash
npm install
```

3. **环境配置**
```bash
cp env.example .env.local
# 编辑 .env.local 文件，填入必要的API密钥
```

4. **启动开发环境**
```bash
# 启动数据库和Redis
npm run docker:up

# 运行数据库迁移
npm run db:migrate

# 启动开发服务器
npm run dev
```

## 📁 项目结构

```
lumos-reading/
├── apps/
│   ├── web/                    # Next.js 前端应用
│   │   ├── src/
│   │   │   ├── app/            # App Router
│   │   │   ├── components/     # React组件
│   │   │   ├── hooks/          # 自定义Hooks
│   │   │   ├── lib/            # 工具函数
│   │   │   ├── stores/         # Zustand状态管理
│   │   │   └── types/          # TypeScript类型
│   │   ├── public/             # 静态资源
│   │   └── package.json
│   │
│   ├── api/                    # FastAPI 后端服务
│   │   ├── app/
│   │   │   ├── core/           # 核心配置
│   │   │   ├── models/         # 数据模型
│   │   │   ├── schemas/        # Pydantic模式
│   │   │   ├── services/       # 业务逻辑
│   │   │   ├── routers/        # API路由
│   │   │   └── utils/          # 工具函数
│   │   ├── migrations/         # 数据库迁移
│   │   └── requirements.txt
│   │
│   └── ai-service/             # AI服务模块
│       ├── generators/         # 内容生成器
│       ├── prompts/            # Prompt模板
│       └── validators/         # 质量验证
│
├── packages/
│   ├── ui/                     # 共享UI组件
│   ├── tsconfig/              # TypeScript配置
│   └── eslint-config/         # ESLint配置
│
├── infrastructure/             # 基础设施配置
│   ├── docker/                # Docker配置
│   ├── k8s/                   # Kubernetes配置
│   └── terraform/             # IaC配置
│
├── docs/                      # 文档
├── tests/                     # 测试
└── scripts/                   # 脚本
```

## 🛠️ 开发工作流

### 分支策略
- `master`: 主分支，用于生产环境
- `develop`: 开发分支，用于集成功能
- `feature/*`: 功能分支
- `hotfix/*`: 热修复分支

### 提交规范
使用 Conventional Commits 规范：

```bash
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

### 代码规范
- 使用 TypeScript 严格模式
- 遵循 ESLint 和 Prettier 配置
- 组件优先使用函数式组件
- API 遵循 RESTful 设计

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
npm run test

# 运行单元测试
npm run test:unit

# 运行集成测试
npm run test:integration

# 运行E2E测试
npm run test:e2e
```

### 测试覆盖率
- 单元测试覆盖率 > 80%
- 关键路径覆盖率 100%

## 🚀 部署

### 开发环境
```bash
npm run docker:up
```

### 生产环境
```bash
# 构建镜像
npm run docker:build

# 部署到Kubernetes
kubectl apply -f infrastructure/k8s/
```

## 📊 监控

### 开发环境监控
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

### 关键指标
- API响应时间
- 错误率
- 数据库连接数
- 内存使用率

## 🐛 调试

### 前端调试
- 使用 React Developer Tools
- 浏览器开发者工具
- Next.js 内置调试功能

### 后端调试
- 使用 FastAPI 自动生成的文档
- 日志系统
- 数据库查询分析

### AI服务调试
- 模型响应日志
- 提示词优化
- 成本监控

## 📚 文档

- [产品需求文档](docs/LumosReading_PRD_Dev_v2.0.md)
- [技术架构设计](docs/LumosReading%20技术实施指南_v2.1.md)
- [工程实施文档](docs/LumosReading%20工程实施文档_v2.0.md)
- [开发指导文档](docs/LumosReading%20项目开发指导文档_v2.0.md)

## 🤝 贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📞 支持

- 问题反馈：https://github.com/Taisunlink/lumos-reading/issues
- 讨论区：https://github.com/Taisunlink/lumos-reading/discussions
- 邮箱：dev@lumosreading.com
