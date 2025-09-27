import asyncio
import json
from typing import Dict, Any, Optional
import httpx
import logging

logger = logging.getLogger(__name__)

class QwenClient:
    """通义千问API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.8,
        **kwargs
    ) -> Dict[str, Any]:
        """生成文本内容"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "output" in result and "text" in result["output"]:
                return {
                    "text": result["output"]["text"],
                    "usage": result.get("usage", {}),
                    "request_id": result.get("request_id", "")
                }
            else:
                raise Exception(f"Unexpected response format: {result}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Qwen API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Qwen API error: {str(e)}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        style: str = "realistic",
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """生成图像内容"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "wanx-v1",
            "input": {
                "prompt": prompt,
                "style": style,
                "size": size,
                "quality": quality
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/services/aigc/image-generation/generation",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "output" in result and "results" in result["output"]:
                return {
                    "images": result["output"]["results"],
                    "request_id": result.get("request_id", "")
                }
            else:
                raise Exception(f"Unexpected response format: {result}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Qwen Image API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Qwen Image API error: {str(e)}")
            raise
    
    async def close(self):
        """关闭客户端连接"""
        await self.client.aclose()
