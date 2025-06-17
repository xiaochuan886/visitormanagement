"""
工作流配置测试数据工厂

提供工作流配置相关的测试数据生成。
"""

import factory
from factory import LazyAttribute, LazyFunction, Sequence
from datetime import datetime
import uuid
import json

from app.infrastructure.database.models import (
    WorkflowConfigurationModel as WorkflowConfiguration,
)
from app.domain.enums.config_enums import (
    WorkflowType,
    WorkflowStatus,
    StepType,
    ApprovalType,
    ConfigurationStatus,
    # TransitionType - 不存在，使用字符串常量
    # NotificationMethod - 不存在，使用字符串常量
)


class WorkflowConfigurationFactory(factory.Factory):
    """工作流配置测试数据工厂"""
    
    class Meta:
        model = WorkflowConfiguration
    
    # 基础字段
    id = LazyFunction(lambda: str(uuid.uuid4()))
    tenant_id = "test-tenant"
    name = LazyAttribute(lambda obj: f"test_workflow_{obj.id[:8]}")
    workflow_name = LazyAttribute(lambda obj: f"测试工作流_{obj.id[:8]}")  # 使用正确的字段名
    description = "这是一个测试工作流配置"
    
    # 工作流类型和状态
    workflow_type = WorkflowType.VISITOR_APPROVAL
    status = ConfigurationStatus.ACTIVE
    version = "1.0.0"
    
    # 工作流配置
    workflow_definition = LazyFunction(lambda: {
        "steps": [
            {
                "id": "start",
                "name": "开始",
                "type": "automatic",  # 使用字符串常量替代StepType
                "actions": ["initialize_data"],
                "next": "approval"
            },
            {
                "id": "approval", 
                "name": "审批步骤",
                "type": "approval",  # 使用字符串常量
                "approver_type": "single_approver",  # 使用字符串常量替代ApprovalType
                "approvers": ["manager"],
                "timeout": 24,  # 24小时
                "next": "notification"
            },
            {
                "id": "notification",
                "name": "通知步骤", 
                "type": "notification",  # 使用字符串常量
                "notification_type": "email",  # 使用字符串常量替代NotificationMethod
                "recipients": ["applicant", "manager"],
                "next": "end"
            },
            {
                "id": "end",
                "name": "结束",
                "type": "automatic",  # 使用字符串常量
                "actions": ["update_status"]
            }
        ],
        "variables": {
            "timeout_hours": 24,
            "auto_approve_threshold": 1000
        }
    })
    
    # 审批配置
    approver_config = LazyFunction(lambda: {
        "default_approvers": ["manager", "admin"],
        "approval_rules": [
            {
                "condition": "amount > 1000",
                "approvers": ["director", "finance"]
            },
            {
                "condition": "department == 'IT'", 
                "approvers": ["it_manager"]
            }
        ],
        "escalation": {
            "enabled": True,
            "timeout_hours": 24,
            "escalate_to": ["director"]
        }
    })
    
    # 条件配置
    conditions = LazyFunction(lambda: {
        "trigger_conditions": [
            {
                "field": "visit_type",
                "operator": "equals",
                "value": "business"
            },
            {
                "field": "duration",
                "operator": "greater_than",
                "value": 4
            }
        ],
        "approval_conditions": [
            {
                "field": "risk_level",
                "operator": "less_than_or_equal",
                "value": "medium"
            }
        ]
    })
    
    # 时间字段
    created_at = LazyFunction(datetime.now)
    updated_at = LazyFunction(datetime.now)
    created_by = "test_user"
    updated_by = "test_user"
    
    @classmethod
    def create_visitor_approval_workflow(cls, tenant_id="test-tenant"):
        """创建访客审批工作流"""
        return cls(
            tenant_id=tenant_id,
            name="visitor_approval_workflow",
            workflow_name="访客审批工作流",
            description="用于访客申请的审批流程",
            workflow_type=WorkflowType.VISITOR_APPROVAL,
            workflow_definition={
                "steps": [
                    {
                        "id": "submit",
                        "name": "提交申请",
                        "type": "manual",
                        "required_fields": ["visitor_name", "visit_purpose", "visit_date"],
                        "next": "initial_review"
                    },
                    {
                        "id": "initial_review",
                        "name": "初步审核",
                        "type": "automatic",
                        "actions": ["validate_visitor_info", "check_blacklist"],
                        "conditions": [
                            {
                                "if": "blacklist_check == 'failed'",
                                "then": "reject",
                                "else": "manager_approval"
                            }
                        ]
                    },
                    {
                        "id": "manager_approval", 
                        "name": "主管审批",
                        "type": "approval",
                        "approver_type": "department_head",
                        "timeout": 8,  # 8小时
                        "actions": {
                            "approve": "security_check",
                            "reject": "reject_notification",
                            "timeout": "escalate_approval"
                        }
                    },
                    {
                        "id": "security_check",
                        "name": "安全检查",
                        "type": "automatic", 
                        "actions": ["background_check", "security_assessment"],
                        "next": "final_approval"
                    },
                    {
                        "id": "final_approval",
                        "name": "最终批准",
                        "type": "notification",
                        "notification_type": "multi_channel",  # 使用字符串常量
                        "recipients": ["visitor", "host", "security"],
                        "actions": ["generate_access_code", "create_visitor_badge"]
                    }
                ]
            }
        )
    
    @classmethod
    def create_device_control_workflow(cls, tenant_id="test-tenant"):
        """创建设备控制工作流"""
        return cls(
            tenant_id=tenant_id,
            name="device_control_workflow",
            workflow_name="设备控制工作流", 
            description="用于控制门禁、摄像头等设备",
            workflow_type=WorkflowType.DEVICE_CONTROL,
            workflow_definition={
                "steps": [
                    {
                        "id": "trigger",
                        "name": "触发事件",
                        "type": "automatic",
                        "trigger_events": ["visitor_approved", "visitor_arrived"],
                        "next": "device_action"
                    },
                    {
                        "id": "device_action",
                        "name": "设备操作",
                        "type": "automatic",
                        "actions": [
                            "unlock_entrance_door",
                            "activate_camera_recording", 
                            "update_access_log"
                        ],
                        "devices": ["entrance_gate", "lobby_camera", "access_control_system"],
                        "next": "monitor"
                    },
                    {
                        "id": "monitor",
                        "name": "状态监控",
                        "type": "automatic",
                        "monitor_duration": 30,  # 30秒
                        "actions": ["check_device_status", "log_visitor_entry"],
                        "next": "complete"
                    }
                ]
            }
        )

# 技术债务说明：
# 1. 字段名 'name' vs 'workflow_name' 需要根据实际数据库模型调整
# 2. 枚举类型 TransitionType, NotificationMethod 不存在，暂用字符串常量
# 3. WorkflowStepFactory, WorkflowTransitionFactory 已移除，模型关系复杂 