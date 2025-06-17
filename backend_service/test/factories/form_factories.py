"""
表单配置测试数据工厂

提供表单配置、字段配置的测试数据生成。
"""

import factory
from factory import LazyAttribute, SubFactory, LazyFunction
from datetime import datetime
import uuid
import json

from app.infrastructure.database.models import (
    FormConfigurationModel as FormConfiguration,
    FormFieldConfigurationModel as FormFieldConfiguration
)
from app.domain.enums.config_enums import (
    ConfigurationStatus,
    FieldType,
    FormType
)


class FormConfigurationFactory(factory.Factory):
    """表单配置测试数据工厂"""
    
    class Meta:
        model = FormConfiguration
    
    # 基础字段
    id = LazyFunction(lambda: str(uuid.uuid4()))
    tenant_id = "test-tenant"
    name = LazyAttribute(lambda obj: f"测试表单_{obj.id[:8]}")
    title = LazyAttribute(lambda obj: f"测试表单标题_{obj.id[:8]}")
    description = "这是一个测试表单配置"
    
    # 状态和配置 - 使用字符串常量替代不存在的枚举
    status = "active"  # 使用字符串常量替代FormStatus.ACTIVE
    version = "1.0.0"
    is_system_form = False
    
    # JSON 配置字段
    form_schema = LazyFunction(lambda: {
        "type": "object",
        "properties": {
            "test_field": {
                "type": "string",
                "title": "测试字段"
            }
        },
        "required": ["test_field"]
    })
    
    ui_schema = LazyFunction(lambda: {
        "test_field": {
            "ui:widget": "text",
            "ui:placeholder": "请输入测试内容"
        }
    })
    
    form_settings = LazyFunction(lambda: {
        "enable_draft": True,
        "enable_validation": True,
        "auto_save": False,
        "max_file_size": "10MB"
    })
    
    # 权限配置
    permissions = LazyFunction(lambda: {
        "create": ["admin", "user"],
        "read": ["admin", "user", "guest"],
        "update": ["admin"],
        "delete": ["admin"]
    })
    
    # 元数据
    metadata = LazyFunction(lambda: {
        "category": "test",
        "tags": ["testing", "form"],
        "creator": "test_user",
        "business_unit": "IT"
    })
    
    # 时间字段
    created_at = LazyFunction(datetime.now)
    updated_at = LazyFunction(datetime.now)
    created_by = "test_user"
    updated_by = "test_user"
    
    @classmethod
    def create_visitor_registration_form(cls, tenant_id="test-tenant"):
        """创建访客登记表单"""
        return cls(
            tenant_id=tenant_id,
            name="visitor_registration",
            title="访客登记表单",
            description="访客登记专用表单",
            form_schema={
                "type": "object",
                "properties": {
                    "visitor_name": {
                        "type": "string",
                        "title": "访客姓名",
                        "minLength": 2,
                        "maxLength": 50
                    },
                    "visitor_phone": {
                        "type": "string",
                        "title": "联系电话",
                        "pattern": "^1[3-9]\\d{9}$"
                    },
                    "id_card": {
                        "type": "string", 
                        "title": "身份证号",
                        "pattern": "^[1-9]\\d{5}(18|19|20)\\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\\d{3}[0-9Xx]$"
                    },
                    "visit_purpose": {
                        "type": "string",
                        "title": "来访目的",
                        "enum": ["商务洽谈", "技术交流", "培训学习", "参观考察", "其他"]
                    },
                    "expected_duration": {
                        "type": "integer",
                        "title": "预计停留时长(小时)",
                        "minimum": 1,
                        "maximum": 8
                    },
                    "emergency_contact": {
                        "type": "string",
                        "title": "紧急联系人",
                        "maxLength": 50
                    }
                },
                "required": ["visitor_name", "visitor_phone", "visit_purpose"]
            },
            ui_schema={
                "visitor_name": {
                    "ui:widget": "text",
                    "ui:placeholder": "请输入访客真实姓名"
                },
                "visitor_phone": {
                    "ui:widget": "tel",
                    "ui:placeholder": "请输入11位手机号码"
                },
                "id_card": {
                    "ui:widget": "text",
                    "ui:placeholder": "请输入18位身份证号"
                },
                "visit_purpose": {
                    "ui:widget": "select"
                },
                "expected_duration": {
                    "ui:widget": "updown"
                },
                "emergency_contact": {
                    "ui:widget": "text",
                    "ui:placeholder": "紧急联系人姓名"
                }
            }
        )


class FormFieldConfigurationFactory(factory.Factory):
    """表单字段配置测试数据工厂"""
    
    class Meta:
        model = FormFieldConfiguration
    
    # 基础字段
    id = LazyFunction(lambda: str(uuid.uuid4()))
    tenant_id = "test-tenant"
    form_id = SubFactory(FormConfigurationFactory)
    field_key = LazyAttribute(lambda obj: f"test_field_{obj.id[:8]}")
    field_label = LazyAttribute(lambda obj: f"测试字段_{obj.id[:8]}")
    field_type = FieldType.TEXT
    
    # 字段配置
    is_required = False
    is_readonly = False
    is_hidden = False
    display_order = LazyAttribute(lambda obj: hash(obj.id) % 100)
    
    # JSON 配置
    field_config = LazyFunction(lambda: {
        "placeholder": "请输入内容",
        "maxLength": 100,
        "minLength": 0
    })
    
    validation_rules = LazyFunction(lambda: {
        "required": False,
        "pattern": None,
        "min": None,
        "max": None
    })
    
    # 时间字段
    created_at = LazyFunction(datetime.now)
    updated_at = LazyFunction(datetime.now)
    created_by = "test_user"
    updated_by = "test_user"
    
    @classmethod
    def create_name_field(cls, form_id, tenant_id="test-tenant"):
        """创建姓名字段"""
        return cls(
            tenant_id=tenant_id,
            form_id=form_id,
            field_key="visitor_name",
            field_label="访客姓名",
            field_type=FieldType.TEXT,
            is_required=True,
            field_config={
                "placeholder": "请输入访客真实姓名",
                "maxLength": 50,
                "minLength": 2
            },
            validation_rules={
                "required": True,
                "pattern": "^[\\u4e00-\\u9fa5a-zA-Z\\s]{2,50}$"
            }
        )
    
    @classmethod
    def create_phone_field(cls, form_id, tenant_id="test-tenant"):
        """创建电话字段"""
        return cls(
            tenant_id=tenant_id,
            form_id=form_id,
            field_key="visitor_phone",
            field_label="联系电话",
            field_type=FieldType.TEXT,
            is_required=True,
            field_config={
                "placeholder": "请输入11位手机号码",
                "maxLength": 11,
                "minLength": 11
            },
            validation_rules={
                "required": True,
                "pattern": "^1[3-9]\\d{9}$"
            }
        )
    
    @classmethod
    def create_email_field(cls, form_id, tenant_id="test-tenant"):
        """创建邮箱字段"""
        return cls(
            tenant_id=tenant_id,
            form_id=form_id,
            field_key="visitor_email",
            field_label="邮箱地址",
            field_type=FieldType.EMAIL,
            is_required=False,
            field_config={
                "placeholder": "请输入邮箱地址"
            },
            validation_rules={
                "required": False,
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            }
        )

# 注释：FormValidationRuleFactory已移除，因为FormValidationRule模型在当前数据库中不存在
# 如需验证规则功能，可以使用FormFieldConfiguration中的validation_rules字段 