"""
通义千问图像生成服务
支持通义千问文生图和通义万相文生图模型
"""

import asyncio
import base64
import os
import logging
import aiohttp
import json
import time
from typing import Dict, Optional, Union
from PIL import Image
import io
import dashscope
from dashscope import ImageSynthesis

logger = logging.getLogger(__name__)

class QwenImageService:
    """通义千问图像生成服务"""

    def __init__(self, api_key: str, model: str = "qwen-image"):
        self.api_key = api_key
        self.model = model  # "qwen-image" 或 "wanxiang"

        # 设置DashScope API密钥 (多种方式确保生效)
        dashscope.api_key = api_key
        os.environ['DASHSCOPE_API_KEY'] = api_key

        # 模型配置
        self.model_configs = {
            "qwen-image": {
                "model": "qwen-vl-plus",  # 通义千问文生图
                "style": "watercolor",
                "size": "1024*1024"
            },
            "wanxiang": {
                "model": "wanx-v1",  # 通义万相
                "style": "cartoon",
                "size": "1024*1024"
            },
            "stable-diffusion": {
                "model": "stable-diffusion-v1-5",
                "style": "realistic",
                "size": "512*512"
            },
            "flux": {
                "model": "flux-1-dev",
                "style": "artistic",
                "size": "1024*1024"
            }
        }

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style: str = "cartoon",
        size: str = "1024*1024",
        seed: Optional[int] = None
    ) -> Dict:
        """
        使用通义千问生成图像

        Args:
            prompt: 图像描述提示词
            negative_prompt: 负面提示词
            style: 图像风格 (cartoon, watercolor, realistic等)
            size: 图像尺寸
            seed: 随机种子

        Returns:
            包含生成图像信息的字典
        """
        try:
            # 增强提示词，确保儿童友好
            enhanced_prompt = self._enhance_prompt_for_children(prompt)

            # 构建请求参数
            request_data = {
                "model": self.model_configs[self.model]["model"],
                "input": {
                    "prompt": enhanced_prompt,
                    "negative_prompt": negative_prompt or self._get_default_negative_prompt(),
                    "style": style,
                    "size": size,
                    "n": 1
                },
                "parameters": {
                    "style": style,
                    "size": size
                }
            }

            if seed is not None:
                request_data["parameters"]["seed"] = seed

            # 调用DashScope API生成图像
            result = await self._call_dashscope_api(enhanced_prompt, style, size)

            return self._process_response(result)

        except Exception as e:
            logger.error(f"Qwen image generation failed: {e}")
            raise Exception(f"Image generation failed: {str(e)}")

    async def _call_dashscope_api(self, prompt: str, style: str, size: str) -> Dict:
        """调用DashScope异步HTTP API"""
        try:
            # 步骤1: 创建任务获取任务ID
            task_id = await self._create_image_task(prompt, style, size)
            logger.info(f"Created Qwen image task: {task_id}")

            # 步骤2: 轮询任务状态直到完成
            result = await self._poll_task_result(task_id)
            return result

        except Exception as e:
            logger.error(f"DashScope API call failed: {e}")
            raise

    async def _create_image_task(self, prompt: str, style: str, size: str) -> str:
        """创建图像生成任务"""
        import aiohttp

        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }

        data = {
            "model": self.model_configs[self.model]["model"],
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "style": style,
                "size": size,
                "n": 1
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Task creation failed: {response.status} - {error_text}")

                result = await response.json()

                if "output" not in result or "task_id" not in result["output"]:
                    raise Exception(f"Invalid response format: {result}")

                return result["output"]["task_id"]

    async def _poll_task_result(self, task_id: str, max_attempts: int = 30) -> Dict:
        """轮询任务结果"""
        import aiohttp

        url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        async with aiohttp.ClientSession() as session:
            for attempt in range(max_attempts):
                await asyncio.sleep(2)  # 等待2秒

                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Task polling failed: {response.status} - {error_text}")

                    result = await response.json()

                    if "output" not in result:
                        raise Exception(f"Invalid response format: {result}")

                    task_status = result["output"].get("task_status", "UNKNOWN")

                    if task_status == "SUCCEEDED":
                        return result["output"]
                    elif task_status == "FAILED":
                        error_msg = result["output"].get("message", "Unknown error")
                        raise Exception(f"Task failed: {error_msg}")
                    elif task_status in ["PENDING", "RUNNING"]:
                        logger.info(f"Task {task_id} status: {task_status}, waiting...")
                        continue
                    else:
                        raise Exception(f"Unknown task status: {task_status}")

            raise Exception(f"Task {task_id} timed out after {max_attempts * 2} seconds")


    def _enhance_prompt_for_children(self, prompt: str) -> str:
        """增强提示词，确保生成儿童友好的内容"""

        # 儿童插图风格前缀
        style_prefix = (
            "儿童绘本插图，温馨友好的风格，"
            "柔和的色彩，卡通但精细，适合儿童，"
            "没有恐怖或暴力元素，天真快乐，"
        )

        # 质量和风格后缀
        style_suffix = (
            "，高质量数字艺术，清晰的线条，明亮的光照，"
            "适合3-11岁儿童，教育性和启发性"
        )

        # 组合提示词
        enhanced = f"{style_prefix}{prompt}{style_suffix}"

        # 确保长度不超过限制
        if len(enhanced) > 500:
            enhanced = enhanced[:496] + "..."

        return enhanced

    def _get_default_negative_prompt(self) -> str:
        """获取默认的负面提示词"""
        return (
            "暴力，恐怖，血腥，武器，打斗，死亡，"
            "不适合儿童，成人内容，恶心，"
            "violence, horror, blood, weapons, fighting, death, "
            "nsfw, adult content, disgusting, scary"
        )

    def _process_response(self, response: Dict) -> Dict:
        """处理DashScope异步API响应，提取图像数据"""
        try:
            # 异步API响应格式: {'results': [{'url': 'https://...'}]}
            results = response.get("results", [])
            if not results:
                raise Exception("No image generated")

            result = results[0]
            image_url = result.get("url")

            if not image_url:
                raise Exception("No image URL in response")

            # 获取图像基本信息
            return {
                "image_url": image_url,
                "format": "PNG",
                "width": 1024,  # 默认尺寸
                "height": 1024,
                "safety_info": self._extract_safety_info(response),
                "provider": "qwen",
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Response processing failed: {e}")
            raise Exception(f"Failed to process response: {str(e)}")

    def _extract_safety_info(self, response: Dict) -> Dict:
        """提取安全检查信息"""
        safety_info = {
            "blocked": False,
            "categories": [],
            "scores": {}
        }

        try:
            # 检查是否有安全相关的信息
            output = response.get("output", {})
            if "code" in output and output["code"] != "Success":
                safety_info["blocked"] = True
                safety_info["reason"] = output.get("message", "Unknown safety issue")

        except Exception as e:
            logger.warning(f"Failed to extract safety info: {e}")

        return safety_info

    async def check_safety(self, prompt: str) -> Dict:
        """检查提示词是否安全"""
        try:
            # 基本的关键词检查
            unsafe_keywords = [
                "暴力", "恐怖", "血腥", "武器", "打斗", "死亡", "杀害",
                "violence", "horror", "blood", "weapon", "fight", "death", "kill"
            ]

            prompt_lower = prompt.lower()
            detected_unsafe = []

            for kw in unsafe_keywords:
                # 检查关键词是否作为独立词出现
                if f" {kw} " in f" {prompt_lower} " or prompt_lower.startswith(f"{kw} ") or prompt_lower.endswith(f" {kw}"):
                    detected_unsafe.append(kw)

            return {
                "safe": len(detected_unsafe) == 0,
                "detected_unsafe_keywords": detected_unsafe,
                "recommendation": "儿童内容应避免暴力、恐怖等不当元素" if detected_unsafe else "内容安全"
            }

        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return {"safe": True, "error": str(e)}

    def get_supported_styles(self) -> list:
        """获取支持的风格"""
        return [
            "cartoon",      # 卡通
            "watercolor",   # 水彩
            "realistic",    # 写实
            "anime",        # 动漫
            "oil_painting", # 油画
            "sketch"        # 素描
        ]

    def get_supported_sizes(self) -> list:
        """获取支持的尺寸"""
        return ["512*512", "768*768", "1024*1024", "1024*768", "768*1024"]

    def get_model_info(self) -> Dict:
        """获取模型信息"""
        config = self.model_configs.get(self.model, {})
        return {
            "provider": "qwen",
            "model": self.model,
            "api_model": config.get("model", "unknown"),
            "max_prompt_length": 500,
            "supported_formats": ["PNG", "JPG"],
            "supported_styles": self.get_supported_styles(),
            "supported_sizes": self.get_supported_sizes(),
            "async_generation": True,
            "average_generation_time": "15-20 seconds"
        }