#!/usr/bin/env python3
"""
简化的配置引擎工厂测试

验证配置引擎核心功能的数据创建和处理能力。
"""

import uuid
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


# 简化的配置数据类
@dataclass
class FormConfiguration:
    """表单配置"""
    id: str
    tenant_id: str
    name: str
    title: str
    description: str
    status: str
    version: str
    form_schema: Dict[str, Any]
    ui_schema: Dict[str, Any]
    form_settings: Dict[str, Any]
    permissions: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


@dataclass
class WorkflowConfiguration:
    """工作流配置"""
    id: str
    tenant_id: str
    name: str
    title: str
    description: str
    status: str
    version: str
    workflow_schema: Dict[str, Any]
    workflow_settings: Dict[str, Any]
    permissions: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


@dataclass
class SpatialHierarchy:
    """空间层级结构"""
    id: str
    tenant_id: str
    hierarchy_name: str
    hierarchy_code: str
    description: str
    max_levels: int
    is_active: bool
    level_config: Dict[str, Any]
    hierarchy_rules: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


@dataclass
class BusinessRule:
    """业务规则"""
    id: str
    tenant_id: str
    rule_name: str
    rule_code: str
    description: str
    rule_type: str
    status: str
    priority: int
    rule_definition: Dict[str, Any]
    execution_config: Dict[str, Any]
    permissions: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


