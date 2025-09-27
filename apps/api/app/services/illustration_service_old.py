import asyncio
import aiohttp
import aiofiles
import os
import uuid
import hashlib
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.illustration import Illustration, IllustrationStatus, IllustrationStyle
from app.models.story import Story
from app.core.config import settings

logger = logging.getLogger(__name__)

class IllustrationService:
    """插图生成服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"
        self.cache_dir = "illustrations_cache"
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    async def generate_illustration(
        self,
        story_id: str,
        page_number: int,
        prompt: str,
        style: IllustrationStyle = IllustrationStyle.WATERCOLOR,
        character_bible: Optional[Dict] = None,
        negative_prompt: Optional[str] = None
    ) -> Illustration:
        """生成单张插图"""
        
        # 检查是否已存在
        existing = self.db.query(Illustration).filter(
            and_(
                Illustration.story_id == story_id,
                Illustration.page_number == page_number
            )
        ).first()
        
        if existing and existing.status == IllustrationStatus.COMPLETED:
            logger.info(f"Illustration already exists for story {story_id}, page {page_number}")
            return existing
        
        # 创建插图记录
        illustration = Illustration(
            story_id=story_id,
            page_number=page_number,
            prompt=prompt,
            negative_prompt=negative_prompt,
            style=style,
            status=IllustrationStatus.PENDING,
            generation_metadata={},
            character_consistency_data=character_bible or {}
        )
        
        self.db.add(illustration)
        self.db.commit()
        self.db.refresh(illustration)
        
        try:
            # 更新状态为生成中
            illustration.status = IllustrationStatus.GENERATING
            self.db.commit()
            
            # 生成图片
            image_url, local_path = await self._call_dalle_api(
                prompt, style, character_bible, negative_prompt
            )
            
            # 更新结果
            illustration.image_url = image_url
            illustration.local_path = local_path
            illustration.status = IllustrationStatus.COMPLETED
            illustration.generated_at = datetime.now()
            
            # 质量评估
            quality_scores = await self._assess_illustration_quality(
                image_url, prompt, character_bible
            )
            illustration.quality_score = quality_scores.get('quality', 0.8)
            illustration.safety_score = quality_scores.get('safety', 0.9)
            illustration.appropriateness_score = quality_scores.get('appropriateness', 0.85)
            
            self.db.commit()
            logger.info(f"Illustration generated successfully for story {story_id}, page {page_number}")
            
        except Exception as e:
            logger.error(f"Failed to generate illustration: {str(e)}")
            illustration.status = IllustrationStatus.FAILED
            illustration.generation_metadata = {"error": str(e)}
            self.db.commit()
            raise
        
        return illustration
    
    async def _call_dalle_api(
        self,
        prompt: str,
        style: IllustrationStyle,
        character_bible: Optional[Dict],
        negative_prompt: Optional[str]
    ) -> Tuple[str, str]:
        """调用DALL-E API生成图片"""
        
        # 构建增强的提示词
        enhanced_prompt = self._build_enhanced_prompt(prompt, style, character_bible)
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": enhanced_prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard",
            "style": "vivid"
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/images/generations",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DALL-E API error: {response.status} - {error_text}")
                
                result = await response.json()
                image_url = result["data"][0]["url"]
                
                # 下载并保存到本地
                local_path = await self._download_and_save_image(image_url)
                
                return image_url, local_path
    
    def _build_enhanced_prompt(
        self,
        prompt: str,
        style: IllustrationStyle,
        character_bible: Optional[Dict]
    ) -> str:
        """构建增强的提示词"""
        
        # 基础风格描述
        style_descriptions = {
            IllustrationStyle.WATERCOLOR: "watercolor painting, soft colors, gentle brushstrokes",
            IllustrationStyle.DIGITAL_ART: "digital art, clean lines, vibrant colors",
            IllustrationStyle.CARTOON: "cartoon style, cute and friendly, bright colors",
            IllustrationStyle.REALISTIC: "realistic illustration, detailed, lifelike",
            IllustrationStyle.SKETCH: "pencil sketch, line art, monochrome"
        }
        
        enhanced_prompt = f"{prompt}, {style_descriptions[style]}"
        
        # 添加角色一致性信息
        if character_bible:
            character_info = character_bible.get('characters', [])
            if character_info:
                character_descriptions = []
                for char in character_info:
                    if 'visual_description' in char:
                        character_descriptions.append(char['visual_description'])
                
                if character_descriptions:
                    enhanced_prompt += f", consistent character design: {', '.join(character_descriptions)}"
        
        # 添加儿童友好的描述
        enhanced_prompt += ", child-friendly, safe for children, educational illustration"
        
        return enhanced_prompt
    
    async def _download_and_save_image(self, image_url: str) -> str:
        """下载并保存图片到本地"""
        
        # 生成文件名
        file_hash = hashlib.md5(image_url.encode()).hexdigest()
        filename = f"{file_hash}.png"
        local_path = os.path.join(self.cache_dir, filename)
        
        # 如果文件已存在，直接返回路径
        if os.path.exists(local_path):
            return local_path
        
        # 下载图片
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    async with aiofiles.open(local_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    return local_path
                else:
                    raise Exception(f"Failed to download image: {response.status}")
    
    async def _assess_illustration_quality(
        self,
        image_url: str,
        prompt: str,
        character_bible: Optional[Dict]
    ) -> Dict[str, float]:
        """评估插图质量"""
        
        # 这里可以实现更复杂的质量评估逻辑
        # 目前返回默认值
        return {
            'quality': 0.8,
            'safety': 0.9,
            'appropriateness': 0.85
        }
    
    def get_illustration(self, illustration_id: str) -> Optional[Illustration]:
        """获取插图"""
        return self.db.query(Illustration).filter(Illustration.id == illustration_id).first()
    
    def get_story_illustrations(self, story_id: str) -> List[Illustration]:
        """获取故事的所有插图"""
        return self.db.query(Illustration).filter(
            Illustration.story_id == story_id
        ).order_by(Illustration.page_number).all()
    
    def delete_illustration(self, illustration_id: str) -> bool:
        """删除插图"""
        illustration = self.get_illustration(illustration_id)
        if illustration:
            # 删除本地文件
            if illustration.local_path and os.path.exists(illustration.local_path):
                os.remove(illustration.local_path)
            
            self.db.delete(illustration)
            self.db.commit()
            return True
        return False


class BatchIllustrationService:
    """批量插图生成服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.illustration_service = IllustrationService(db)
    
    async def generate_story_illustrations(
        self,
        story_id: str,
        pages: List[Dict],
        character_bible: Optional[Dict] = None,
        style: IllustrationStyle = IllustrationStyle.WATERCOLOR
    ) -> List[Illustration]:
        """为整个故事生成所有插图"""
        
        illustrations = []
        
        # 并发生成所有插图
        tasks = []
        for page in pages:
            task = self.illustration_service.generate_illustration(
                story_id=story_id,
                page_number=page['page_number'],
                prompt=page['illustration_prompt'],
                style=style,
                character_bible=character_bible
            )
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate illustration for page {i+1}: {str(result)}")
            else:
                illustrations.append(result)
        
        return illustrations
    
    async def generate_illustrations_with_fallback(
        self,
        story_id: str,
        pages: List[Dict],
        character_bible: Optional[Dict] = None,
        style: IllustrationStyle = IllustrationStyle.WATERCOLOR
    ) -> List[Illustration]:
        """带降级处理的批量插图生成"""
        
        illustrations = []
        
        for page in pages:
            try:
                illustration = await self.illustration_service.generate_illustration(
                    story_id=story_id,
                    page_number=page['page_number'],
                    prompt=page['illustration_prompt'],
                    style=style,
                    character_bible=character_bible
                )
                illustrations.append(illustration)
                
            except Exception as e:
                logger.warning(f"Failed to generate illustration for page {page['page_number']}: {str(e)}")
                
                # 创建失败的插图记录
                failed_illustration = Illustration(
                    story_id=story_id,
                    page_number=page['page_number'],
                    prompt=page['illustration_prompt'],
                    style=style,
                    status=IllustrationStatus.FAILED,
                    generation_metadata={"error": str(e)},
                    character_consistency_data=character_bible or {}
                )
                
                self.db.add(failed_illustration)
                self.db.commit()
                illustrations.append(failed_illustration)
        
        return illustrations
