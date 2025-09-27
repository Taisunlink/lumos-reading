-- LumosReading 数据库初始化脚本
-- 创建基础表结构和索引

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
CREATE TABLE IF NOT EXISTS children_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
CREATE TABLE IF NOT EXISTS stories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
CREATE TABLE IF NOT EXISTS reading_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
CREATE TABLE IF NOT EXISTS series_bibles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
CREATE TABLE IF NOT EXISTS preproduced_stories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- AI Agent响应记录表
CREATE TABLE IF NOT EXISTS agent_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50),
    request_hash VARCHAR(64),
    response JSONB,
    tokens_used INTEGER,
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 生成失败记录表
CREATE TABLE IF NOT EXISTS generation_failures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID,
    failure_stage VARCHAR(50), -- 'framework', 'content', 'illustration'
    error_type VARCHAR(100),
    error_details JSONB,
    fallback_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_children_user_id ON children_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_stories_child_id ON stories(child_id);
CREATE INDEX IF NOT EXISTS idx_reading_sessions_story_id ON reading_sessions(story_id);
CREATE INDEX IF NOT EXISTS idx_reading_sessions_child_id ON reading_sessions(child_id);
CREATE INDEX IF NOT EXISTS idx_preproduced_stories_theme ON preproduced_stories(theme);
CREATE INDEX IF NOT EXISTS idx_preproduced_stories_age_group ON preproduced_stories(age_group);
CREATE INDEX IF NOT EXISTS idx_agent_responses_agent_type ON agent_responses(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_responses_created_at ON agent_responses(created_at);

-- 插入示例数据
INSERT INTO preproduced_stories (title, content, age_group, theme, tags, language, quality_score) VALUES
('小兔子的勇气', '{"pages": [{"text": "从前有一只小兔子，他很胆小...", "image": "rabbit_courage.jpg"}]}', '3-5', '勇气', ARRAY['勇气', '成长', '动物'], 'zh', 0.95),
('彩虹桥的传说', '{"pages": [{"text": "在遥远的天空之城...", "image": "rainbow_bridge.jpg"}]}', '6-8', '友谊', ARRAY['友谊', '奇幻', '彩虹'], 'zh', 0.92);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_children_profiles_updated_at BEFORE UPDATE ON children_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_series_bibles_updated_at BEFORE UPDATE ON series_bibles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
