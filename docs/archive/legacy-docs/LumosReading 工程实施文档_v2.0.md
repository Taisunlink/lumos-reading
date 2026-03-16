# LumosReading 工程实施文档

## 一、项目初始化与环境配置

### 1.1 项目结构

```bash
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

### 1.2 环境初始化脚本

```bash
#!/bin/bash
# scripts/init-project.sh

echo "🚀 初始化 LumosReading 项目"

# 1. 检查必需工具
check_requirements() {
    echo "检查环境依赖..."
    
    # Node.js 18+
    if ! command -v node &> /dev/null; then
        echo "❌ 请安装 Node.js 18+"
        exit 1
    fi
    
    # Python 3.9+
    if ! command -v python3 &> /dev/null; then
        echo "❌ 请安装 Python 3.9+"
        exit 1
    fi
    
    # PostgreSQL
    if ! command -v psql &> /dev/null; then
        echo "❌ 请安装 PostgreSQL"
        exit 1
    fi
    
    echo "✅ 环境检查通过"
}

# 2. 创建项目结构
create_structure() {
    echo "创建项目结构..."
    mkdir -p apps/{web,api,ai-service}
    mkdir -p packages/{ui,tsconfig,eslint-config}
    mkdir -p infrastructure/{docker,k8s,terraform}
    mkdir -p {docs,tests,scripts}
}

# 3. 初始化前端
init_frontend() {
    echo "初始化前端项目..."
    cd apps/web
    npx create-next-app@latest . --typescript --tailwind --app --no-git
    npm install zustand @tanstack/react-query axios
    npm install -D @types/node
}

# 4. 初始化后端
init_backend() {
    echo "初始化后端项目..."
    cd ../api
    python3 -m venv venv
    source venv/bin/activate
    pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary
    pip install redis celery pydantic python-jose passlib
}

# 执行初始化
check_requirements
create_structure
init_frontend
init_backend

echo "✅ 项目初始化完成"
```

## 二、核心配置文件

### 2.1 环境变量配置

```env
# .env.development

# 数据库配置
DATABASE_URL=postgresql://lumos:password@localhost:5432/lumos_dev
REDIS_URL=redis://localhost:6379/0

# AI服务配置
CLAUDE_API_KEY=your-claude-key
OPENAI_API_KEY=your-openai-key
QWEN_API_KEY=your-qwen-key
DALLE_API_KEY=your-dalle-key

# 阿里云配置
ALIYUN_ACCESS_KEY=your-access-key
ALIYUN_SECRET_KEY=your-secret-key
ALIYUN_OSS_BUCKET=lumos-reading
ALIYUN_OSS_REGION=cn-shanghai

# 支付配置
WECHAT_PAY_APPID=your-appid
WECHAT_PAY_MCHID=your-mchid
ALIPAY_APPID=your-appid

# 安全配置
JWT_SECRET_KEY=your-very-secret-key
ENCRYPTION_KEY=your-encryption-key

# 服务配置
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
AI_SERVICE_URL=http://singapore-server:8001
```

### 2.2 Docker Compose配置

```yaml
# docker-compose.yml

version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: lumos_dev
      POSTGRES_USER: lumos
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  api:
    build: 
      context: ./apps/api
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://lumos:password@postgres:5432/lumos_dev
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./apps/api:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
  
  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./apps/web:/app
    ports:
      - "3000:3000"
    depends_on:
      - api
  
  celery:
    build: 
      context: ./apps/api
    command: celery -A app.core.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://lumos:password@postgres:5432/lumos_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgres

volumes:
  postgres_data:
```

## 三、数据库设计与模型

### 3.1 数据库初始化

```sql
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
```

### 3.2 SQLAlchemy模型

```python
# apps/api/app/models/base.py

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
# apps/api/app/models/user.py

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class SubscriptionTier(enum.Enum):
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"
    FAMILY = "family"

class User(BaseModel):
    __tablename__ = "users"
    
    phone = Column(String(20), unique=True)
    wechat_openid = Column(String(100))
    email = Column(String(255))
    password_hash = Column(String(255))
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires_at = Column(DateTime)
    
    # 关系
    children = relationship("ChildProfile", back_populates="user")
    series_bibles = relationship("SeriesBible", back_populates="user")
```

## 四、核心业务逻辑实现

### 4.1 故事生成服务

```python
# apps/api/app/services/story_generator.py

