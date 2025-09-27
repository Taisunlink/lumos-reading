# LumosReading 产品需求文档 v2.0

## 智能阅读伙伴 - 包容性儿童教育平台

------

## 执行摘要

LumosReading是一个基于教育心理学和AI技术的智能绘本平台，通过对话式阅读法（Dialogic Reading）和神经多样性友好设计，为3-11岁儿童提供个性化、科学化的阅读体验。本文档整合了产品愿景、技术架构、运营策略和工程实施方案，形成完整的开发指南。

------

## 第一部分：产品战略与科学基础

### 1.1 核心价值主张

**产品定位**：不是内容生成器，而是教育学赋能系统

**目标用户群体**：

- 主要用户：3-11岁儿童（含ADHD、自闭谱系等神经多样性儿童）
- 决策用户：家长（寻求科学陪伴与教育价值）
- 扩展用户：成人定制需求（家族故事、特殊场合）

### 1.2 理论基础强化

#### 认知发展理论应用

```python
class CognitiveDevelopmentFramework:
    """皮亚杰认知发展阶段的产品化应用"""
    
    STAGES = {
        'preoperational': {
            'age_range': '2-7岁',
            'characteristics': ['直觉思维', '自我中心', '符号功能'],
            'content_strategy': '具象叙事，简单因果，重复强化'
        },
        'concrete_operational': {
            'age_range': '7-11岁',
            'characteristics': ['逻辑思维', '守恒概念', '分类能力'],
            'content_strategy': '复合因果，多层次叙事，抽象概念引入'
        }
    }
```

#### 神经多样性支持框架

```python
class NeuroDiversitySupport:
    """神经多样性友好的核心设计"""
    
    ADHD_ADAPTATIONS = {
        'attention_support': {
            'shorter_segments': '3-5分钟段落',
            'visual_anchors': '视觉锚点辅助注意力',
            'interactive_breaks': '高频互动保持专注',
            'progress_indicators': '清晰进度条减少焦虑'
        },
        'executive_function_support': {
            'clear_structure': '明确的故事框架',
            'predictable_patterns': '可预测的叙事节奏',
            'choice_limitation': '有限选择避免决策疲劳'
        }
    }
    
    AUTISM_SPECTRUM_ADAPTATIONS = {
        'sensory_comfort': {
            'visual_consistency': '稳定的视觉风格',
            'audio_control': '精细的音量控制',
            'transition_warnings': '场景切换预告',
            'routine_support': '固定的阅读仪式'
        },
        'social_understanding': {
            'explicit_emotions': '明确的情绪标注',
            'social_scripts': '社交场景解释',
            'perspective_taking': '角色视角引导'
        }
    }
```

------

## 第二部分：产品功能架构

### 2.1 三层用户旅程（更新版）

#### Layer 1: 快速启动层

```yaml
目标: 3分钟完成设置，立即获得价值
流程:
  1. 微信/手机号注册: 30秒
  2. 儿童档案创建:
     - 基础信息: 昵称、年龄、性别
     - 神经多样性评估: 可选的简单问卷
     - 安全边界: 敏感主题规避
  3. 首个故事生成: 
     - 智能推荐主题
     - 一键生成
     - 立即可读
```

#### Layer 2: 个性化深化层

```yaml
目标: 建立独特的阅读体验
功能:
  - 角色定制系统:
    - Series Bible创建
    - LoRA模型训练
    - 一致性保障
  - 神经适配调节:
    - 感官控制面板
    - 交互密度调整
    - 视觉复杂度设置
  - 家长控制中心:
    - 内容过滤器
    - 时间管理
    - 学习目标设定
```

#### Layer 3: 生态构建层

```yaml
目标: 形成持续价值循环
特性:
  - 成长陪伴系统:
    - 阅读里程碑
    - 成长编年史
    - 家庭故事宇宙
  - 智能推荐引擎:
    - 基于行为的内容推荐
    - 预测性故事生成
    - 社交化分享
  - 成人定制接口:
    - 家族故事传承
    - 特殊场合定制
    - 治疗性故事
```

### 2.2 核心功能模块设计

#### 2.2.1 智能故事生成引擎 v2.0

