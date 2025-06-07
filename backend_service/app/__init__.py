"""
访客管理系统应用包
"""

__version__ = "1.0.0"
__author__ = "Visitor Management Team"

# 导入Celery应用实例，确保可以被发现
from app.core.celery import celery_app

__all__ = ["celery_app"] 