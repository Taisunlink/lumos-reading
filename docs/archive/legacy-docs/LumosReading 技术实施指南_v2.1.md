# LumosReading 技术实施指南

## 快速开始
bash
git clone [repo]
cd lumos-reading
./scripts/init-project.sh
docker-compose up -d

## 项目结构

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



## 数据库设计
-- migrations/001_initial_schema.sql

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE,
    wechat_openid VARCHAR(100),
    email VARCHAR(255),
    password_hash VARCHAR(255),
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 儿童档案表
CREATE TABLE children_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    nickname VARCHAR(100),
    birthday DATE,
    gender VARCHAR(10),
    avatar_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    neuro_profile JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 故事表
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES children_profiles(id),
    title VARCHAR(200) NOT NULL,
    content JSONB NOT NULL,
    generation_type VARCHAR(20), -- 'preproduced', 'template', 'realtime'
    theme VARCHAR(100),
    age_group VARCHAR(20),
    reading_time INTEGER, -- 分钟
    word_count INTEGER,
    illustrations JSONB,
    interaction_points JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 阅读记录表
CREATE TABLE reading_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id),
    child_id UUID REFERENCES children_profiles(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    progress FLOAT DEFAULT 0,
    interaction_responses JSONB,
    duration INTEGER, -- 秒
    device_info JSONB
);

-- Series Bible表（角色一致性）
CREATE TABLE series_bibles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(200),
    characters JSONB NOT NULL,
    world_settings JSONB,
    narrative_rules JSONB,
    visual_assets JSONB,
    lora_models JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预生产内容库
CREATE TABLE preproduced_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content JSONB NOT NULL,
    age_group VARCHAR(20),
    theme VARCHAR(100),
    tags TEXT[],
    language VARCHAR(10),
    quality_score FLOAT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_children_user_id ON children_profiles(user_id);
CREATE INDEX idx_stories_child_id ON stories(child_id);
CREATE INDEX idx_reading_sessions_story_id ON reading_sessions(story_id);
CREATE INDEX idx_reading_sessions_child_id ON reading_sessions(child_id);
CREATE INDEX idx_preproduced_stories_theme ON preproduced_stories(theme);
CREATE INDEX idx_preproduced_stories_age_group ON preproduced_stories(age_group);



-- 新增表：用户留存机制相关

-- 阅读成就表
CREATE TABLE reading_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES children_profiles(id),
    achievement_type VARCHAR(50),  -- 'daily_streak', 'words_learned', 'stories_completed'
    achievement_value INTEGER,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reward_claimed BOOLEAN DEFAULT FALSE
);

-- 家庭共读会话表
CREATE TABLE family_reading_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id),
    primary_device_id VARCHAR(100),
    participant_devices JSONB,  -- 多设备同步信息
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_events JSONB  -- 翻页同步等事件
);

-- AI生成失败记录表（用于优化）
CREATE TABLE generation_failures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID,
    failure_stage VARCHAR(50),  -- 'framework', 'content', 'illustration'
    error_type VARCHAR(100),
    error_details JSONB,
    fallback_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 客服工单表
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    priority VARCHAR(20),  -- 'urgent', 'high', 'normal'
    category VARCHAR(50),  -- 'content_issue', 'technical', 'payment'
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_minutes INTEGER,
    resolution_notes TEXT
);

-- 已有的neuro_profile字段是JSONB，够灵活但需要规范化结构

-- 建议增加专门的表来存储神经多样性配置模板
CREATE TABLE neuro_diversity_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),  -- 'ADHD-轻度', 'ASD-感官敏感型'
    category VARCHAR(50),  -- 'ADHD', 'ASD', 'Dyslexia'
    configuration JSONB,  -- 详细配置
    created_by VARCHAR(50),  -- 'system' or 'expert'
    validated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 追踪神经多样性适配效果
CREATE TABLE neuro_adaptation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES children_profiles(id),
    story_id UUID REFERENCES stories(id),
    adaptation_applied JSONB,  -- 实际应用的适配
    effectiveness_score FLOAT,  -- 家长评分
    child_engagement_metrics JSONB,  -- 客观指标
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 在children_profiles表的neuro_profile字段规范化
ALTER TABLE children_profiles 
ADD COLUMN neuro_template_id UUID REFERENCES neuro_diversity_templates(id),
ADD COLUMN neuro_custom_settings JSONB;  -- 个性化微调



-- 社交关系表（预留）
CREATE TABLE social_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES children_profiles(id),
    friend_child_id UUID REFERENCES children_profiles(id),
    connection_type VARCHAR(50),  -- 'classmate', 'friend', 'sibling'
    status VARCHAR(20),  -- 'pending', 'active', 'blocked'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(child_id, friend_child_id)
);

-- 故事分享记录
CREATE TABLE story_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id),
    shared_by_child_id UUID REFERENCES children_profiles(id),
    shared_to_child_id UUID,  -- 可为空（分享到群）
    share_type VARCHAR(50),  -- 'direct', 'group', 'public_card'
    share_content JSONB,  -- 分享卡片内容
    interactions JSONB,  -- 点赞、评论等
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 阅读群组（班级、兴趣组等）
CREATE TABLE reading_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200),
    type VARCHAR(50),  -- 'class', 'family', 'interest'
    creator_user_id UUID REFERENCES users(id),
    settings JSONB,  -- 群组设置
    member_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 群组成员