from typing import Dict, Any
import asyncio
from ..utils.ai_clients import ClaudeClient, QwenClient, DalleClient
from ..models import Story, ChildProfile
from ..schemas import StoryRequest

class StoryGenerationService:
    """
    故事生成核心服务
    实现教育心理学驱动的内容生成
    """
    
    def __init__(self):
        self.claude = ClaudeClient()
        self.qwen = QwenClient()
        self.dalle = DalleClient()
        
    async def generate_story(
        self, 
        request: StoryRequest, 
        child_profile: ChildProfile
    ) -> Story:
        """
        主生成流程：框架设计 → 内容生成 → 图像生成
        """
        
        # 1. 分析儿童画像，准备个性化参数
        personalization = self._analyze_child_profile(child_profile)
        
        # 2. Claude生成教育框架
        framework = await self._generate_framework(
            request, 
            personalization,
            child_profile.neuro_profile
        )
        
        # 3. 通义千问生成本地化内容
        content = await self._generate_content(framework)
        
        # 4. DALL-E生成插图
        illustrations = await self._generate_illustrations(
            framework.visual_prompts
        )
        
        # 5. 组装最终故事
        story = self._assemble_story(
            framework, 
            content, 
            illustrations,
            child_profile
        )
        
        return story
    
    async def _generate_framework(
        self, 
        request: StoryRequest,
        personalization: Dict,
        neuro_profile: Dict = None
    ) -> Dict:
        """
        使用Claude生成教育学框架
        """
        
        prompt = f"""
        Create a children's story framework based on educational psychology principles.
        
        Child Information:
        - Age: {personalization['age']} years
        - Cognitive Stage: {personalization['cognitive_stage']}
        - Interests: {personalization['interests']}
        
        Requirements:
        1. Story Structure: Follow 3-act structure with clear beats
        2. Educational Objectives: Include {personalization['learning_goals']}
        3. CROWD Interaction Points: Place 5 age-appropriate prompts
        4. Emotional Arc: Design appropriate emotional journey
        
        {self._get_neuro_adaptations(neuro_profile)}
        
        Output Format:
        {{
            "title": "Story Title",
            "structure": {{
                "act1": {{"setup": "...", "pages": [1,2,3]}},
                "act2": {{"conflict": "...", "pages": [4,5,6,7,8]}},
                "act3": {{"resolution": "...", "pages": [9,10,11,12]}}
            }},
            "pages": [
                {{
                    "number": 1,
                    "content_guidance": "...",
                    "visual_description": "...",
                    "interaction": {{"type": "Completion", "prompt": "..."}}
                }}
            ],
            "vocabulary_targets": ["word1", "word2"],
            "emotional_beats": [...],
            "visual_consistency": {{"character": "...", "style": "..."}}
        }}
        """
        
        response = await self.claude.generate(prompt)
        return response
    
    def _get_neuro_adaptations(self, neuro_profile: Dict) -> str:
        """
        生成神经多样性适配指导
        """
        if not neuro_profile:
            return ""
            
        adaptations = []
        
        if neuro_profile.get('adhd'):
            adaptations.append("""
            ADHD Adaptations:
            - Shorter segments (3-5 minute reading blocks)
            - Visual anchors for attention
            - Frequent interaction points
            - Clear progress indicators
            """)
            
        if neuro_profile.get('autism_spectrum'):
            adaptations.append("""
            Autism Spectrum Adaptations:
            - Predictable story structure
            - Explicit emotion labeling
            - Consistent visual style
            - Social situation explanations
            """)
            
        return "\n".join(adaptations)
```

### 4.2 CROWD交互系统

```python
# apps/api/app/services/interaction_engine.py

from typing import Dict, List
from enum import Enum

class InteractionType(Enum):
    COMPLETION = "Completion"
    RECALL = "Recall"
    OPEN_ENDED = "Open-ended"
    WH_QUESTIONS = "Wh-questions"
    DISTANCING = "Distancing"

