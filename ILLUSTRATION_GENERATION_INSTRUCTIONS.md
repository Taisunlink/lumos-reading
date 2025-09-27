# 🎨 LumosReading 图像生成系统实施指令

## 📋 概述
为LumosReading实现完整的AI图像生成系统，支持故事插图自动生成、角色一致性保持和儿童友好的视觉效果。

## 🎯 核心目标
1. **替换图像占位符** - 实现真实的AI生成插图
2. **角色一致性** - 通过Series Bible确保角色外观统一
3. **儿童友好** - 适合3-11岁儿童的视觉风格
4. **性能优化** - 图像缓存和CDN分发

## 🏗️ 系统架构

### Backend图像服务 (`apps/api/app/services/illustration_service.py`)

```python
from openai import OpenAI
from typing import Dict, List, Optional
import asyncio
import hashlib
import json
from datetime import datetime
from app.core.config import settings
from app.models.story import Story
from app.models.illustration import Illustration  # 新建模型

class IllustrationService:
    """AI图像生成服务 - 支持DALL-E 3和角色一致性"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.base_style_prompt = (
            "Children's book illustration style, warm and friendly, "
            "soft colors, cartoon-like but detailed, safe for ages 3-11, "
            "Chinese cultural elements when appropriate"
        )

    async def generate_story_illustration(
        self,
        story_id: str,
        page_number: int,
        illustration_prompt: str,
        character_bible: Optional[Dict] = None
    ) -> Dict:
        """为故事页面生成插图"""

        # 1. 增强提示词
        enhanced_prompt = await self._enhance_prompt_with_characters(
            illustration_prompt, character_bible
        )

        # 2. 检查缓存
        cache_key = self._generate_cache_key(enhanced_prompt)
        cached_url = await self._get_cached_illustration(cache_key)
        if cached_url:
            return {"url": cached_url, "cached": True}

        # 3. 调用DALL-E 3生成
        try:
            response = await asyncio.to_thread(
                self.openai_client.images.generate,
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                style="vivid",
                n=1
            )

            image_url = response.data[0].url

            # 4. 下载并存储到OSS
            stored_url = await self._store_image(image_url, cache_key)

            # 5. 保存到数据库
            await self._save_illustration_record(
                story_id, page_number, stored_url, enhanced_prompt
            )

            return {"url": stored_url, "cached": False}

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            # 降级到预设图像
            return await self._get_fallback_image(illustration_prompt)

    async def _enhance_prompt_with_characters(
        self,
        base_prompt: str,
        character_bible: Optional[Dict]
    ) -> str:
        """使用角色圣经增强提示词"""

        enhanced = f"{self.base_style_prompt}. {base_prompt}"

        if character_bible and character_bible.get("characters"):
            char_descriptions = []
            for char in character_bible["characters"]:
                char_desc = (
                    f"{char['name']}: {char['visual_description']}, "
                    f"personality: {char['personality']}"
                )
                char_descriptions.append(char_desc)

            enhanced += f". Characters in scene: {'; '.join(char_descriptions)}"

        # 确保长度不超过DALL-E限制
        if len(enhanced) > 4000:
            enhanced = enhanced[:3900] + "..."

        return enhanced

    async def _store_image(self, image_url: str, cache_key: str) -> str:
        """下载图像并存储到OSS/本地存储"""
        import aiohttp
        import aiofiles
        import os

        # 下载图像
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()

                    # 生成文件名
                    filename = f"illustrations/{cache_key}.png"
                    local_path = f"/tmp/claude/{filename}"

                    # 确保目录存在
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)

                    # 保存到本地（生产环境应上传到OSS）
                    async with aiofiles.open(local_path, 'wb') as f:
                        await f.write(image_data)

                    # 返回访问URL（生产环境应返回CDN URL）
                    return f"/api/static/illustrations/{cache_key}.png"

        raise Exception("Failed to download and store image")

    def _generate_cache_key(self, prompt: str) -> str:
        """生成缓存键"""
        return hashlib.md5(prompt.encode()).hexdigest()

    async def _get_cached_illustration(self, cache_key: str) -> Optional[str]:
        """检查缓存中的插图"""
        # 实现Redis或数据库缓存查询
        return None  # 暂时返回None，实际应查询缓存

    async def _save_illustration_record(
        self,
        story_id: str,
        page_number: int,
        image_url: str,
        prompt: str
    ):
        """保存插图记录到数据库"""
        from app.core.database import get_db_session

        async with get_db_session() as db:
            illustration = Illustration(
                story_id=story_id,
                page_number=page_number,
                image_url=image_url,
                generation_prompt=prompt,
                created_at=datetime.now()
            )
            db.add(illustration)
            await db.commit()

    async def _get_fallback_image(self, prompt: str) -> Dict:
        """获取降级图像（预设占位符）"""
        return {
            "url": "/api/static/placeholders/default_story.png",
            "cached": False,
            "fallback": True
        }

# 批量生成服务
class BatchIllustrationService:
    """批量图像生成服务 - 用于故事完整生成"""

    def __init__(self):
        self.illustration_service = IllustrationService()

    async def generate_all_story_illustrations(
        self,
        story_id: str,
        progress_callback: Optional[callable] = None
    ) -> List[Dict]:
        """为整个故事生成所有插图"""

        from app.core.database import get_db_session

        async with get_db_session() as db:
            story = await db.get(Story, story_id)
            if not story:
                raise ValueError(f"Story {story_id} not found")

            pages = story.content.get("pages", [])
            character_bible = story.content.get("characters", [])

            results = []
            total_pages = len(pages)

            for i, page in enumerate(pages):
                if "illustration_prompt" in page:
                    illustration = await self.illustration_service.generate_story_illustration(
                        story_id=story_id,
                        page_number=page["page_number"],
                        illustration_prompt=page["illustration_prompt"],
                        character_bible={"characters": character_bible}
                    )

                    results.append({
                        "page_number": page["page_number"],
                        "illustration": illustration
                    })

                    # 调用进度回调
                    if progress_callback:
                        await progress_callback({
                            "type": "illustration_generated",
                            "page_number": page["page_number"],
                            "progress": (i + 1) / total_pages * 100,
                            "illustration_url": illustration["url"]
                        })

            return results
```

