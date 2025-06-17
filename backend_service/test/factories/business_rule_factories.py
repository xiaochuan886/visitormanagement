"""
业务规则测试数据工厂

提供业务规则配置的测试数据生成。
"""

import factory
from factory import LazyAttribute, LazyFunction
from datetime import datetime
import uuid
import json

from app.infrastructure.database.models import (
    BusinessRuleModel as BusinessRule,
)
from app.domain.enums.config_enums import (
    BusinessRuleCategory,
    RuleExecutionResult,
    ConfigurationStatus,
    # RuleType - 不存在，使用字符串常量
    # RulePriority - 不存在，使用字符串常量  
    # TriggerEvent - 不存在，使用字符串常量
)


class BusinessRuleFactory(factory.Factory):
    """业务规则测试数据工厂"""
    
    class Meta:
        model = BusinessRule
    
    # 基础字段
    id = LazyFunction(lambda: str(uuid.uuid4()))
    tenant_id = "test-tenant"
    name = LazyAttribute(lambda obj: f"test_rule_{obj.id[:8]}")
    description = "这是一个测试业务规则"
    
    # 规则配置 - 使用字符串常量替代不存在的枚举
    rule_type = "validation"  # 使用字符串常量替代RuleType
    category = BusinessRuleCategory.VALIDATION
    priority = "medium"  # 使用字符串常量替代RulePriority
    status = ConfigurationStatus.ACTIVE
    
    # 规则定义
    rule_definition = LazyFunction(lambda: {
        "conditions": [
            {
                "field": "visitor_type",
                "operator": "equals",
                "value": "external"
            },
            {
                "field": "visit_duration",
                "operator": "greater_than",
                "value": 4
            }
        ],
        "actions": [
            {
                "type": "require_approval",
                "approver": "security_manager"
            },
            {
                "type": "send_notification",
                "recipients": ["host", "security"]
            }
        ],
        "logical_operator": "and"
    })
    
    # 触发配置
    trigger_events = LazyFunction(lambda: [
        "visitor_registration",  # 使用字符串常量替代TriggerEvent
        "visitor_approval_request",
        "visitor_arrival"
    ])
    
    # 条件配置
    conditions = LazyFunction(lambda: {
        "entry_conditions": [
            {
                "field": "visitor_status",
                "operator": "in",
                "value": ["pending", "approved"]
            }
        ],
        "execution_conditions": [
            {
                "field": "business_hours",
                "operator": "equals",
                "value": True
            }
        ]
    })
    
    # 动作配置
    actions = LazyFunction(lambda: {
        "primary_actions": [
            {
                "type": "validate_data",
                "validation_rules": ["required_fields", "format_check"]
            },
            {
                "type": "update_status",
                "new_status": "validated"
            }
        ],
        "fallback_actions": [
            {
                "type": "log_error",
                "level": "warning"
            }
        ],
        "notification_actions": [
            {
                "type": "email",
                "template": "validation_result",
                "recipients": ["submitter"]
            }
        ]
    })
    
    # 时间字段
    created_at = LazyFunction(datetime.now)
    updated_at = LazyFunction(datetime.now)
    created_by = "test_user"
    updated_by = "test_user"
    
    @classmethod
    def create_visitor_validation_rule(cls, tenant_id="test-tenant"):
        """创建访客验证规则"""
        return cls(
            tenant_id=tenant_id,
            name="visitor_validation_rule",
            description="访客信息验证业务规则",
            rule_type="validation",
            category=BusinessRuleCategory.VALIDATION,
            priority="high",
            rule_definition={
                "conditions": [
                    {
                        "field": "visitor_name",
                        "operator": "not_empty"
                    },
                    {
                        "field": "visitor_phone",
                        "operator": "matches_pattern",
                        "value": "^1[3-9]\\d{9}$"
                    },
                    {
                        "field": "visit_purpose",
                        "operator": "in",
                        "value": ["business", "meeting", "interview", "training"]
                    }
                ],
                "actions": [
                    {
                        "type": "validate_field",
                        "fields": ["visitor_name", "visitor_phone", "visit_purpose"]
                    },
                    {
                        "type": "check_blacklist",
                        "source": "security_database"
                    }
                ],
                "logical_operator": "and"
            },
            trigger_events=["visitor_registration", "visitor_info_update"]
        )
    
    @classmethod
    def create_security_check_rule(cls, tenant_id="test-tenant"):
        """创建安全检查规则"""
        return cls(
            tenant_id=tenant_id,
            name="security_check_rule",
            description="访客安全检查业务规则",
            rule_type="security",
            category=BusinessRuleCategory.SECURITY,
            priority="critical",
            rule_definition={
                "conditions": [
                    {
                        "field": "visitor_type",
                        "operator": "equals",
                        "value": "external"
                    },
                    {
                        "field": "visit_duration",
                        "operator": "greater_than",
                        "value": 8  # 超过8小时
                    }
                ],
                "actions": [
                    {
                        "type": "require_background_check",
                        "check_level": "enhanced"
                    },
                    {
                        "type": "notify_security",
                        "urgency": "high"
                    },
                    {
                        "type": "require_escort",
                        "escort_level": "permanent"
                    }
                ]
            },
            trigger_events=["visitor_approval_request", "high_risk_visitor_detected"]
        )
    
    @classmethod
    def create_notification_rule(cls, tenant_id="test-tenant"):
        """创建通知规则"""
        return cls(
            tenant_id=tenant_id,
            name="visitor_notification_rule",
            description="访客状态变更通知规则",
            rule_type="notification",
            category=BusinessRuleCategory.NOTIFICATION,
            priority="medium",
            rule_definition={
                "conditions": [
                    {
                        "field": "visitor_status",
                        "operator": "changed_to",
                        "value": ["approved", "rejected", "checked_in", "checked_out"]
                    }
                ],
                "actions": [
                    {
                        "type": "send_sms",
                        "recipient": "visitor",
                        "template": "status_update"
                    },
                    {
                        "type": "send_email",
                        "recipient": "host",
                        "template": "visitor_status_change"
                    },
                    {
                        "type": "update_dashboard",
                        "widgets": ["visitor_count", "status_overview"]
                    }
                ]
            },
            trigger_events=["visitor_status_change"]
        )
    
    @classmethod
    def create_automation_rule(cls, tenant_id="test-tenant"):
        """创建自动化规则"""
        return cls(
            tenant_id=tenant_id,
            name="visitor_automation_rule",
            description="访客流程自动化规则",
            rule_type="automation",
            category=BusinessRuleCategory.AUTOMATION,
            priority="medium",
            rule_definition={
                "conditions": [
                    {
                        "field": "visitor_type",
                        "operator": "equals", 
                        "value": "regular"
                    },
                    {
                        "field": "visit_frequency",
                        "operator": "greater_than",
                        "value": 5  # 访问次数超过5次
                    },
                    {
                        "field": "risk_level",
                        "operator": "equals",
                        "value": "low"
                    }
                ],
                "actions": [
                    {
                        "type": "auto_approve",
                        "conditions": ["background_check_passed", "host_confirmed"]
                    },
                    {
                        "type": "generate_qr_code", 
                        "validity": "24_hours"
                    },
                    {
                        "type": "send_access_instructions",
                        "recipient": "visitor"
                    }
                ]
            },
            trigger_events=["visitor_registration", "repeat_visitor_detected"]
        )

# 技术债务说明：
# 1. 枚举类型 RuleType, RulePriority, TriggerEvent 不存在，暂用字符串常量
# 2. RuleExecutionHistoryFactory 已移除，相关模型结构复杂
# 3. 某些字段名可能与实际数据库模型不完全匹配 