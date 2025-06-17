# 访客管理系统通用化配置引擎 API 规范文档

## 📋 API 概述

**系统名称**: 访客管理系统通用化配置引擎  
**API版本**: v2.0  
**技术栈**: FastAPI + PostgreSQL + Redis  
**认证方式**: JWT Bearer Token  
**API基础路径**: `/api/v1`

## 🎯 核心配置引擎 API

### 1. 表单配置 API (`/config/forms`)

#### 1.1 创建表单配置
```http
POST /api/v1/config/forms
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "config_name": "访客登记表单",
  "form_type": "visitor_registration",
  "description": "标准访客登记表单配置",
  "fields": [
    {
      "field_name": "visitor_name",
      "field_type": "text",
      "label": "访客姓名",
      "required": true,
      "validation_rules": {
        "min_length": 2,
        "max_length": 50,
        "pattern": "^[\\u4e00-\\u9fa5a-zA-Z\\s]+$"
      }
    },
    {
      "field_name": "phone",
      "field_type": "tel",
      "label": "联系电话",
      "required": true,
      "validation_rules": {
        "pattern": "^1[3-9]\\d{9}$"
      }
    },
    {
      "field_name": "visit_purpose",
      "field_type": "select",
      "label": "来访目的",
      "required": true,
      "options": [
        {"value": "business", "label": "商务洽谈"},
        {"value": "interview", "label": "面试"},
        {"value": "meeting", "label": "会议"}
      ]
    }
  ],
  "ui_schema": {
    "layout": "vertical",
    "submit_button_text": "提交登记",
    "theme": "default"
  },
  "validation_schema": {
    "required_fields": ["visitor_name", "phone", "visit_purpose"],
    "conditional_rules": []
  }
}
```

**响应示例 (201 Created):**
```json
{
  "id": "uuid-form-config-id",
  "tenant_id": "tenant-001",
  "config_name": "访客登记表单",
  "form_type": "visitor_registration",
  "form_version": 1,
  "fields": [...],
  "ui_schema": {...},
  "validation_schema": {...},
  "is_active": true,
  "created_at": "2025-01-01T12:00:00Z",
  "created_by": "admin"
}
```

#### 1.2 获取表单配置列表
```http
GET /api/v1/config/forms?skip=0&limit=10&form_type=visitor_registration&is_active=true
Authorization: Bearer {jwt_token}
```

#### 1.3 获取表单渲染数据
```http
GET /api/v1/config/forms/{config_id}/render
Authorization: Bearer {jwt_token}
```

#### 1.4 验证表单数据
```http
POST /api/v1/config/forms/{config_id}/validate
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "visitor_name": "张三",
  "phone": "13812345678",
  "visit_purpose": "business"
}
```

### 2. 工作流配置 API (`/config/workflows`)

#### 2.1 创建工作流配置
```http
POST /api/v1/config/workflows
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "workflow_name": "访客审批工作流",
  "workflow_type": "visitor_approval",
  "description": "标准访客审批流程",
  "trigger_conditions": {
    "form_type": "visitor_registration",
    "visit_purpose": ["business", "meeting"]
  },
  "steps": [
    {
      "step_name": "部门审批",
      "step_type": "manual_approval",
      "step_order": 1,
      "assignee_type": "department_manager",
      "timeout_minutes": 1440,
      "auto_approval_rules": {
        "conditions": [],
        "enabled": false
      }
    },
    {
      "step_name": "安保审批",
      "step_type": "manual_approval", 
      "step_order": 2,
      "assignee_type": "security_officer",
      "timeout_minutes": 720
    },
    {
      "step_name": "发送通知",
      "step_type": "notification",
      "step_order": 3,
      "notification_config": {
        "channels": ["sms", "email"],
        "templates": {
          "sms": "您的访客申请已通过审批",
          "email": "访客申请审批通知"
        }
      }
    }
  ],
  "failure_handling": {
    "retry_count": 3,
    "retry_interval_minutes": 30
  }
}
```

#### 2.2 启动工作流执行
```http
POST /api/v1/config/workflows/{workflow_id}/execute
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "context_data": {
    "visitor_id": "uuid-visitor-id",
    "form_data": {
      "visitor_name": "张三",
      "phone": "13812345678",
      "visit_purpose": "business"
    }
  },
  "priority": "normal"
}
```