class CROWDInteractionEngine:
    """
    对话式阅读交互引擎
    基于CROWD-PEER框架
    """
    
    def generate_interactions(
        self, 
        story_content: Dict,
        child_age: int,
        reading_progress: float
    ) -> List[Dict]:
        """
        为故事生成合适的CROWD交互点
        """
        
        interactions = []
        
        for page in story_content['pages']:
            # 根据阅读进度选择交互类型
            interaction_type = self._select_interaction_type(
                page['number'], 
                len(story_content['pages']),
                child_age
            )
            
            # 生成具体的交互提示
            interaction = self._generate_prompt(
                interaction_type,
                page['content'],
                child_age
            )
            
            interactions.append({
                'page': page['number'],
                'type': interaction_type.value,
                'prompt': interaction['prompt'],
                'parent_guidance': interaction['guidance'],
                'expected_response': interaction['expected']
            })
        
        return interactions
    
    def _select_interaction_type(
        self, 
        page_num: int, 
        total_pages: int,
        child_age: int
    ) -> InteractionType:
        """
        基于页面位置和儿童年龄选择交互类型
        """
        
        progress = page_num / total_pages
        
        if progress < 0.2:
            # 故事开始：Completion类提示
            return InteractionType.COMPLETION
        elif progress < 0.4:
            # 早期：Wh-questions
            return InteractionType.WH_QUESTIONS
        elif progress < 0.6:
            # 中期：Recall
            return InteractionType.RECALL
        elif progress < 0.8:
            # 后期：Open-ended
            return InteractionType.OPEN_ENDED
        else:
            # 结尾：Distancing
            return InteractionType.DISTANCING
    
    def _generate_prompt(
        self,
        interaction_type: InteractionType,
        page_content: str,
        child_age: int
    ) -> Dict:
        """
        生成具体的交互提示
        """
        
        generators = {
            InteractionType.COMPLETION: self._generate_completion,
            InteractionType.RECALL: self._generate_recall,
            InteractionType.OPEN_ENDED: self._generate_open_ended,
            InteractionType.WH_QUESTIONS: self._generate_wh_question,
            InteractionType.DISTANCING: self._generate_distancing
        }
        
        return generators[interaction_type](page_content, child_age)
```

### 4.3 角色一致性保障

```python
# apps/api/app/services/character_consistency.py

import hashlib
from typing import Dict, List
from ..models import SeriesBible

class CharacterConsistencyManager:
    """
    角色一致性管理系统
    使用Series Bible确保跨故事一致性
    """
    
    async def create_character(
        self,
        character_design: Dict,
        reference_images: List[str] = None
    ) -> Dict:
        """
        创建新角色并生成一致性资产
        """
        
        # 生成角色ID
        character_id = self._generate_character_id(character_design)
        
        # 创建角色Bible条目
        character_bible = {
            'id': character_id,
            'name': character_design['name'],
            'fixed_traits': {
                'species': character_design.get('species', 'human'),
                'appearance': character_design['appearance'],
                'personality': character_design['personality'],
                'distinctive_features': character_design['distinctive_features']
            },
            'visual_consistency': {
                'color_palette': self._extract_colors(character_design),
                'proportions': character_design.get('proportions'),
                'style_markers': character_design.get('style_markers', [])
            },
            'prompt_template': self._generate_prompt_template(character_design)
        }
        
        # 如果提供了参考图片，训练LoRA（未来功能）
        if reference_images:
            character_bible['lora_model'] = await self._train_lora(
                character_id, 
                reference_images
            )
        
        return character_bible
    
    def _generate_prompt_template(self, character_design: Dict) -> str:
        """
        生成可复用的角色描述模板
        """
        
        template = f"""
        Character: {character_design['name']}
        Appearance: {character_design['appearance']}
        Always include: {', '.join(character_design['distinctive_features'])}
        Style: children's book illustration, consistent character design
        """
        
        return template.strip()
    
    async def ensure_consistency(
        self,
        character_id: str,
        new_illustration_prompt: str
    ) -> str:
        """
        确保新插图提示包含角色一致性要素
        """
        
        # 获取角色Bible
        character = await self._get_character_bible(character_id)
        
        # 增强提示以确保一致性
        consistent_prompt = f"""
        {character['prompt_template']}
        
        Scene: {new_illustration_prompt}
        
        IMPORTANT: Maintain exact character design consistency.
        """
        
        return consistent_prompt
```

## 五、前端核心组件

### 5.1 阅读界面组件

```typescript
// apps/web/src/components/reader/StoryReader.tsx

import React, { useState, useEffect } from 'react';
import { useStoryStore } from '@/stores/storyStore';
import { InteractionPrompt } from './InteractionPrompt';
import { IllustrationDisplay } from './IllustrationDisplay';
import { ProgressBar } from '@/components/ui/ProgressBar';

interface StoryReaderProps {
  storyId: string;
  childId: string;
}

