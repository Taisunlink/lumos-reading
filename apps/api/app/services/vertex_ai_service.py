"""
Google Vertex AI 图像生成服务
使用 Imagen 模型生成儿童友好的插图
"""

import asyncio
import base64
import os
import logging
from typing import Dict, Optional, Union
from google.cloud import aiplatform
from google.auth import default
import google.auth
from PIL import Image
import io

logger = logging.getLogger(__name__)

class VertexAIImageService:
    """Google Vertex AI Imagen 图像生成服务"""

    def __init__(self, project_id: str, location: str, credentials_path: str, model: str = "imagegeneration@006"):
        self.project_id = project_id
        self.location = location
        self.model = model
        self.credentials_path = credentials_path
        self._client = None

        # 设置认证
        self._setup_credentials()

    def _setup_credentials(self):
        """设置Google Cloud认证"""
        try:
            # 设置环境变量
            credentials_full_path = os.path.abspath(self.credentials_path)
            if os.path.exists(credentials_full_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_full_path
                logger.info(f"Using Google credentials: {credentials_full_path}")
            else:
                logger.warning(f"Credentials file not found: {credentials_full_path}")

            # 初始化Vertex AI
            aiplatform.init(project=self.project_id, location=self.location)

        except Exception as e:
            logger.error(f"Failed to setup Vertex AI credentials: {e}")
            raise

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        guidance_scale: float = 7.0,
        seed: Optional[int] = None
    ) -> Dict:
        """
        使用Vertex AI Imagen生成图像

        Args:
            prompt: 图像描述提示词
            negative_prompt: 负面提示词
            aspect_ratio: 宽高比 (1:1, 9:16, 16:9, 4:3, 3:4)
            guidance_scale: 引导尺度 (1.0-20.0)
            seed: 随机种子

        Returns:
            包含生成图像信息的字典
        """
        try:
            # 增强提示词，确保儿童友好
            enhanced_prompt = self._enhance_prompt_for_children(prompt)

            # 构建请求参数
            instances = [{
                "prompt": enhanced_prompt
            }]

            parameters = {
                "sampleCount": 1,
                "aspectRatio": aspect_ratio,
                "guidanceScale": guidance_scale,
                "includeRaiReason": True  # 包含安全检查信息
            }

            if negative_prompt:
                instances[0]["negativePrompt"] = negative_prompt

            if seed is not None:
                parameters["seed"] = seed

            # 调用Vertex AI API
            endpoint = aiplatform.Endpoint.list(
                filter=f'display_name="{self.model}"',
                location=self.location
            )

            if not endpoint:
                # 如果没有部署的端点，使用预测API
                response = await self._predict_with_model(instances, parameters)
            else:
                # 使用部署的端点
                response = await self._predict_with_endpoint(endpoint[0], instances, parameters)

            return self._process_response(response)

        except Exception as e:
            logger.error(f"Vertex AI image generation failed: {e}")
            raise Exception(f"Image generation failed: {str(e)}")

    def _enhance_prompt_for_children(self, prompt: str) -> str:
        """增强提示词，确保生成儿童友好的内容"""

        # 儿童插图风格前缀
        style_prefix = (
            "Children's book illustration, warm and friendly style, "
            "soft pastel colors, cartoon-like but detailed, safe for kids, "
            "no scary or violent elements, innocent and joyful, "
        )

        # 质量和风格后缀
        style_suffix = (
            ", high quality digital art, clean lines, bright lighting, "
            "suitable for ages 3-11, educational and inspiring"
        )

        # 组合提示词
        enhanced = f"{style_prefix}{prompt}{style_suffix}"

        # 确保长度不超过限制
        if len(enhanced) > 1024:
            enhanced = enhanced[:1020] + "..."

        return enhanced

    async def _predict_with_model(self, instances, parameters):
        """使用模型直接预测"""
        try:
            # 使用模型服务进行预测
            from google.cloud.aiplatform.gapic import PredictionServiceClient
            from google.cloud.aiplatform_v1 import PredictRequest

            client = PredictionServiceClient()

            # 构建端点路径
            endpoint_path = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model}"

            # 运行同步API在线程池中
            def _sync_predict():
                request = PredictRequest(
                    endpoint=endpoint_path,
                    instances=instances,
                    parameters=parameters
                )
                return client.predict(request=request)

            response = await asyncio.to_thread(_sync_predict)
            return response

        except Exception as e:
            logger.error(f"Model prediction failed: {e}")
            raise

    async def _predict_with_endpoint(self, endpoint, instances, parameters):
        """使用部署的端点进行预测"""
        try:
            def _sync_predict():
                return endpoint.predict(instances=instances, parameters=parameters)

            response = await asyncio.to_thread(_sync_predict)
            return response

        except Exception as e:
            logger.error(f"Endpoint prediction failed: {e}")
            raise

    def _process_response(self, response) -> Dict:
        """处理API响应，提取图像数据"""
        try:
            predictions = response.predictions

            if not predictions:
                raise Exception("No image generated")

            prediction = predictions[0]

            # 提取图像数据
            if "bytesBase64Encoded" in prediction:
                image_bytes = base64.b64decode(prediction["bytesBase64Encoded"])
            elif "generatedImage" in prediction:
                image_bytes = base64.b64decode(prediction["generatedImage"]["bytesBase64Encoded"])
            else:
                raise Exception("No image data in response")

            # 验证图像
            try:
                image = Image.open(io.BytesIO(image_bytes))
                width, height = image.size
            except Exception:
                raise Exception("Invalid image data received")

            # 检查安全性
            safety_info = self._extract_safety_info(prediction)

            return {
                "image_bytes": image_bytes,
                "format": "PNG",
                "width": width,
                "height": height,
                "safety_info": safety_info,
                "provider": "vertex-ai",
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Response processing failed: {e}")
            raise Exception(f"Failed to process response: {str(e)}")

    def _extract_safety_info(self, prediction) -> Dict:
        """提取安全检查信息"""
        safety_info = {
            "blocked": False,
            "categories": [],
            "scores": {}
        }

        try:
            if "raiFilteredReason" in prediction:
                safety_info["blocked"] = True
                safety_info["reason"] = prediction["raiFilteredReason"]

            if "safetyAttributes" in prediction:
                safety_attrs = prediction["safetyAttributes"]
                if "blocked" in safety_attrs:
                    safety_info["blocked"] = safety_attrs["blocked"]
                if "categories" in safety_attrs:
                    safety_info["categories"] = safety_attrs["categories"]
                if "scores" in safety_attrs:
                    safety_info["scores"] = safety_attrs["scores"]

        except Exception as e:
            logger.warning(f"Failed to extract safety info: {e}")

        return safety_info

    async def check_safety(self, prompt: str) -> Dict:
        """检查提示词是否安全"""
        try:
            # 更精确的关键词检查（放宽限制）
            unsafe_keywords = [
                "violence", "horror", "blood", "weapon", "fight", "death", "kill",
                "暴力", "恐怖", "血", "武器", "打架", "死亡", "杀"
            ]

            prompt_lower = prompt.lower()
            # 只检查完整单词匹配，避免误判
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

    def get_supported_aspect_ratios(self) -> list:
        """获取支持的宽高比"""
        return ["1:1", "9:16", "16:9", "4:3", "3:4"]

    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            "provider": "google-vertex-ai",
            "model": self.model,
            "project": self.project_id,
            "location": self.location,
            "max_prompt_length": 1024,
            "supported_formats": ["PNG"],
            "supported_aspect_ratios": self.get_supported_aspect_ratios()
        }