class ConfigEngineFactory:
    """配置引擎工厂"""
    
    @staticmethod
    def create_visitor_registration_form(tenant_id: str = "test-tenant") -> FormConfiguration:
        """创建访客登记表单"""
        return FormConfiguration(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name="visitor_registration",
            title="访客登记表单",
            description="访客登记专用表单",
            status="active",
            version="1.0.0",
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
                    "visit_purpose": {
                        "type": "string",
                        "title": "来访目的",
                        "enum": ["商务洽谈", "技术交流", "培训学习", "参观考察", "其他"]
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
                "visit_purpose": {
                    "ui:widget": "select"
                }
            },
            form_settings={
                "enable_draft": True,
                "enable_validation": True,
                "auto_save": False,
                "max_file_size": "10MB"
            },
            permissions={
                "create": ["admin", "user"],
                "read": ["admin", "user", "guest"],
                "update": ["admin"],
                "delete": ["admin"]
            },
            metadata={
                "category": "visitor_management",
                "tags": ["visitor", "registration"],
                "creator": "system",
                "business_unit": "security"
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            updated_by="system"
        )
    
    @staticmethod
    def create_visitor_approval_workflow(tenant_id: str = "test-tenant") -> WorkflowConfiguration:
        """创建访客审批工作流"""
        return WorkflowConfiguration(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name="visitor_approval",
            title="访客审批工作流",
            description="访客预约申请审批流程",
            status="active",
            version="1.0.0",
            workflow_schema={
                "start_step": "submit_application",
                "end_steps": ["approved", "rejected"],
                "parallel_execution": False,
                "timeout_minutes": 120,
                "steps": [
                    {
                        "id": "submit_application",
                        "name": "提交申请",
                        "type": "start",
                        "next": ["security_review"]
                    },
                    {
                        "id": "security_review",
                        "name": "安全审核",
                        "type": "approval",
                        "assignee": "security_officer",
                        "timeout_minutes": 30,
                        "next": ["manager_approval", "rejected"]
                    },
                    {
                        "id": "manager_approval",
                        "name": "主管审批",
                        "type": "approval",
                        "assignee": "department_manager",
                        "timeout_minutes": 60,
                        "next": ["approved", "rejected"]
                    },
                    {
                        "id": "approved",
                        "name": "审批通过",
                        "type": "end"
                    },
                    {
                        "id": "rejected",
                        "name": "审批拒绝",
                        "type": "end"
                    }
                ]
            },
            workflow_settings={
                "enable_rollback": True,
                "auto_assign": True,
                "notification_enabled": True,
                "deadline_tracking": True,
                "require_comments": True
            },
            permissions={
                "start": ["admin", "user"],
                "view": ["admin", "user", "guest"],
                "modify": ["admin"],
                "cancel": ["admin", "creator"]
            },
            metadata={
                "category": "approval",
                "business_process": "visitor_management",
                "sla_hours": 2,
                "priority": "high",
                "departments": ["security", "hr", "reception"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            updated_by="system"
        )
    
    @staticmethod
    def create_office_hierarchy(tenant_id: str = "test-tenant") -> SpatialHierarchy:
        """创建办公场所层级结构"""
        return SpatialHierarchy(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            hierarchy_name="office_space_hierarchy",
            hierarchy_code="OFFICE_HIER",
            description="办公场所空间层级结构",
            max_levels=4,
            is_active=True,
            level_config={
                "levels": [
                    {
                        "level": 1,
                        "name": "园区",
                        "code": "campus",
                        "required": True,
                        "attributes": ["address", "contact_person", "security_level"]
                    },
                    {
                        "level": 2,
                        "name": "建筑",
                        "code": "building",
                        "required": True,
                        "attributes": ["building_type", "floor_count", "elevator_count"]
                    },
                    {
                        "level": 3,
                        "name": "楼层",
                        "code": "floor",
                        "required": True,
                        "attributes": ["floor_number", "area_sqm", "capacity"]
                    },
                    {
                        "level": 4,
                        "name": "办公室",
                        "code": "office",
                        "required": False,
                        "attributes": ["office_type", "seat_count", "department"]
                    }
                ]
            },
            hierarchy_rules={
                "naming_rules": {
                    "allow_duplicates": False,
                    "case_sensitive": False,
                    "max_length": 50,
                    "min_length": 2
                },
                "path_separator": "/",
                "enable_auto_coding": True,
                "code_format": "{level_code}{sequence:03d}",
                "access_control": {
                    "require_authorization": True,
                    "inheritance_enabled": True
                }
            },
            metadata={
                "category": "office",
                "business_unit": "facilities",
                "purpose": "space_management",
                "tags": ["office", "hierarchy"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            updated_by="system"
        )
    
    @staticmethod
    def create_visitor_validation_rule(tenant_id: str = "test-tenant") -> BusinessRule:
        """创建访客验证规则"""
        return BusinessRule(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            rule_name="visitor_phone_validation",
            rule_code="VISITOR_PHONE_VAL",
            description="访客手机号码格式验证规则",
            rule_type="validation",
            status="active",
            priority=200,
            rule_definition={
                "conditions": [
                    {
                        "field": "visitor_phone",
                        "operator": "matches_pattern",
                        "value": "^1[3-9]\\d{9}$",
                        "message": "手机号码格式不正确"
                    },
                    {
                        "field": "visitor_phone",
                        "operator": "not_empty",
                        "value": None,
                        "message": "手机号码不能为空"
                    }
                ],
                "actions": [
                    {
                        "type": "validation_error",
                        "message": "访客手机号码验证失败",
                        "field": "visitor_phone"
                    }
                ],
                "logical_operator": "and"
            },
            execution_config={
                "trigger_events": ["form_submit", "field_change"],
                "execution_order": 1,
                "timeout_seconds": 5,
                "immediate_execution": True
            },
            permissions={
                "manage": ["admin"],
                "view": ["admin", "user"],
                "execute": ["system", "admin", "user"]
            },
            metadata={
                "category": "validation",
                "business_domain": "visitor_management",
                "tags": ["validation", "phone"],
                "author": "system"
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            updated_by="system"
        )


def test_configuration_engine():
    """测试配置引擎功能"""
    
    print("🧪 测试配置引擎数据工厂...")
    
    # 测试表单配置
    print("\n📝 测试表单配置...")
    form = ConfigEngineFactory.create_visitor_registration_form()
    print(f"✅ 表单ID: {form.id[:8]}...")
    print(f"✅ 表单名称: {form.name}")
    print(f"✅ 表单标题: {form.title}")
    print(f"✅ 字段数量: {len(form.form_schema['properties'])}")
    print(f"✅ 必填字段: {form.form_schema['required']}")
    
    # 验证表单schema结构
    assert form.form_schema["type"] == "object"
    assert "visitor_name" in form.form_schema["properties"]
    assert "visitor_phone" in form.form_schema["properties"]
    assert "visit_purpose" in form.form_schema["properties"]
    assert len(form.form_schema["required"]) == 3
    
    print("\n🎉 配置引擎功能测试全部通过！")
    print(f"  ✅ 表单配置: {form.name} - 包含{len(form.form_schema['properties'])}个字段")
    
    return {"form_configuration": form}


if __name__ == "__main__":
    try:
        results = test_configuration_engine()
        print("\n✨ 配置引擎数据工厂验证成功！表单配置功能正常。")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        exit(1) 