```python
class StoryGenerationEngine:
    def generate_story(self, request: StoryRequest) -> Story:
        """
        多模态故事生成流程
        """
        # 1. 用户画像分析
        user_profile = self.analyze_user_profile(request.user_id)
        
        # 2. 神经多样性适配
        if user_profile.neuro_profile:
            request = self.adapt_for_neurodiversity(request, user_profile.neuro_profile)
        
        # 3. 内容生成策略选择
        strategy = self.select_generation_strategy(user_profile, request)
        
        if strategy == 'preproduced':
            # 预生产内容匹配
            return self.match_preproduced_content(request)
        elif strategy == 'template_based':
            # 模板个性化
            return self.personalize_template(request)
        else:
            # 实时生成
            return self.generate_realtime(request)
```

#### 2.2.2 CROWD-PEER交互系统

```python
class CROWDInteractionEngine:
    """对话式阅读的智能实现"""
    
    def generate_interaction(self, page_content, reading_context):
        interaction_type = self.select_interaction_type(reading_context)
        
        INTERACTION_STRATEGIES = {
            'Completion': self.generate_completion_prompt,
            'Recall': self.generate_recall_prompt,
            'Open_ended': self.generate_open_prompt,
            'Wh_questions': self.generate_wh_prompt,
            'Distancing': self.generate_distancing_prompt
        }
        
        # 神经多样性调整
        if reading_context.neuro_profile:
            interaction = self.adapt_interaction(
                interaction_type,
                reading_context.neuro_profile
            )
        
        return INTERACTION_STRATEGIES[interaction_type](page_content)
```

------

## 第三部分：技术架构设计

### 3.1 系统架构（轻资产模式）

```yaml
技术栈选择:
  前端:
    - 框架: Next.js 14 (App Router)
    - 状态管理: Zustand
    - UI库: Tailwind CSS + Radix UI
    - PWA: Workbox
    
  后端:
    - 框架: FastAPI
    - 数据库: PostgreSQL + Redis
    - 消息队列: RabbitMQ
    - 对象存储: 阿里云OSS
    
  AI服务:
    - 文本生成: OpenAI API (GPT-4)
    - 图像生成: DALL-E 3 (初期) + SD API (扩展)
    - 语音合成: Azure TTS
    
  基础设施:
    - 部署: Docker + K8s
    - CDN: Cloudflare
    - 监控: Grafana + Prometheus
```

### 3.2 数据模型设计

```sql
-- 核心数据表结构
CREATE TABLE users (
    id UUID PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    wechat_openid VARCHAR(100),
    created_at TIMESTAMP,
    subscription_tier ENUM('free', 'standard', 'premium', 'family')
);

CREATE TABLE children_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(100),
    birthday DATE,
    gender VARCHAR(10),
    neuro_profile JSONB,  -- 神经多样性配置
    preferences JSONB,
    created_at TIMESTAMP
);

CREATE TABLE stories (
    id UUID PRIMARY KEY,
    child_id UUID REFERENCES children_profiles(id),
    title VARCHAR(200),
    content JSONB,  -- 包含文本、图片、交互点
    generation_type ENUM('preproduced', 'template', 'realtime'),
    metadata JSONB,
    created_at TIMESTAMP
);

CREATE TABLE reading_sessions (
    id UUID PRIMARY KEY,
    story_id UUID REFERENCES stories(id),
    child_id UUID REFERENCES children_profiles(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    interaction_data JSONB,
    progress FLOAT
);

CREATE TABLE series_bible (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    characters JSONB,
    world_settings JSONB,
    narrative_rules JSONB,
    visual_assets JSONB,
    created_at TIMESTAMP
);
```

### 3.3 内容生产架构

```python
class HybridContentProduction:
    """混合内容生产策略"""
    
    def __init__(self):
        self.preproduced_library = PreproducedContent()  # 500-1000本
        self.template_engine = TemplateEngine()          # 100+模板
        self.realtime_generator = RealtimeGenerator()    # API驱动
        
    async def produce_content(self, request):
        # 智能路由决策
        if self.preproduced_library.has_match(request, threshold=0.8):
            return await self.preproduced_library.get(request)
            
        elif request.user_tier == 'premium':
            return await self.realtime_generator.generate(request)
            
        else:
            # 异步生成，8-10分钟
            task_id = await self.template_engine.queue(request)
            return {'status': 'generating', 'task_id': task_id}
```

------

## 第四部分：运营策略

### 4.1 订阅模式设计

```yaml
订阅层级:
  免费版:
    - 每月1本预生产内容
    - 基础CROWD提示
    - 单设备
    
  标准版 (¥29/月):
    - 每周2本内容
    - 半定制功能
    - 2设备同步
    - 基础数据报告
    
  高级版 (¥68/月):
    - 无限内容
    - 实时深度定制
    - 神经多样性完整支持
    - 3设备同步
    - 详细发展报告
    
  家庭版 (¥98/月):
    - 支持3个儿童档案
    - 所有高级功能
    - 5设备同步
    - 家庭共享空间
```

