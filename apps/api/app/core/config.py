"""
应用配置管理
基于Pydantic Settings的配置系统
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    app_name: str = "LumosReading API"
    version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # 安全配置
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 数据库配置
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # AI服务配置
    ai_service_url: str = Field(default="http://localhost:8001", env="AI_SERVICE_URL")
    ai_service_timeout: int = Field(default=300, env="AI_SERVICE_TIMEOUT")
    
    # 文件存储配置
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(default=["image/jpeg", "image/png", "image/gif"], env="ALLOWED_FILE_TYPES")
    
    # CORS配置
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    
    # 允许的主机
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "*.lumosreading.com"],
        env="ALLOWED_HOSTS"
    )
    
    # 限流配置
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # 秒
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # 监控配置
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # 微信支付配置
    wechat_app_id: Optional[str] = Field(default=None, env="WECHAT_APP_ID")
    wechat_mch_id: Optional[str] = Field(default=None, env="WECHAT_MCH_ID")
    wechat_api_key: Optional[str] = Field(default=None, env="WECHAT_API_KEY")
    wechat_cert_path: Optional[str] = Field(default=None, env="WECHAT_CERT_PATH")
    
    # 阿里云OSS配置
    oss_access_key_id: Optional[str] = Field(default=None, env="OSS_ACCESS_KEY_ID")
    oss_access_key_secret: Optional[str] = Field(default=None, env="OSS_ACCESS_KEY_SECRET")
    oss_endpoint: Optional[str] = Field(default=None, env="OSS_ENDPOINT")
    oss_bucket_name: Optional[str] = Field(default=None, env="OSS_BUCKET_NAME")

    # AI图像生成配置
    image_provider: str = Field(default="qwen", env="IMAGE_PROVIDER")  # qwen, vertex, openai

    # OpenAI配置 (用于图像生成)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="dall-e-3", env="OPENAI_MODEL")
    openai_image_size: str = Field(default="1024x1024", env="OPENAI_IMAGE_SIZE")
    openai_image_quality: str = Field(default="standard", env="OPENAI_IMAGE_QUALITY")

    # Google Vertex AI配置
    google_project_id: str = Field(default="tokyo-silicon-473221", env="GOOGLE_PROJECT_ID")
    google_location: str = Field(default="us-central1", env="GOOGLE_LOCATION")
    google_credentials_path: str = Field(default="tokyo-silicon-473221-k1-53da36c03c3b.json", env="GOOGLE_CREDENTIALS_PATH")
    vertex_model: str = Field(default="imagegeneration@006", env="VERTEX_MODEL")

    # 通义千问配置 (主要图像生成服务)
    qwen_api_key: Optional[str] = Field(default=None, env="QWEN_API_KEY")
    qwen_model: str = Field(default="qwen-image", env="QWEN_MODEL")  # qwen-image, wanxiang, stable-diffusion, flux
    qwen_style: str = Field(default="cartoon", env="QWEN_STYLE")  # cartoon, watercolor, realistic, anime
    qwen_size: str = Field(default="1024*1024", env="QWEN_SIZE")
    qwen_timeout: int = Field(default=60, env="QWEN_TIMEOUT")  # API超时时间(秒)

    # 插图存储配置
    illustration_storage_type: str = Field(default="local", env="ILLUSTRATION_STORAGE_TYPE")
    illustration_cache_ttl: int = Field(default=3600, env="ILLUSTRATION_CACHE_TTL")
    static_files_url: str = Field(default="http://localhost:8000/api/static", env="STATIC_FILES_URL")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("allowed_file_types", pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 创建全局配置实例
settings = Settings()
