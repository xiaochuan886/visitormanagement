"""
Celery任务模块包
包含访客管理系统的所有异步任务
"""

# 导入所有任务模块，确保Celery能够发现任务
from . import email_tasks
from . import report_tasks

__all__ = [
    "email_tasks",
    "report_tasks",
] 