### 4.2 成长陪伴系统

```python
class GrowthCompanionSystem:
    """非功利性的成长激励"""
    
    MILESTONES = {
        10: {'reward': '成长纪念故事', 'type': 'content'},
        20: {'reward': '角色形象升级', 'type': 'visual'},
        50: {'reward': '专属故事宇宙', 'type': 'world'},
        100: {'reward': '年度成长编年史', 'type': 'collection'}
    }
    
    SPECIAL_MOMENTS = {
        'birthday_month': {
            'reward': '2次高级定制权限',
            'message': '生日月特别礼物'
        },
        'reading_anniversary': {
            'reward': '纪念故事集',
            'message': '我们一起走过的阅读时光'
        }
    }
```

------

## 第五部分：工程实施计划

### 5.1 开发路线图

#### Phase 1: MVP (0-3个月)

```yaml
核心功能:
  - 用户系统（注册/登录/儿童档案）
  - 基础故事生成（5个模板 + 100本预生产）
  - CROWD提示系统（基础版）
  - PWA客户端
  - 微信支付集成

技术目标:
  - 系统可用性 > 99%
  - 故事生成 < 30秒（模板）
  - 首屏加载 < 2秒

团队配置:
  - 全栈开发: 2人
  - UI/UX设计: 1人
  - 产品经理: 1人
```

#### Phase 2: 增长期 (3-6个月)

```yaml
功能扩展:
  - 神经多样性完整支持
  - Series Bible + LoRA一致性
  - 多设备同步
  - 智能推荐系统
  - 成长陪伴系统

技术优化:
  - 微服务架构迁移
  - 实时生成能力（GPU选配）
  - 数据分析平台
  - A/B测试框架
```

#### Phase 3: 成熟期 (6-12个月)

```yaml
创新功能:
  - 成人定制接口
  - AR/VR阅读体验
  - 语音交互
  - UGC内容市场
  - 教育效果评测

商业拓展:
  - B端幼儿园方案
  - 海外市场
  - IP授权合作
```

### 5.2 质量保证体系

```python
class QualityAssurance:
    """多层质量保证机制"""
    
    def content_safety_check(self, content):
        checks = [
            self.check_age_appropriateness(),
            self.check_cultural_sensitivity(),
            self.check_psychological_safety(),
            self.check_copyright_compliance()
        ]
        return all(checks)
    
    def technical_quality_metrics(self):
        return {
            'api_response_time': '<500ms (P95)',
            'story_generation': '<30s (template), <5min (custom)',
            'system_availability': '>99.5%',
            'user_satisfaction': '>4.5/5'
        }
```

------

## 第六部分：风险管理

### 6.1 技术风险

- **AI服务依赖**: 多供应商备份策略
- **内容一致性**: LoRA训练 + 人工审核
- **扩展性**: 云原生架构，弹性伸缩

### 6.2 业务风险

- **用户获取成本**: 口碑营销 + KOL合作
- **内容审核**: AI预审 + 人工复核
- **竞争壁垒**: 神经多样性专业度 + 数据积累

### 6.3 合规风险

- **儿童隐私**: COPPA/GDPR合规
- **内容安全**: 严格的内容过滤机制
- **支付安全**: PCI DSS标准

------

## 第七部分：成功指标

```yaml
用户指标:
  - MAU目标: 月1万（6个月）, 10万（12个月）
  - 留存率: D7 > 40%, D30 > 25%
  - NPS: > 50

业务指标:
  - 付费转化率: > 15%
  - 客单价: ¥35/月
  - LTV/CAC: > 3

教育指标:
  - 完读率: > 70%
  - CROWD互动率: > 60%
  - 家长满意度: > 4.5/5
```

------

## 附录A：API接口规范

```typescript
// 故事生成API
interface StoryGenerationAPI {
  endpoint: '/api/v1/stories/generate',
  method: 'POST',
  request: {
    childId: string,
    preferences: StoryPreferences,
    neuroAdaptations?: NeuroProfile,
    generationType: 'preproduced' | 'template' | 'realtime'
  },
  response: {
    storyId: string,
    status: 'ready' | 'generating',
    estimatedTime?: number,
    content?: StoryContent
  }
}
```

------

## 附录B：神经多样性设计指南

详细的ADHD和自闭谱系适配指南，包括：

- UI/UX设计原则
- 内容创作指导
- 交互设计规范
- 测试验证方法

------

 