CREATE TABLE group_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES reading_groups(id),
    child_id UUID REFERENCES children_profiles(id),
    role VARCHAR(20),  -- 'member', 'admin'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, child_id)
);

-- 成就定义表
CREATE TABLE achievement_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE,  -- 'first_story', 'reading_streak_7'
    name VARCHAR(200),
    description TEXT,
    category VARCHAR(50),  -- 'reading', 'interaction', 'social'
    icon_url VARCHAR(500),
    criteria JSONB,  -- 达成条件
    rewards JSONB,  -- 奖励内容
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);

-- 已经有了reading_achievements表，但需要增强
ALTER TABLE reading_achievements
ADD COLUMN achievement_definition_id UUID REFERENCES achievement_definitions(id),
ADD COLUMN progress JSONB,  -- 进度详情
ADD COLUMN metadata JSONB;  -- 扩展信息

-- 成就进度追踪（对于渐进式成就）
CREATE TABLE achievement_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES children_profiles(id),
    achievement_definition_id UUID REFERENCES achievement_definitions(id),
    current_value INTEGER,
    target_value INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(child_id, achievement_definition_id)
);

-- 积分/虚拟货币系统（未来货币化）
CREATE TABLE child_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES children_profiles(id) UNIQUE,
    total_points INTEGER DEFAULT 0,
    spent_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    level_progress FLOAT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 积分交易记录
CREATE TABLE point_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES children_profiles(id),
    points INTEGER,  -- 正为获得，负为消费
    transaction_type VARCHAR(50),  -- 'earned', 'spent', 'bonus'
    source VARCHAR(100),  -- 'story_complete', 'achievement', 'purchase'
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通用的功能开关表（方便A/B测试和渐进发布）
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_key VARCHAR(100) UNIQUE,  -- 'social_sharing', 'achievements_v2'
    is_enabled BOOLEAN DEFAULT FALSE,
    rollout_percentage INTEGER DEFAULT 0,  -- 灰度发布百分比
    user_whitelist JSONB,  -- 白名单用户
    configuration JSONB,  -- 功能配置
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户行为事件表（为了未来的数据分析）
CREATE TABLE user_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    child_id UUID REFERENCES children_profiles(id),
    event_type VARCHAR(100),  -- 'story_start', 'achievement_unlock'
    event_properties JSONB,  -- 灵活的属性
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 为events表建立分区（按月）以支持大数据量
CREATE TABLE user_events_2024_01 PARTITION OF user_events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

## API设计
 // 更新：api.d.ts - 新增关键接口

interface APIv2 {
  // 渐进式故事生成
  '/api/v2/stories/progressive-generate': {
    method: 'POST'
    request: {
      childId: string
      preferences: StoryPreferences
    }
    response: {
      // 立即返回
      immediate: {
        storyId: string
        title: string
        firstPage: PageContent
        estimatedTime: number
      }
      // WebSocket推送后续页面
      websocket: 'ws://api/stories/{storyId}/stream'
    }
  }

  // 故事降级获取
  '/api/v2/stories/fallback': {
    method: 'GET'
    request: {
      ageGroup: string
      previouslyRead: string[]  // 避免重复
    }
    response: {
      story: Story
      fallbackReason: string
    }
  }

  // 音频生成
  '/api/v2/audio/generate': {
    method: 'POST'
    request: {
      storyId: string
      voice: 'default' | 'parent' | 'character'
      speed: number
    }
    response: {
      audioUrl: string
      duration: number
    }
  }

  // 家庭共读同步
  '/api/v2/family/sync': {
    method: 'WebSocket'
    events: {
      'page_turn': { page: number, deviceId: string }
      'highlight': { paragraph: number, deviceId: string }
      'interaction': { response: string, deviceId: string }
    }
  }
}



interface AdultCustomizationAPI {
  // 1. 轻量级自助接口
  quickCustomization: {
    endpoint: '/api/v1/adult/quick-story',
    method: 'POST',
    params: {
      occasion: 'birthday' | 'anniversary' | 'apology' | 'proposal',
      protagonists: {
        main: { name: string, traits: string[] },
        secondary: { name: string, relationship: string }
      },
      keyMemories: string[],  // 3-5个关键回忆点
      tone: 'romantic' | 'humorous' | 'touching' | 'nostalgic',
      length: 'short' | 'medium' | 'long'  // 5/10/15页
    },
    response: {
      storyId: string,
      previewUrl: string,
      estimatedTime: number,
      price: number
    }
  },

  // 2. 深度定制接口（预留）
  deepCustomization: {
    endpoint: '/api/v1/adult/custom-project',
    method: 'POST',
    params: {
      projectType: 'family_history' | 'brand_story' | 'educational',
      briefDocument: File,  // 支持上传详细需求
      referenceImages: File[],  // 参考图片
      consultationRequest: boolean,  // 是否需要人工咨询
      budget: number,
      deadline: Date
    },
    workflow: {
      steps: [
        'AI初稿生成',
        '人工编辑优化',
        '客户确认',
        '精装制作'
      ]
    }
  }
}

