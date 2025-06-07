"""
核心配置模块
使用Pydantic Settings进行类型安全的配置管理
"""
from typing import Optional, List
from pydantic import validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "访客管理系统"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/visitormanagement"
    database_echo: bool = False
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS配置
    allowed_hosts: List[str] = ["*"]
    allowed_origins: List[str] = ["*"]
    
    # 邮件配置
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    
    # 文件存储配置
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "pdf"]
    
    # Celery配置
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    # Celery任务配置
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: List[str] = ["json"]
    celery_timezone: str = "UTC"
    celery_enable_utc: bool = True
    
    # 多租户配置
    default_tenant_id: str = "default"
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """验证数据库URL格式"""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("数据库URL必须是PostgreSQL格式")
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False,
        "extra": "allow"  # 允许额外字段
    }


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings() 