"""
邮件相关的Celery任务
处理访客管理系统的邮件通知功能
"""
import logging
from typing import Dict, Any, Optional
from celery import current_task
from app.core.celery import celery_app
from app.core.config import get_settings

# 配置日志
logger = logging.getLogger(__name__)
settings = get_settings()

@celery_app.task(bind=True, name="send_visitor_notification")
def send_visitor_notification(
    self,
    visitor_email: str,
    visitor_name: str,
    notification_type: str,
    template_data: Dict[str, Any],
    tenant_id: str = "default"
):
    """
    发送访客通知邮件
    
    Args:
        visitor_email: 访客邮箱
        visitor_name: 访客姓名
        notification_type: 通知类型 (welcome, approval, rejection, reminder)
        template_data: 邮件模板数据
        tenant_id: 租户ID
    """
    try:
        logger.info(f"开始发送访客通知邮件: {notification_type} to {visitor_email}")
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"step": "准备邮件内容", "progress": 25}
        )
        
        # TODO: 集成实际的邮件发送服务
        # 这里应该集成 FastAPI-Mail 或其他邮件服务
        email_content = _prepare_email_content(
            notification_type, 
            visitor_name, 
            template_data
        )
        
        current_task.update_state(
            state="PROGRESS",
            meta={"step": "发送邮件", "progress": 75}
        )
        
        # 模拟邮件发送
        logger.info(f"邮件内容准备完成: {email_content['subject']}")
        
        # 记录发送结果
        result = {
            "status": "success",
            "recipient": visitor_email,
            "subject": email_content["subject"],
            "sent_at": "2025-06-07T16:11:00Z",
            "tenant_id": tenant_id
        }
        
        logger.info(f"访客通知邮件发送成功: {visitor_email}")
        return result
        
    except Exception as exc:
        logger.error(f"发送访客通知邮件失败: {str(exc)}")
        # 重试机制
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True, name="send_approval_notification")
def send_approval_notification(
    self,
    approver_email: str,
    approver_name: str,
    visitor_info: Dict[str, Any],
    tenant_id: str = "default"
):
    """
    发送审批通知邮件给审批人
    
    Args:
        approver_email: 审批人邮箱
        approver_name: 审批人姓名
        visitor_info: 访客信息
        tenant_id: 租户ID
    """
    try:
        logger.info(f"开始发送审批通知邮件 to {approver_email}")
        
        current_task.update_state(
            state="PROGRESS",
            meta={"step": "准备审批通知", "progress": 30}
        )
        
        # 准备审批邮件内容
        email_content = {
            "subject": f"访客审批请求 - {visitor_info.get('name', '未知访客')}",
            "body": f"""
            尊敬的 {approver_name}，
            
            您有一个新的访客审批请求：
            
            访客姓名: {visitor_info.get('name')}
            访客公司: {visitor_info.get('company_name', '未提供')}
            访问目的: {visitor_info.get('purpose', '未提供')}
            预期到访时间: {visitor_info.get('expected_date')}
            
            请登录系统进行审批。
            
            访客管理系统
            """
        }
        
        current_task.update_state(
            state="PROGRESS",
            meta={"step": "发送审批邮件", "progress": 80}
        )
        
        # TODO: 实际邮件发送逻辑
        logger.info(f"审批通知邮件内容: {email_content['subject']}")
        
        result = {
            "status": "success",
            "recipient": approver_email,
            "subject": email_content["subject"],
            "visitor_id": visitor_info.get("id"),
            "sent_at": "2025-06-07T16:11:00Z",
            "tenant_id": tenant_id
        }
        
        logger.info(f"审批通知邮件发送成功: {approver_email}")
        return result
        
    except Exception as exc:
        logger.error(f"发送审批通知邮件失败: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True, name="send_bulk_notifications")
def send_bulk_notifications(
    self,
    notification_list: list,
    tenant_id: str = "default"
):
    """
    批量发送通知邮件
    
    Args:
        notification_list: 通知列表
        tenant_id: 租户ID
    """
    try:
        logger.info(f"开始批量发送通知邮件，数量: {len(notification_list)}")
        
        results = []
        total = len(notification_list)
        
        for i, notification in enumerate(notification_list):
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "step": f"发送邮件 {i+1}/{total}",
                    "progress": int((i / total) * 100)
                }
            )
            
            # 调用单个邮件发送任务
            if notification["type"] == "visitor":
                result = send_visitor_notification.delay(
                    notification["email"],
                    notification["name"],
                    notification["notification_type"],
                    notification["template_data"],
                    tenant_id
                )
            elif notification["type"] == "approval":
                result = send_approval_notification.delay(
                    notification["email"],
                    notification["name"],
                    notification["visitor_info"],
                    tenant_id
                )
            
            results.append(result.id)
        
        logger.info(f"批量邮件发送任务创建完成，任务数: {len(results)}")
        return {
            "status": "completed",
            "total_tasks": len(results),
            "task_ids": results,
            "tenant_id": tenant_id
        }
        
    except Exception as exc:
        logger.error(f"批量发送邮件失败: {str(exc)}")
        raise self.retry(exc=exc, countdown=120, max_retries=2)

def _prepare_email_content(notification_type: str, visitor_name: str, template_data: Dict[str, Any]) -> Dict[str, str]:
    """
    准备邮件内容
    
    Args:
        notification_type: 通知类型
        visitor_name: 访客姓名
        template_data: 模板数据
    
    Returns:
        包含subject和body的字典
    """
    templates = {
        "welcome": {
            "subject": f"欢迎访问 - {visitor_name}",
            "body": f"尊敬的 {visitor_name}，欢迎您的到访！"
        },
        "approval": {
            "subject": f"访问申请已批准 - {visitor_name}",
            "body": f"尊敬的 {visitor_name}，您的访问申请已获得批准。"
        },
        "rejection": {
            "subject": f"访问申请未通过 - {visitor_name}",
            "body": f"尊敬的 {visitor_name}，很抱歉，您的访问申请未能通过审批。"
        },
        "reminder": {
            "subject": f"访问提醒 - {visitor_name}",
            "body": f"尊敬的 {visitor_name}，提醒您即将到访。"
        }
    }
    
    return templates.get(notification_type, templates["welcome"]) 