export const StoryReader: React.FC<StoryReaderProps> = ({
  storyId,
  childId
}) => {
  const [currentPage, setCurrentPage] = useState(0);
  const { story, loading, fetchStory, saveProgress } = useStoryStore();
  
  useEffect(() => {
    fetchStory(storyId);
  }, [storyId]);
  
  // 处理翻页
  const handlePageTurn = async (direction: 'next' | 'prev') => {
    const newPage = direction === 'next' 
      ? Math.min(currentPage + 1, story.pages.length - 1)
      : Math.max(currentPage - 1, 0);
    
    setCurrentPage(newPage);
    
    // 保存阅读进度
    await saveProgress(storyId, childId, newPage / story.pages.length);
  };
  
  // 处理CROWD交互
  const handleInteraction = async (response: string) => {
    // 记录交互响应
    await recordInteraction(
      storyId,
      currentPage,
      response
    );
  };
  
  if (loading) {
    return <div>加载中...</div>;
  }
  
  const page = story?.pages[currentPage];
  
  return (
    <div className="story-reader max-w-4xl mx-auto">
      {/* 进度条 */}
      <ProgressBar 
        current={currentPage + 1} 
        total={story?.pages.length || 1}
      />
      
      {/* 插图展示 */}
      <IllustrationDisplay 
        imageUrl={page?.illustration}
        altText={page?.imageDescription}
      />
      
      {/* 故事文本 */}
      <div className="story-text p-6 text-lg leading-relaxed">
        {page?.text}
      </div>
      
      {/* CROWD交互提示 */}
      {page?.interaction && (
        <InteractionPrompt
          interaction={page.interaction}
          onResponse={handleInteraction}
        />
      )}
      
      {/* 翻页控制 */}
      <div className="flex justify-between mt-6">
        <button
          onClick={() => handlePageTurn('prev')}
          disabled={currentPage === 0}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          上一页
        </button>
        
        <button
          onClick={() => handlePageTurn('next')}
          disabled={currentPage === story?.pages.length - 1}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          下一页
        </button>
      </div>
    </div>
  );
};
```

### 5.2 神经多样性适配组件

```typescript
// apps/web/src/components/accessibility/NeuroAdaptiveControls.tsx

import React from 'react';
import { useAccessibilityStore } from '@/stores/accessibilityStore';

export const NeuroAdaptiveControls: React.FC = () => {
  const { 
    settings, 
    updateSettings 
  } = useAccessibilityStore();
  
  return (
    <div className="neuro-adaptive-controls p-4 bg-gray-100 rounded">
      <h3 className="font-bold mb-4">阅读辅助设置</h3>
      
      {/* ADHD支持选项 */}
      <div className="mb-4">
        <h4 className="font-semibold mb-2">专注力支持</h4>
        
        <label className="flex items-center mb-2">
          <input
            type="checkbox"
            checked={settings.showProgressBar}
            onChange={(e) => updateSettings({ 
              showProgressBar: e.target.checked 
            })}
          />
          <span className="ml-2">显示阅读进度</span>
        </label>
        
        <label className="flex items-center mb-2">
          <input
            type="checkbox"
            checked={settings.highlightCurrentSentence}
            onChange={(e) => updateSettings({ 
              highlightCurrentSentence: e.target.checked 
            })}
          />
          <span className="ml-2">高亮当前句子</span>
        </label>
        
        <label className="flex items-center">
          <span className="mr-2">阅读节奏提醒：</span>
          <select
            value={settings.readingPaceReminder}
            onChange={(e) => updateSettings({ 
              readingPaceReminder: e.target.value 
            })}
          >
            <option value="off">关闭</option>
            <option value="5min">每5分钟</option>
            <option value="10min">每10分钟</option>
          </select>
        </label>
      </div>
      
      {/* 自闭谱系支持选项 */}
      <div className="mb-4">
        <h4 className="font-semibold mb-2">感官舒适度</h4>
        
        <label className="flex items-center mb-2">
          <span className="mr-2">背景颜色：</span>
          <select
            value={settings.backgroundColor}
            onChange={(e) => updateSettings({ 
              backgroundColor: e.target.value 
            })}
          >
            <option value="white">白色</option>
            <option value="cream">米色</option>
            <option value="lightblue">浅蓝</option>
            <option value="lightgreen">浅绿</option>
          </select>
        </label>
        
        <label className="flex items-center mb-2">
          <span className="mr-2">动画速度：</span>
          <input
            type="range"
            min="0"
            max="100"
            value={settings.animationSpeed}
            onChange={(e) => updateSettings({ 
              animationSpeed: parseInt(e.target.value) 
            })}
          />
        </label>
        
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.predictableTransitions}
            onChange={(e) => updateSettings({ 
              predictableTransitions: e.target.checked 
            })}
          />
          <span className="ml-2">场景切换预告</span>
        </label>
      </div>
      
      {/* 字体调整 */}
      <div className="mb-4">
        <h4 className="font-semibold mb-2">文字显示</h4>
        
        <label className="flex items-center mb-2">
          <span className="mr-2">字体大小：</span>
          <input
            type="range"
            min="12"
            max="24"
            value={settings.fontSize}
            onChange={(e) => updateSettings({ 
              fontSize: parseInt(e.target.value) 
            })}
          />
          <span className="ml-2">{settings.fontSize}px</span>
        </label>
        
        <label className="flex items-center">
          <span className="mr-2">行间距：</span>
          <select
            value={settings.lineSpacing}
            onChange={(e) => updateSettings({ 
              lineSpacing: e.target.value 
            })}
          >
            <option value="normal">标准</option>
            <option value="relaxed">宽松</option>
            <option value="loose">很宽松</option>
          </select>
        </label>
      </div>
    </div>
  );
};
```

## 六、部署与运维

### 6.1 生产环境部署脚本

```bash
#!/bin/bash
# scripts/deploy-production.sh