#### 2.3 执行工作流步骤
```http
POST /api/v1/config/workflows/executions/{execution_id}/step
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "step_action": "approve",
  "comments": "审批通过",
  "step_data": {
    "approval_result": "approved",
    "approval_time": "2025-01-01T15:30:00Z"
  }
}
```

### 3. 空间配置 API (`/config/spatial`)

#### 3.1 创建空间配置
```http
POST /api/v1/config/spatial
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "config_name": "总部大厦空间配置",
  "description": "总部大厦完整空间层级管理",
  "hierarchy_levels": [
    {"level": 1, "type": "site", "name": "站点"},
    {"level": 2, "type": "building", "name": "楼栋"},
    {"level": 3, "type": "floor", "name": "楼层"},
    {"level": 4, "type": "zone", "name": "区域"},
    {"level": 5, "type": "room", "name": "房间"}
  ],
  "access_control_rules": {
    "default_access_level": "restricted",
    "visitor_accessible_types": ["room", "meeting_room"],
    "requires_escort": ["server_room", "finance_area"]
  }
}
```

#### 3.2 创建空间实体
```http
POST /api/v1/config/spatial/{config_id}/entities
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "entity_code": "HQ-B1-F1-001",
  "entity_name": "会议室A",
  "entity_type": "room",
  "parent_id": "uuid-floor-entity-id",
  "capacity": 12,
  "area_sqm": 25.5,
  "coordinates": {
    "latitude": 39.908722,
    "longitude": 116.397496
  },
  "facilities": [
    "projector",
    "whiteboard", 
    "video_conference"
  ],
  "access_devices": [
    {
      "device_id": "door-001",
      "device_type": "door_controller",
      "device_name": "会议室A门禁"
    }
  ],
  "operating_hours": {
    "weekdays": {
      "start": "08:00",
      "end": "18:00"
    },
    "weekends": {
      "start": "09:00", 
      "end": "17:00"
    }
  }
}
```

#### 3.3 获取空间层级结构
```http
GET /api/v1/config/spatial/{config_id}/hierarchy?include_inactive=false
Authorization: Bearer {jwt_token}
```

#### 3.4 搜索空间实体
```http
GET /api/v1/config/spatial/search?query=会议室&entity_types=room,meeting_room&limit=20
Authorization: Bearer {jwt_token}
```

### 4. 业务规则 API (`/config/rules`)

#### 4.1 创建业务规则
```http
POST /api/v1/config/rules
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "rule_name": "VIP访客自动审批",
  "rule_type": "validation_rule",
  "rule_category": "auto_approval",
  "description": "VIP客户访客申请自动审批规则",
  "conditions": {
    "operator": "AND",
    "rules": [
      {
        "field": "visitor_company",
        "operator": "in",
        "value": ["重要客户A", "重要客户B", "重要客户C"]
      },
      {
        "field": "visit_purpose", 
        "operator": "equals",
        "value": "business"
      },
      {
        "field": "visit_time",
        "operator": "between",
        "value": ["09:00", "17:00"]
      }
    ]
  },
  "actions": [
    {
      "action_type": "auto_approve",
      "parameters": {
        "approval_level": "department",
        "skip_security_check": false
      }
    },
    {
      "action_type": "send_notification",
      "parameters": {
        "recipients": ["security@company.com"],
        "template": "vip_visitor_auto_approved"
      }
    }
  ],
  "priority": 90,
  "execution_order": 1
}
```

#### 4.2 执行业务规则
```http
POST /api/v1/config/rules/{rule_id}/execute
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "input_data": {
    "visitor_company": "重要客户A",
    "visit_purpose": "business",
    "visit_time": "14:30",
    "visitor_name": "李总",
    "phone": "13987654321"
  },
  "execution_context": {
    "visitor_id": "uuid-visitor-id",
    "form_submission_id": "uuid-form-id"
  }
}
```

**响应示例:**
```json
{
  "execution_id": "uuid-execution-id",
  "rule_id": "uuid-rule-id",
  "execution_result": "success",
  "conditions_met": true,
  "actions_executed": [
    {
      "action_type": "auto_approve",
      "result": "success",
      "output": {
        "approval_granted": true,
        "approval_level": "department"
      }
    },
    {
      "action_type": "send_notification",
      "result": "success",
      "output": {
        "notification_sent": true,
        "recipients": ["security@company.com"]
      }
    }
  ],
  "execution_time_ms": 245,
  "executed_at": "2025-01-01T14:30:15Z"
}
```

