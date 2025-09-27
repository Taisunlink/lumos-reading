"""
多AI提供商图像生成服务
支持 OpenAI DALL-E 和 Google Vertex AI Imagen
"""

import asyncio
import aiohttp
import aiofiles
import os
import uuid
import hashlib
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

# 导入AI服务
from app.services.vertex_ai_service import VertexAIImageService
from app.services.qwen_image_service import QwenImageService
from app.models.illustration import Illustration, IllustrationStatus, IllustrationStyle
from app.models.story import Story
from app.core.config import settings

logger = logging.getLogger(__name__)

class MultiAIIllustrationService:
    """多AI提供商插图生成服务"""

    def __init__(self, db: Session):
        self.db = db
        self.provider = settings.image_provider  # "vertex" or "openai"
        self.cache_dir = "/tmp/claude/illustrations"
        self.ensure_cache_dir()

        # 初始化AI服务
        self._init_ai_services()

    def _init_ai_services(self):
        """初始化AI服务"""
        try:
            # 通义千问 (主要服务)
            if self.provider == "qwen":
                if not settings.qwen_api_key:
                    logger.warning("Qwen API key not configured, will use fallback")
                    return
                self.qwen_service = QwenImageService(
                    api_key=settings.qwen_api_key,
                    model=settings.qwen_model
                )
                logger.info("Qwen service initialized")

            # Google Vertex AI
            elif self.provider == "vertex":
                self.vertex_service = VertexAIImageService(
                    project_id=settings.google_project_id,
                    location=settings.google_location,
                    credentials_path=settings.google_credentials_path,
                    model=settings.vertex_model
                )
                logger.info("Vertex AI service initialized")

            # OpenAI (作为备用)
            self.openai_api_key = settings.openai_api_key

        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            self.vertex_service = None
            self.qwen_service = None

    def ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    async def generate_story_illustration(
        self,
        story_id: str,
        page_number: int,
        illustration_prompt: str,
        character_bible: Optional[Dict] = None
    ) -> Dict:
        """为故事页面生成插图 - 主要API接口"""

        try:
            # 1. 检查缓存
            cache_key = self._generate_cache_key(illustration_prompt, character_bible)
            cached_result = await self._get_cached_illustration(cache_key)
            if cached_result:
                logger.info(f"Using cached illustration for story {story_id}, page {page_number}")
                return cached_result

            # 2. 增强提示词
            enhanced_prompt = await self._enhance_prompt_with_characters(
                illustration_prompt, character_bible
            )

            # 3. 安全检查
            safety_check = await self._check_prompt_safety(enhanced_prompt)
            if not safety_check["safe"]:
                logger.warning(f"Unsafe prompt detected: {safety_check}")
                return await self._get_fallback_image("unsafe_content")

            # 4. 生成图像
            generation_result = await self._generate_with_provider(enhanced_prompt)

            # 5. 存储图像
            stored_url = await self._store_image(generation_result["image_bytes"], cache_key)

            # 6. 保存到数据库
            illustration_record = await self._save_illustration_record(
                story_id=story_id,
                page_number=page_number,
                image_url=stored_url,
                prompt=enhanced_prompt,
                provider=generation_result["provider"],
                model=generation_result.get("model", "unknown"),
                safety_info=generation_result.get("safety_info", {}),
                cache_key=cache_key
            )

            return {
                "url": stored_url,
                "cached": False,
                "provider": generation_result["provider"],
                "safety_info": generation_result.get("safety_info", {}),
                "illustration_id": str(illustration_record.id)
            }

        except Exception as e:
            logger.error(f"Illustration generation failed for story {story_id}, page {page_number}: {e}")
            # 返回降级图像
            return await self._get_fallback_image("generation_failed")

    async def _generate_with_provider(self, prompt: str) -> Dict:
        """使用指定的AI提供商生成图像"""

        if self.provider == "qwen" and hasattr(self, 'qwen_service') and self.qwen_service:
            return await self._generate_with_qwen(prompt)
        elif self.provider == "vertex" and hasattr(self, 'vertex_service') and self.vertex_service:
            return await self._generate_with_vertex(prompt)
        elif self.provider == "openai" and self.openai_api_key:
            return await self._generate_with_openai(prompt)
        else:
            # 尝试降级到其他提供商
            if hasattr(self, 'qwen_service') and self.qwen_service and self.provider != "qwen":
                logger.info("Falling back to Qwen")
                return await self._generate_with_qwen(prompt)
            elif hasattr(self, 'vertex_service') and self.vertex_service and self.provider != "vertex":
                logger.info("Falling back to Vertex AI")
                return await self._generate_with_vertex(prompt)
            elif self.openai_api_key and self.provider != "openai":
                logger.info("Falling back to OpenAI")
                return await self._generate_with_openai(prompt)
            else:
                raise Exception("No AI providers available")

    async def _generate_with_vertex(self, prompt: str) -> Dict:
        """使用Google Vertex AI生成图像"""
        try:
            result = await self.vertex_service.generate_image(
                prompt=prompt,
                aspect_ratio="1:1",  # 适合儿童绘本
                guidance_scale=7.0,  # 平衡创意和准确性
                negative_prompt="scary, violent, dark, inappropriate for children"
            )

            return {
                "image_bytes": result["image_bytes"],
                "provider": "vertex-ai",
                "model": result["model"],
                "safety_info": result.get("safety_info", {}),
                "width": result.get("width", 1024),
                "height": result.get("height", 1024)
            }

        except Exception as e:
            logger.error(f"Vertex AI generation failed: {e}")
            raise

    async def _generate_with_qwen(self, prompt: str) -> Dict:
        """使用通义千问生成图像"""
        try:
            result = await self.qwen_service.generate_image(
                prompt=prompt,
                style=settings.qwen_style,  # cartoon, watercolor, realistic等
                size=settings.qwen_size,   # 1024*1024
                negative_prompt="暴力，恐怖，血腥，不适合儿童，成人内容"
            )

            # 如果返回的是URL，需要下载图像
            if "image_url" in result:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(result["image_url"]) as response:
                        if response.status == 200:
                            image_bytes = await response.read()
                            return {
                                "image_bytes": image_bytes,
                                "provider": "qwen",
                                "model": result.get("model", settings.qwen_model),
                                "safety_info": result.get("safety_info", {}),
                                "format": result.get("format", "PNG"),
                                "width": result.get("width", 1024),
                                "height": result.get("height", 1024)
                            }
                        else:
                            raise Exception(f"Failed to download image from {result['image_url']}")
            else:
                # 直接返回图像字节数据
                return {
                    "image_bytes": result["image_bytes"],
                    "provider": "qwen",
                    "model": result.get("model", settings.qwen_model),
                    "safety_info": result.get("safety_info", {}),
                    "format": result.get("format", "PNG"),
                    "width": result.get("width", 1024),
                    "height": result.get("height", 1024)
                }

        except Exception as e:
            logger.error(f"Qwen generation failed: {e}")
            raise

    async def _generate_with_openai(self, prompt: str) -> Dict:
        """使用OpenAI DALL-E生成图像"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": settings.openai_model,
                "prompt": prompt,
                "n": 1,
                "size": settings.openai_image_size,
                "quality": settings.openai_image_quality,
                "response_format": "url"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")

                    result = await response.json()
                    image_url = result["data"][0]["url"]

                    # 下载图像
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            image_bytes = await img_response.read()

                            return {
                                "image_bytes": image_bytes,
                                "provider": "openai",
                                "model": settings.openai_model,
                                "safety_info": {"safe": True, "provider_filtered": False},
                                "width": 1024,
                                "height": 1024
                            }
                        else:
                            raise Exception(f"Failed to download image from OpenAI: {img_response.status}")

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def _enhance_prompt_with_characters(
        self,
        base_prompt: str,
        character_bible: Optional[Dict]
    ) -> str:
        """使用角色圣经增强提示词"""

        # 基础儿童插图风格
        base_style = (
            "Children's book illustration, warm and friendly, "
            "soft pastel colors, cartoon-like but detailed, safe for ages 3-11, "
            "high quality digital art, innocent and joyful, "
        )

        enhanced = f"{base_style}{base_prompt}"

        # 添加角色描述
        if character_bible and character_bible.get("characters"):
            char_descriptions = []
            for char in character_bible["characters"]:
                if char.get("visual_description"):
                    char_desc = (
                        f"{char['name']}: {char['visual_description']}, "
                        f"personality: {char.get('personality', 'friendly')}"
                    )
                    char_descriptions.append(char_desc)

            if char_descriptions:
                enhanced += f". Characters: {'; '.join(char_descriptions)}"

        # 确保儿童友好
        enhanced += ". Bright, colorful, educational, no scary elements"

        # 长度限制
        if len(enhanced) > 1024:
            enhanced = enhanced[:1020] + "..."

        return enhanced

    async def _check_prompt_safety(self, prompt: str) -> Dict:
        """检查提示词安全性"""

        if self.provider == "vertex" and self.vertex_service:
            return await self.vertex_service.check_safety(prompt)
        else:
            # 更精确的关键词检查（放宽限制）
            unsafe_keywords = [
                "violence", "horror", "blood", "weapon", "fight", "death", "kill",
                "暴力", "恐怖", "血", "武器", "打架", "死亡", "杀", "害怕"
            ]

            prompt_lower = prompt.lower()
            # 只检查完整单词匹配，避免误判
            detected = []
            for kw in unsafe_keywords:
                # 检查关键词是否作为独立词出现
                if f" {kw} " in f" {prompt_lower} " or prompt_lower.startswith(f"{kw} ") or prompt_lower.endswith(f" {kw}"):
                    detected.append(kw)

            return {
                "safe": len(detected) == 0,
                "detected_unsafe_keywords": detected
            }

    async def _store_image(self, image_bytes: bytes, cache_key: str) -> str:
        """存储图像到本地存储"""
        try:
            filename = f"{cache_key}.png"
            file_path = os.path.join(self.cache_dir, filename)

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(image_bytes)

            # 返回访问URL（生产环境应使用CDN）
            return f"/api/static/illustrations/{filename}"

        except Exception as e:
            logger.error(f"Failed to store image: {e}")
            raise

    async def _save_illustration_record(
        self,
        story_id: str,
        page_number: int,
        image_url: str,
        prompt: str,
        provider: str,
        model: str,
        safety_info: Dict,
        cache_key: str
    ) -> Illustration:
        """保存插图记录到数据库"""

        try:
            illustration = Illustration(
                id=uuid.uuid4(),
                story_id=uuid.UUID(story_id),
                page_number=page_number,
                image_url=image_url,
                generation_prompt=prompt,
                provider=provider,
                model_name=model,
                status=IllustrationStatus.COMPLETED,
                style=IllustrationStyle.DIGITAL,
                cache_key=cache_key,
                safety_info=safety_info,
                created_at=datetime.now()
            )

            self.db.add(illustration)
            self.db.commit()
            self.db.refresh(illustration)

            return illustration

        except Exception as e:
            logger.error(f"Failed to save illustration record: {e}")
            self.db.rollback()
            raise

    def _generate_cache_key(self, prompt: str, character_bible: Optional[Dict] = None) -> str:
        """生成缓存键"""
        cache_data = {
            "prompt": prompt,
            "characters": character_bible.get("characters", []) if character_bible else [],
            "provider": self.provider
        }

        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    async def _get_cached_illustration(self, cache_key: str) -> Optional[Dict]:
        """检查缓存中的插图"""
        try:
            # 检查数据库缓存
            cached = self.db.query(Illustration).filter(
                Illustration.cache_key == cache_key,
                Illustration.status == IllustrationStatus.COMPLETED
            ).first()

            if cached:
                # 检查文件是否存在
                file_path = os.path.join(self.cache_dir, f"{cache_key}.png")
                if os.path.exists(file_path):
                    return {
                        "url": cached.image_url,
                        "cached": True,
                        "provider": cached.provider,
                        "illustration_id": str(cached.id)
                    }

            return None

        except Exception as e:
            logger.error(f"Cache check failed: {e}")
            return None

    async def _get_fallback_image(self, reason: str) -> Dict:
        """获取降级图像"""

        # 创建简单的占位符
        fallback_filename = f"fallback_{reason}.png"
        fallback_path = os.path.join(self.cache_dir, fallback_filename)

        # 如果占位符不存在，创建一个
        if not os.path.exists(fallback_path):
            await self._create_fallback_image(fallback_path, reason)

        return {
            "url": f"/api/static/illustrations/{fallback_filename}",
            "cached": False,
            "fallback": True,
            "reason": reason,
            "provider": "fallback"
        }

    async def _create_fallback_image(self, file_path: str, reason: str):
        """创建降级占位符图像"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # 创建1024x1024的图像
            img = Image.new('RGB', (1024, 1024), color='#f0f8ff')
            draw = ImageDraw.Draw(img)

            # 绘制简单的插图占位符
            draw.rectangle([100, 100, 924, 924], outline='#ddd', width=4)

            # 添加文字
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            except:
                font = ImageFont.load_default()

            text = "故事插图"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (1024 - text_width) // 2
            y = (1024 - text_height) // 2

            draw.text((x, y), text, fill='#888', font=font)

            # 保存图像
            img.save(file_path, 'PNG')

        except Exception as e:
            logger.error(f"Failed to create fallback image: {e}")
            # 如果创建失败，使用空文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(b'')

    async def get_illustration_by_story_page(self, story_id: str, page_number: int) -> Optional[Illustration]:
        """根据故事ID和页码获取插图"""
        return self.db.query(Illustration).filter(
            and_(
                Illustration.story_id == story_id,
                Illustration.page_number == page_number,
                Illustration.status == IllustrationStatus.COMPLETED
            )
        ).first()

    async def get_story_illustrations(self, story_id: str) -> List[Illustration]:
        """获取故事的所有插图"""
        return self.db.query(Illustration).filter(
            Illustration.story_id == story_id,
            Illustration.status == IllustrationStatus.COMPLETED
        ).order_by(Illustration.page_number).all()

    # API兼容性方法
    async def generate_illustration(
        self,
        story_id: str,
        page_number: int,
        prompt: str,
        style: IllustrationStyle = IllustrationStyle.DIGITAL,
        character_bible: Optional[Dict] = None,
        negative_prompt: Optional[str] = None
    ) -> Illustration:
        """生成单张插图 - API兼容性包装器"""
        # 调用新的生成方法
        result = await self.generate_story_illustration(
            story_id=story_id,
            page_number=page_number,
            illustration_prompt=prompt,
            character_bible=character_bible
        )

        # 如果生成失败，返回fallback记录
        if result.get("fallback"):
            # 创建fallback记录
            illustration = Illustration(
                id=uuid.uuid4(),
                story_id=uuid.UUID(story_id),
                page_number=page_number,
                image_url=result["url"],
                generation_prompt=prompt,
                provider="fallback",
                model_name="fallback",
                status=IllustrationStatus.FAILED,
                style=style,
                created_at=datetime.now()
            )

            self.db.add(illustration)
            self.db.commit()
            self.db.refresh(illustration)
            return illustration

        # 返回生成成功的记录
        if result.get("illustration_id"):
            illustration = self.db.query(Illustration).filter(
                Illustration.id == result["illustration_id"]
            ).first()
            if illustration:
                return illustration

        # 如果找不到记录，抛出异常
        raise Exception("Failed to create illustration record")

    def get_illustration(self, illustration_id: str) -> Optional[Illustration]:
        """获取单张插图"""
        return self.db.query(Illustration).filter(
            Illustration.id == illustration_id
        ).first()

    def delete_illustration(self, illustration_id: str) -> bool:
        """删除插图"""
        illustration = self.get_illustration(illustration_id)
        if illustration:
            self.db.delete(illustration)
            self.db.commit()
            return True
        return False