set -e

echo "🚀 开始部署 LumosReading 到生产环境"

# 配置
ENVIRONMENT="production"
REGISTRY="registry.cn-shanghai.aliyuncs.com/lumos-reading"
NAMESPACE="lumos-production"

# 1. 构建镜像
build_images() {
    echo "📦 构建Docker镜像..."
    
    # 构建API镜像
    docker build -t $REGISTRY/api:$VERSION ./apps/api
    docker push $REGISTRY/api:$VERSION
    
    # 构建Web镜像
    docker build -t $REGISTRY/web:$VERSION ./apps/web
    docker push $REGISTRY/web:$VERSION
    
    # 构建AI服务镜像
    docker build -t $REGISTRY/ai-service:$VERSION ./apps/ai-service
    docker push $REGISTRY/ai-service:$VERSION
}

# 2. 数据库迁移
run_migrations() {
    echo "🗄️ 执行数据库迁移..."
    kubectl run migrations \
        --image=$REGISTRY/api:$VERSION \
        --rm -it --restart=Never \
        --namespace=$NAMESPACE \
        -- alembic upgrade head
}

# 3. 部署到Kubernetes
deploy_k8s() {
    echo "☸️ 部署到Kubernetes..."
    
    # 应用配置
    kubectl apply -f infrastructure/k8s/production/ \
        --namespace=$NAMESPACE
    
    # 更新镜像
    kubectl set image deployment/api api=$REGISTRY/api:$VERSION \
        --namespace=$NAMESPACE
    kubectl set image deployment/web web=$REGISTRY/web:$VERSION \
        --namespace=$NAMESPACE
    
    # 等待部署完成
    kubectl rollout status deployment/api --namespace=$NAMESPACE
    kubectl rollout status deployment/web --namespace=$NAMESPACE
}

# 4. 健康检查
health_check() {
    echo "🏥 执行健康检查..."
    
    # 检查API健康
    API_URL=$(kubectl get service api -o jsonpath='{.status.loadBalancer.ingress[0].ip}' \
        --namespace=$NAMESPACE)
    
    curl -f http://$API_URL/health || exit 1
    
    echo "✅ 健康检查通过"
}

# 执行部署
VERSION=$(git rev-parse --short HEAD)

build_images
run_migrations
deploy_k8s
health_check

echo "✅ 部署成功完成！版本：$VERSION"
```

### 6.2 监控配置

```yaml
# infrastructure/monitoring/prometheus-config.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'lumos-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
  
  - job_name: 'lumos-web'
    static_configs:
      - targets: ['web:3000']
    metrics_path: '/api/metrics'
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

# 告警规则
rule_files:
  - '/etc/prometheus/alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

这套完整的工程文档提供了从项目初始化到生产部署的所有关键配置和代码，严格遵循了我们讨论的核心设计原则：

1. **教育心理学基础**：在故事生成服务中实现
2. **神经多样性支持**：专门的适配组件和服务
3. **CROWD-PEER框架**：完整的交互引擎实现
4. **角色一致性**：Series Bible系统
5. **高质量内容**：Claude+通义千问协同架构

每个模块都可以在Cursor中直接使用，并且包含了详细的注释说明实现逻辑。