#### 4.3 批量执行业务规则
```http
POST /api/v1/config/rules/batch-execute?rule_type=validation_rule&rule_category=auto_approval
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "input_data": {
    "visitor_company": "重要客户A",
    "visit_purpose": "business"
  }
}
```

#### 4.4 获取规则执行统计
```http
GET /api/v1/config/rules/statistics/execution-summary?rule_type=validation_rule&start_time=2025-01-01T00:00:00Z&end_time=2025-01-01T23:59:59Z
Authorization: Bearer {jwt_token}
```

## 🔐 认证和授权

### JWT Token 格式
```json
{
  "sub": "user_id",
  "tenant_id": "tenant-001", 
  "username": "admin",
  "role": "admin",
  "permissions": [
    "config:read",
    "config:write", 
    "config:execute"
  ],
  "exp": 1640995200,
  "iat": 1640908800
}
```

### 权限要求

| API操作 | 所需权限 |
|---------|----------|
| 查看配置 | `config:read` |
| 创建/更新配置 | `config:write` |
| 删除配置 | `config:delete` |
| 执行工作流/规则 | `config:execute` |
| 查看统计数据 | `config:analytics` |

## 🚨 错误响应格式

### 标准错误响应
```json
{
  "detail": "错误详细信息",
  "error_code": "CONFIG_001",
  "timestamp": "2025-01-01T12:00:00Z",
  "path": "/api/v1/config/forms",
  "tenant_id": "tenant-001"
}
```

### 常见错误代码

| 错误代码 | HTTP状态码 | 说明 |
|----------|------------|------|
| CONFIG_001 | 400 | 配置参数无效 |
| CONFIG_002 | 404 | 配置不存在 |
| CONFIG_003 | 409 | 配置名称重复 |
| CONFIG_004 | 422 | 表单验证失败 |
| WORKFLOW_001 | 400 | 工作流执行失败 |
| WORKFLOW_002 | 408 | 工作流执行超时 |
| RULE_001 | 400 | 规则条件解析失败 |
| RULE_002 | 500 | 规则执行异常 |

## 📊 性能指标

### 响应时间目标
- 配置查询: < 200ms
- 配置创建/更新: < 500ms
- 工作流启动: < 300ms
- 规则执行: < 100ms
- 批量操作: < 2s

### 并发支持
- 同时在线租户: 100+
- 单租户并发请求: 1000 req/min
- 工作流并发执行: 50个实例/租户

## 🎛️ 配置引擎特性

### 1. 表单配置引擎
- ✅ 15种字段类型支持
- ✅ 动态验证规则
- ✅ 条件显示逻辑
- ✅ 自定义UI主题
- ✅ 多语言支持

### 2. 工作流配置引擎  
- ✅ 多步骤审批流程
- ✅ 条件分支逻辑
- ✅ 超时处理机制
- ✅ 失败重试策略
- ✅ 实时状态跟踪

### 3. 空间配置引擎
- ✅ 无限层级支持
- ✅ 地理坐标定位
- ✅ 设备集成管理
- ✅ 访问权限控制
- ✅ 路径规划支持

### 4. 业务规则引擎
- ✅ 复杂条件表达式
- ✅ 多种动作类型
- ✅ 规则优先级管理
- ✅ 批量执行优化
- ✅ 执行性能监控

## 🔄 API 版本管理

### 当前版本: v1
- 基础路径: `/api/v1`
- 支持时间: 2025年 - 2026年
- 废弃通知: 提前6个月

### 即将发布: v2 (预计2025年Q3)
- GraphQL支持
- 实时WebSocket推送
- 高级分析API
- 插件扩展接口

## 📝 使用示例

### 完整配置流程示例
```bash
# 1. 创建表单配置
curl -X POST "https://api.company.com/api/v1/config/forms" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d @form_config.json

# 2. 创建工作流配置
curl -X POST "https://api.company.com/api/v1/config/workflows" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d @workflow_config.json

# 3. 创建业务规则
curl -X POST "https://api.company.com/api/v1/config/rules" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d @business_rule.json

# 4. 测试配置集成
curl -X POST "https://api.company.com/api/v1/config/forms/{form_id}/validate" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d @test_form_data.json
```

---

**文档版本**: v2.0  
**最后更新**: 2025年1月1日  
**维护团队**: 后端架构组 