# 配置引擎开发指南

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **适用角色**: 业务配置人员、高级开发者

## 🎯 配置引擎概述

配置引擎是访客管理系统的核心创新功能，提供通用化的动态配置管理能力，支持运行时配置变更，无需重启系统。

### 核心模块
- ✅ **表单配置**: 动态表单结构定义，支持15种字段类型
- ✅ **工作流配置**: 多步骤流程定义，支持条件分支
- ✅ **空间配置**: 无限层级空间管理，支持动态层级
- ✅ **业务规则**: 复杂条件表达式，支持优先级管理

## 🔧 表单配置引擎

### 支持的字段类型
```
基础字段：text, textarea, number, email, phone, url, password
日期时间：date, datetime, time
选择字段：select, multiselect, radio, checkbox
文件字段：file, image
```

### 表单配置示例
```json
{
  "form_name": "访客登记表单",
  "form_type": "visitor_registration",
  "description": "标准访客登记表单",
  "form_fields": [
    {
      "field_key": "visitor_name",
      "field_label": "访客姓名",
      "field_type": "text",
      "field_order": 1,
      "is_required": true,
      "validation_rules": {
        "min_length": 2,
        "max_length": 50
      }
    },
    {
      "field_key": "phone_number",
      "field_label": "联系电话",
      "field_type": "phone",
      "field_order": 2,
      "is_required": true,
      "validation_rules": {
        "pattern": "^1[3-9]\\d{9}$"
      }
    },
    {
      "field_key": "visit_purpose",
      "field_label": "访问目的",
      "field_type": "select",
      "field_order": 3,
      "is_required": true,
      "field_options": {
        "options": [
          {"value": "business_meeting", "label": "商务会议"},
          {"value": "interview", "label": "面试"},
          {"value": "site_visit", "label": "参观访问"}
        ]
      }
    }
  ]
}
```

## 🔄 工作流配置引擎

### 工作流步骤定义
```json
{
  "workflow_name": "访客审批流程",
  "workflow_type": "visitor_approval",
  "workflow_steps": [
    {
      "step_id": "initial_review",
      "step_name": "初审",
      "step_type": "manual",
      "assignee_type": "role",
      "assignee_value": "receptionist",
      "timeout_hours": 24,
      "next_steps": {
        "approved": "manager_review",
        "rejected": "end"
      }
    },
    {
      "step_id": "manager_review",
      "step_name": "经理审批",
      "step_type": "manual",
      "assignee_type": "department_manager",
      "timeout_hours": 48,
      "next_steps": {
        "approved": "end",
        "rejected": "end"
      }
    }
  ],
  "trigger_conditions": {
    "entity_type": "visitor",
    "event": "created",
    "conditions": [
      {
        "field": "purpose",
        "operator": "in",
        "value": ["business_meeting", "interview"]
      }
    ]
  }
}
```

## 🏢 空间配置引擎

### 空间层级定义
```json
{
  "spatial_name": "总部空间配置",
  "description": "北京总部空间层级管理",
  "level_definitions": [
    {
      "level": 1,
      "level_name": "站点",
      "level_code": "site",
      "properties": ["name", "address", "contact"]
    },
    {
      "level": 2,
      "level_name": "建筑",
      "level_code": "building",
      "properties": ["name", "floors", "elevator"]
    },
    {
      "level": 3,
      "level_name": "楼层",
      "level_code": "floor",
      "properties": ["floor_number", "area", "capacity"]
    },
    {
      "level": 4,
      "level_name": "区域",
      "level_code": "zone",
      "properties": ["zone_type", "access_level"]
    },
    {
      "level": 5,
      "level_name": "房间",
      "level_code": "room",
      "properties": ["room_number", "capacity", "equipment"]
    }
  ]
}
```

## 📋 业务规则引擎

### 规则条件表达式
```json
{
  "rule_name": "工作时间访客提醒",
  "rule_category": "notification",
  "description": "工作时间外的访客申请发送提醒",
  "conditions": {
    "operator": "AND",
    "rules": [
      {
        "field": "expected_date",
        "operator": "time_outside",
        "value": "09:00-18:00"
      },
      {
        "field": "purpose",
        "operator": "equals",
        "value": "business_meeting"
      }
    ]
  },
  "actions": [
    {
      "action_type": "send_notification",
      "target": "manager",
      "template": "overtime_visitor_notification",
      "parameters": {
        "message": "有访客申请在非工作时间访问"
      }
    }
  ],
  "priority": 100
}
```

## 🚀 配置引擎API使用

### 创建表单配置
```javascript
const formConfig = {
  form_name: "员工入职表单",
  form_type: "employee_registration",
  form_fields: [
    {
      field_key: "employee_name",
      field_label: "员工姓名",
      field_type: "text",
      is_required: true
    }
  ]
}

const response = await fetch('/api/v1/config/forms/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(formConfig)
})
```

### 获取表单配置
```javascript
const response = await fetch('/api/v1/config/forms/?form_type=visitor_registration')
const formConfigs = await response.json()
```

## 🔍 配置验证

### 表单字段验证规则
```json
{
  "validation_rules": {
    "required": true,
    "min_length": 2,
    "max_length": 100,
    "pattern": "^[\\u4e00-\\u9fa5a-zA-Z\\s]+$",
    "custom_validator": "name_validator"
  }
}
```

### 条件逻辑配置
```json
{
  "conditional_logic": {
    "show_if": {
      "field": "visitor_type",
      "operator": "equals",
      "value": "external"
    },
    "required_if": {
      "field": "purpose",
      "operator": "equals",
      "value": "business_meeting"
    }
  }
}
```

## 📊 配置管理最佳实践

### 1. 版本控制
- 每个配置修改自动增加版本号
- 支持配置回滚到历史版本
- 保留配置变更历史记录

### 2. 测试策略
- 配置发布前进行验证测试
- 支持配置的A/B测试
- 监控配置变更对系统的影响

### 3. 权限管理
- 配置修改需要相应权限
- 重要配置需要审批流程
- 配置变更日志完整记录

## 🛠️ 故障排除

### 常见问题
**Q**: 表单字段不显示？
**A**: 检查字段的`is_visible`属性和条件逻辑配置

**Q**: 工作流不执行？
**A**: 验证触发条件是否正确匹配业务数据

**Q**: 业务规则不生效？
**A**: 检查规则的`is_active`状态和优先级设置

---

## 📞 技术支持

### 配置引擎支持
- **负责人**: 配置管理团队
- **更新频率**: 随系统功能更新
- **问题反馈**: 通过配置管理平台提交

### 相关文档
- [后端API完整参考手册](./Backend_API_Reference.md)
- [后端数据模型设计文档](./Backend_Data_Models.md)
- [前端对接指南](./Frontend_Integration_Guide.md) 