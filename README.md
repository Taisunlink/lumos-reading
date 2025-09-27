# LumosReading - 智能阅读伙伴

> 基于教育心理学理论的AI驱动儿童绘本平台，为3-11岁儿童（含神经多样性儿童）提供个性化、科学化的阅读体验。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

## 🌟 项目特色

### 核心价值主张
- **不是内容生成器，而是教育学赋能系统**
- **将科学验证的对话式阅读法无缝嵌入个性化绘本**
- **为家长提供"教育学上的安心感"**

### 技术亮点
- 🤖 **AI专家团队协同**：心理学专家 + 故事创作专家 + 质量控制专家
- 🧠 **神经多样性支持**：ADHD和自闭谱系专门适配
- 📚 **CROWD-PEER框架**：对话式阅读法智能实现
- 🎨 **角色一致性保障**：Series Bible + LoRA技术
- ⚡ **降级策略**：确保100%可用性

## 🏗️ 技术架构

### 前端技术栈
- **Next.js 14** + App Router
- **PWA支持** + 多端适配
- **Zustand** 状态管理
- **Tailwind CSS** + Radix UI

### 后端技术栈
- **FastAPI** 微服务架构
- **PostgreSQL** 主数据库
- **Redis** 缓存层
- **RabbitMQ** 消息队列

### AI服务
- **Claude**：教育框架设计
- **通义千问**：中文内容生成
- **DALL-E 3**：图像生成
- **Azure TTS**：语音合成

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.9+
- PostgreSQL 15+
- Redis 7+

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/ethanzh/lumos-reading.git
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

5. **访问应用**
- 前端：http://localhost:3000
- API文档：http://localhost:8000/docs

## 📁 项目结构

```
lumos-reading/
├── apps/
│   ├── web/                    # Next.js 前端应用
│   ├── api/                    # FastAPI 后端服务
│   └── ai-service/             # AI服务模块
├── packages/
│   ├── ui/                     # 共享UI组件
│   ├── tsconfig/              # TypeScript配置
│   └── eslint-config/         # ESLint配置
├── infrastructure/             # 基础设施配置
│   ├── docker/                # Docker配置
│   ├── k8s/                   # Kubernetes配置
│   └── terraform/             # IaC配置
├── docs/                      # 项目文档
├── tests/                     # 测试文件
└── scripts/                   # 脚本文件
```

## 🎯 核心功能

### MVP功能（0-3月）
- [x] 项目架构搭建
- [ ] 用户认证系统
- [ ] 儿童档案管理
- [ ] AI故事生成（3-Agent协同）
- [ ] 渐进式生成API
- [ ] 降级机制实现
- [ ] CROWD互动系统
- [ ] 神经多样性适配
- [ ] 音频TTS支持
- [ ] 基础监控系统

### 增长期功能（3-6月）
- [ ] 角色一致性系统
- [ ] 多设备同步
- [ ] 智能推荐引擎
- [ ] 成长追踪系统
- [ ] 家长控制中心
- [ ] 社交分享功能

### 成熟期功能（6-12月）
- [ ] 成人定制接口
- [ ] AR/VR阅读体验
- [ ] 语音交互
- [ ] UGC内容市场
- [ ] 教育效果评测

## 🧠 神经多样性支持

### ADHD适配
- 短段落阅读（3-5分钟）
- 视觉锚点辅助注意力
- 高频互动保持专注
- 清晰进度指示器

### 自闭谱系适配
- 稳定的视觉风格
- 精细的音量控制
- 场景切换预告
- 固定的阅读仪式

## 💰 商业模式

### 订阅层级
- **免费版**：每月1本预生产内容
- **标准版**（¥29/月）：每周2本，半定制功能
- **高级版**（¥68/月）：无限内容，神经多样性支持
- **家庭版**（¥98/月）：支持3个儿童档案

## 📊 关键指标

### 技术指标
- API响应时间 P95 < 500ms
- 故事生成成功率 > 95%
- 降级触发率 < 5%
- 系统可用性 > 99.5%

### 业务指标
- 首次体验完成率 > 80%
- 故事完读率 > 70%
- CROWD互动参与率 > 60%
- 家长满意度 > 4.0/5

## 🛠️ 开发指南

### 代码规范
- 使用 TypeScript 严格模式
- 遵循 ESLint 和 Prettier 配置
- 组件优先使用函数式组件
- API 遵循 RESTful 设计

### 测试策略
- 单元测试覆盖率 > 80%
- 集成测试覆盖关键流程
- E2E测试覆盖用户旅程
- 性能测试确保响应时间

### 部署流程
- 使用 Docker 容器化
- Kubernetes 编排
- CI/CD 自动化部署
- 蓝绿部署策略

## 📚 文档

- [产品需求文档](docs/LumosReading_PRD_Dev_v2.0.md)
- [技术架构设计](docs/LumosReading%20技术实施指南_v2.1.md)
- [工程实施文档](docs/LumosReading%20工程实施文档_v2.0.md)
- [开发指导文档](docs/LumosReading%20项目开发指导文档_v2.0.md)

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 项目主页：https://github.com/ethanzh/lumos-reading
- 问题反馈：https://github.com/ethanzh/lumos-reading/issues
- 邮箱：contact@lumosreading.com

---

**让每个孩子都拥有专属的智能阅读伙伴** ✨