### 数据库模型 (`apps/api/app/models/illustration.py`)

```python
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class Illustration(Base):
    """插图模型"""
    __tablename__ = "illustrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    image_url = Column(String(500), nullable=False)
    generation_prompt = Column(Text, nullable=False)
    cache_key = Column(String(64), nullable=False, index=True)
    is_cached = Column(Boolean, default=False)
    generation_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

### API路由 (`apps/api/app/routers/illustrations.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.illustration_service import IllustrationService, BatchIllustrationService
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/stories/{story_id}/illustrations/generate-all")
async def generate_all_story_illustrations(
    story_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """为故事生成所有插图（后台任务）"""

    batch_service = BatchIllustrationService()

    # 添加后台任务
    background_tasks.add_task(
        batch_service.generate_all_story_illustrations,
        story_id
    )

    return {"message": "Illustration generation started", "story_id": story_id}

@router.post("/stories/{story_id}/pages/{page_number}/illustration")
async def generate_page_illustration(
    story_id: str,
    page_number: int,
    illustration_prompt: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """为单个页面生成插图"""

    service = IllustrationService()

    illustration = await service.generate_story_illustration(
        story_id=story_id,
        page_number=page_number,
        illustration_prompt=illustration_prompt
    )

    return illustration

@router.get("/stories/{story_id}/illustrations")
async def get_story_illustrations(
    story_id: str,
    db: Session = Depends(get_db)
):
    """获取故事的所有插图"""

    illustrations = db.query(Illustration).filter(
        Illustration.story_id == story_id
    ).order_by(Illustration.page_number).all()

    return illustrations
```

## 🎨 Frontend 图像组件

### 智能图像组件 (`apps/web/src/components/illustration/SmartImage.tsx`)

```tsx
'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Image as ImageIcon, Loader2, AlertCircle } from 'lucide-react'

interface SmartImageProps {
  src?: string
  alt: string
  generationPrompt?: string
  storyId?: string
  pageNumber?: number
  autoGenerate?: boolean
  className?: string
  fallbackSrc?: string
}

export function SmartImage({
  src,
  alt,
  generationPrompt,
  storyId,
  pageNumber,
  autoGenerate = false,
  className = "",
  fallbackSrc = "/images/story-placeholder.svg"
}: SmartImageProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(src || null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  // 自动生成逻辑
  useEffect(() => {
    if (autoGenerate && !imageUrl && generationPrompt && storyId && pageNumber) {
      generateIllustration()
    }
  }, [autoGenerate, generationPrompt, storyId, pageNumber])

  const generateIllustration = async () => {
    if (!generationPrompt || !storyId || !pageNumber) return

    setIsGenerating(true)
    setError(null)

    try {
      const response = await fetch(
        `/api/stories/${storyId}/pages/${pageNumber}/illustration`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ illustration_prompt: generationPrompt })
        }
      )

      if (!response.ok) throw new Error('Generation failed')

      const result = await response.json()
      setImageUrl(result.url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setImageUrl(fallbackSrc) // 使用降级图像
    } finally {
      setIsGenerating(false)
    }
  }

  const handleImageLoad = () => {
    setIsLoaded(true)
  }

  const handleImageError = () => {
    setError('Image load failed')
    setImageUrl(fallbackSrc)
  }

  return (
    <div className={`relative overflow-hidden bg-gray-100 rounded-lg ${className}`}>
      {/* 加载状态 */}
      {isGenerating && (
        <motion.div
          className="absolute inset-0 flex items-center justify-center bg-white/90 z-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
            <p className="text-sm text-gray-600">正在生成插图...</p>
          </div>
        </motion.div>
      )}

      {/* 错误状态 */}
      {error && !isGenerating && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-50 z-10">
          <div className="text-center">
            <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p className="text-sm text-red-600">{error}</p>
            {generationPrompt && (
              <button
                onClick={generateIllustration}
                className="mt-2 px-3 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600"
              >
                重新生成
              </button>
            )}
          </div>
        </div>
      )}

      {/* 图像显示 */}
      {imageUrl && (
        <motion.img
          src={imageUrl}
          alt={alt}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          onLoad={handleImageLoad}
          onError={handleImageError}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: isLoaded ? 1 : 0, scale: 1 }}
          transition={{ duration: 0.3 }}
        />
      )}

      {/* 占位符 */}
      {!imageUrl && !isGenerating && !error && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <ImageIcon className="w-12 h-12 mx-auto mb-2" />
            <p className="text-sm">暂无插图</p>
            {generationPrompt && (
              <button
                onClick={generateIllustration}
                className="mt-2 px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                生成插图
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
```

### 故事页面渲染器更新 (`apps/web/src/components/story-reader/StoryPageRenderer.tsx`)

```tsx
'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { SmartImage } from '@/components/illustration/SmartImage'
import { useNeuroAdaptiveStore } from '@/stores/neuro-adaptive'

interface StoryPage {
  page_number: number
  text: string
  illustration_prompt?: string
  illustration_url?: string
  crowd_prompt?: any
  reading_time_seconds: number
  word_count: number
}

interface StoryPageRendererProps {
  page: StoryPage
  storyId: string
  onReadComplete?: () => void
  className?: string
}

export function StoryPageRenderer({
  page,
  storyId,
  onReadComplete,
  className = ""
}: StoryPageRendererProps) {
  const { adaptations } = useNeuroAdaptiveStore()

  return (
    <motion.div
      className={`story-page ${className}`}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.4 }}
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* 插图区域 */}
        <div className="order-1 lg:order-1">
          <SmartImage
            src={page.illustration_url}
            alt={`故事插图 - 第${page.page_number}页`}
            generationPrompt={page.illustration_prompt}
            storyId={storyId}
            pageNumber={page.page_number}
            autoGenerate={!page.illustration_url && !!page.illustration_prompt}
            className="w-full aspect-square max-w-md mx-auto"
          />
        </div>

        {/* 文本区域 */}
        <div className="order-2 lg:order-2">
          <motion.div
            className="prose prose-lg max-w-none"
            style={{
              fontSize: `${adaptations?.textSize || 16}px`,
              lineHeight: adaptations?.lineHeight || 1.6,
              fontFamily: adaptations?.fontFamily || 'inherit'
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
          >
            <p className="text-gray-800 leading-relaxed">
              {page.text}
            </p>
          </motion.div>

          {/* 阅读完成按钮 */}
          {onReadComplete && (
            <motion.button
              onClick={onReadComplete}
              className="mt-6 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4, duration: 0.2 }}
            >
              我读完了 →
            </motion.button>
          )}
        </div>
      </div>

      {/* 页面信息 */}
      <div className="mt-8 text-center text-sm text-gray-500">
        第 {page.page_number} 页 | 预计阅读时间 {page.reading_time_seconds} 秒
      </div>
    </motion.div>
  )
}
```

## ⚙️ 配置与环境

### 环境变量更新 (`apps/api/.env`)

```bash
# 在现有配置基础上添加
OPENAI_API_KEY=your_openai_api_key_here
ILLUSTRATION_STORAGE_TYPE=local  # local, oss, s3
ILLUSTRATION_CACHE_TTL=3600
DALLE_MODEL=dall-e-3
DALLE_SIZE=1024x1024
DALLE_QUALITY=standard
```

### 依赖包更新

**Backend** (`apps/api/requirements.txt`):
```txt
# 添加到现有依赖
openai>=1.10.0
aiofiles>=23.0.0
aiohttp>=3.9.0
Pillow>=10.0.0
```

**Frontend** (`apps/web/package.json`):
```json
{
  "dependencies": {
    // 现有依赖保持不变，无需添加新包
  }
}
```

## 🚀 实施步骤

### 第一步：后端服务实施
1. **创建插图服务模块**：
   - `apps/api/app/services/illustration_service.py`
   - `apps/api/app/models/illustration.py`
   - `apps/api/app/routers/illustrations.py`

2. **更新主应用**：
   - 在 `main.py` 中注册新路由
   - 更新数据库迁移

3. **添加静态文件服务**：
   - 配置 `/api/static/` 路径服务本地图像

### 第二步：前端组件实施
1. **创建图像组件**：
   - `apps/web/src/components/illustration/SmartImage.tsx`
   - 更新 `StoryPageRenderer.tsx`

2. **API客户端更新**：
   - 添加插图生成相关的API调用函数

### 第三步：集成测试
1. **单页面测试**：测试单个页面的插图生成
2. **完整故事测试**：测试整个故事的批量生成
3. **降级测试**：测试API失败时的降级处理

### 第四步：性能优化
1. **添加图像缓存**：Redis缓存生成的图像URL
2. **批量优化**：支持故事级别的批量生成
3. **CDN配置**：生产环境的图像CDN分发

## 📊 质量标准

### 功能验收标准
- ✅ 故事页面显示真实AI生成的插图（非占位符）
- ✅ 插图风格符合儿童绘本标准
- ✅ 角色在多页面中保持视觉一致性
- ✅ 图像生成失败时有合理的降级处理
- ✅ 生成过程有用户友好的加载状态

### 性能标准
- ✅ 单张图像生成时间 < 30秒
- ✅ 图像加载时间 < 3秒
- ✅ 缓存命中率 > 60%
- ✅ 系统在图像生成失败时不崩溃

### 用户体验标准
- ✅ 生成过程有清晰的进度提示
- ✅ 失败时有重试机制
- ✅ 图像与文本内容高度匹配
- ✅ 支持手动重新生成功能

---

## 🎯 立即开始实施！

**Cursor执行顺序**：
1. 先实施后端服务（illustration_service.py, models, routes）
2. 再实施前端组件（SmartImage.tsx, 更新StoryPageRenderer）
3. 最后进行集成测试和优化

这套方案将彻底解决图像占位符问题，实现真正的AI驱动儿童绘本体验！