# 批量生成服务
class BatchIllustrationService:
    """批量插图生成服务 - 用于故事完整生成"""

    def __init__(self, db: Session):
        self.illustration_service = MultiAIIllustrationService(db)

    async def generate_all_story_illustrations(
        self,
        story_id: str,
        progress_callback: Optional[callable] = None
    ) -> List[Dict]:
        """为整个故事生成所有插图"""

        try:
            # 获取故事信息
            story = self.illustration_service.db.query(Story).filter(Story.id == story_id).first()
            if not story:
                raise ValueError(f"Story {story_id} not found")

            pages = story.content.get("pages", [])
            character_bible = {"characters": story.content.get("characters", [])}

            results = []
            total_pages = len(pages)

            for i, page in enumerate(pages):
                if "illustration_prompt" in page:
                    try:
                        illustration = await self.illustration_service.generate_story_illustration(
                            story_id=story_id,
                            page_number=page["page_number"],
                            illustration_prompt=page["illustration_prompt"],
                            character_bible=character_bible
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

                    except Exception as e:
                        logger.error(f"Failed to generate illustration for page {page['page_number']}: {e}")
                        # 继续处理其他页面
                        results.append({
                            "page_number": page["page_number"],
                            "error": str(e)
                        })

            return results

        except Exception as e:
            logger.error(f"Batch illustration generation failed for story {story_id}: {e}")
            raise

# 保持向后兼容的别名
IllustrationService = MultiAIIllustrationService