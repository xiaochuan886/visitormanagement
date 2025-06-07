"""
Celery应用配置模块
集成访客管理系统的异步任务处理
"""
import os
from celery import Celery
from kombu import Queue
from .config import get_settings

# 获取配置实例
settings = get_settings()

# 创建Celery应用实例
celery_app = Celery(
    "visitor_management",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.application.tasks.email_tasks",
        "app.application.tasks.report_tasks",
    ]
)

# Celery配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # 任务路由配置
    task_routes={
        "app.application.tasks.email_tasks.*": {"queue": "email"},
        "app.application.tasks.report_tasks.*": {"queue": "reports"},
    },
    
    # 队列配置
    task_default_queue="default",
    task_queues=(
        Queue("default"),
        Queue("email"),
        Queue("reports"),
    ),
    
    # 任务执行配置
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # 重试配置
    task_default_retry_delay=60,  # 60秒后重试
    task_max_retries=3,
    
    # 结果过期时间
    result_expires=3600,  # 1小时
    
    # 任务时间限制
    task_soft_time_limit=300,  # 5分钟软限制
    task_time_limit=600,       # 10分钟硬限制
    
    # 监控配置
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# 从环境变量更新配置（Docker环境）
if os.getenv("CELERY_BROKER_URL"):
    celery_app.conf.broker_url = os.getenv("CELERY_BROKER_URL")
if os.getenv("CELERY_RESULT_BACKEND"):
    celery_app.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

# 任务发现
celery_app.autodiscover_tasks([
    "app.application.tasks"
])

@celery_app.task(bind=True, name="debug_task")
def debug_task(self):
    """调试任务，用于测试Celery配置"""
    print(f"Request: {self.request!r}")
    return "Celery is working!"

# 导出Celery应用实例
__all__ = ["celery_app"] 