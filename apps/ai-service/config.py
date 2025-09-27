import os
from typing import Dict, Any
from pydantic_settings import BaseSettings

class AIServiceConfig(BaseSettings):
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    qwen_api_key: str = os.getenv("QWEN_API_KEY", "")
    qwen_api_url: str = os.getenv("QWEN_API_URL", "https://dashscope.aliyuncs.com/api/v1")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Model Configuration
    psychology_model: str = "claude-3-sonnet-20240229"
    story_creation_model: str = "qwen-max"
    quality_control_model: str = "qwen-plus"

    # Token Limits
    max_framework_tokens: int = 2000
    max_story_tokens: int = 4000
    max_quality_tokens: int = 1500

    # Cache Configuration
    enable_framework_cache: bool = True
    cache_ttl_hours: int = 24

    # Cost Control
    max_daily_cost_usd: float = 100.0
    cost_alert_threshold: float = 80.0

    class Config:
        env_file = ".env"

config = AIServiceConfig()
