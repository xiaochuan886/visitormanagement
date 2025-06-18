# 访客管理系统API接口规范

## �� 文档信息
- **版本**: v2.1
- **创建日期**: 2025-06-18
- **最后更新**: 2025-06-18
- **维护者**: API架构师AI
- **适用角色**: 前后端开发团队、测试团队、第三方集成开发者
- **依赖文档**: functional-requirements.md, system-overview.md

## 🎯 文档目标
定义访客管理系统的完整API接口规范，从现有的28个API端点扩展到53个API端点，支持四大场景和移动端备用方案。

## 🏗️ API架构概览

### 技术规范
```yaml
协议: HTTP/HTTPS
架构风格: RESTful API
数据格式: JSON
认证方式: JWT Bearer Token
版本控制: URL路径版本化 (/api/v1/, /api/v2/)
限流策略: 100 req/min (一般用户), 1000 req/min (设备端)
文档标准: OpenAPI 3.0 (Swagger)
```

### API分组结构
| 分组 | 路径前缀 | 描述 | API数量 |
|------|----------|------|---------|
| 认证授权 | `/api/v1/auth` | 用户认证、权限管理 | 8个 |
| 访客管理 | `/api/v1/visitors` | 访客CRUD、状态管理 | 12个 |
| 审批流程 | `/api/v1/approvals` | 审批工作流 | 6个 |
| 组织架构 | `/api/v1/organizations` | 租户、部门、员工 | 9个 |
| 配置引擎 | `/api/v1/configurations` | 系统配置管理 | 8个 |
| 设备管理 | `/api/v1/devices` | 硬件设备集成 | 5个 |
| 通知服务 | `/api/v1/notifications` | 消息推送 | 3个 |
| 数据分析 | `/api/v1/analytics` | 统计报表 | 2个 |

### 全新API端点 (53个API总览)
```
认证授权模块 (8个):
POST   /api/v1/auth/login                    # 用户登录
POST   /api/v1/auth/logout                   # 用户登出
POST   /api/v1/auth/refresh                  # 刷新Token
GET    /api/v1/auth/profile                  # 获取用户信息
PUT    /api/v1/auth/profile                  # 更新用户信息
POST   /api/v1/auth/change-password          # 修改密码
POST   /api/v1/auth/forgot-password          # 忘记密码
POST   /api/v1/auth/verify-token             # Token验证

访客管理模块 (12个):
GET    /api/v1/visitors                      # 获取访客列表
POST   /api/v1/visitors                      # 创建访客申请
GET    /api/v1/visitors/{id}                 # 获取访客详情
PUT    /api/v1/visitors/{id}                 # 更新访客信息
DELETE /api/v1/visitors/{id}                 # 删除访客记录
POST   /api/v1/visitors/batch                # 批量创建访客
PUT    /api/v1/visitors/{id}/status          # 更新访客状态
POST   /api/v1/visitors/{id}/checkin         # 访客签到
POST   /api/v1/visitors/{id}/checkout        # 访客签出
GET    /api/v1/visitors/{id}/qrcode          # 获取访客二维码
POST   /api/v1/visitors/verify               # 验证访客身份
GET    /api/v1/visitors/export               # 导出访客数据

审批流程模块 (6个):
GET    /api/v1/approvals                     # 获取审批列表
POST   /api/v1/approvals/{id}/approve        # 审批通过
POST   /api/v1/approvals/{id}/reject         # 审批拒绝
GET    /api/v1/approvals/{id}/history        # 获取审批历史
POST   /api/v1/approvals/batch               # 批量审批
GET    /api/v1/approvals/statistics          # 审批统计

组织架构模块 (9个):
GET    /api/v1/organizations/tenants         # 获取租户列表
GET    /api/v1/organizations/departments     # 获取部门列表
POST   /api/v1/organizations/departments     # 创建部门
GET    /api/v1/organizations/employees       # 获取员工列表
POST   /api/v1/organizations/employees       # 创建员工
GET    /api/v1/organizations/employees/{id}  # 获取员工详情
PUT    /api/v1/organizations/employees/{id}  # 更新员工信息
GET    /api/v1/organizations/permissions     # 获取权限列表
POST   /api/v1/organizations/permissions     # 分配权限

配置引擎模块 (8个):
GET    /api/v1/configurations/forms          # 获取表单配置
POST   /api/v1/configurations/forms          # 创建表单配置
GET    /api/v1/configurations/workflows      # 获取工作流配置
POST   /api/v1/configurations/workflows      # 创建工作流配置
GET    /api/v1/configurations/rules          # 获取业务规则
POST   /api/v1/configurations/rules          # 创建业务规则
GET    /api/v1/configurations/spatial        # 获取空间配置
POST   /api/v1/configurations/spatial        # 创建空间配置

设备管理模块 (5个):
GET    /api/v1/devices                       # 获取设备列表
POST   /api/v1/devices/register              # 注册设备
PUT    /api/v1/devices/{id}/status           # 更新设备状态
POST   /api/v1/devices/{id}/heartbeat        # 设备心跳
GET    /api/v1/devices/{id}/logs             # 获取设备日志

通知服务模块 (3个):
POST   /api/v1/notifications/send            # 发送通知
GET    /api/v1/notifications                 # 获取通知列表
PUT    /api/v1/notifications/{id}/read       # 标记已读

数据分析模块 (2个):
GET    /api/v1/analytics/dashboard           # 仪表板数据
GET    /api/v1/analytics/reports             # 生成报表
```

## 🔐 认证授权API

### 1. 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin@example.com",
  "password": "password123",
  "tenant_id": "tenant_001"
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4=",
    "expires_in": 3600,
    "user": {
      "id": "user_001",
      "username": "admin@example.com",
      "name": "管理员",
      "role": "admin",
      "permissions": ["visitor:read", "visitor:write", "system:config"]
    }
  }
}
```

### 2. Token验证
```http
POST /api/v1/auth/verify-token
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Token有效",
  "data": {
    "valid": true,
    "expires_at": "2025-06-18T15:30:00Z",
    "user_id": "user_001",
    "tenant_id": "tenant_001"
  }
}
```

## 👥 访客管理API

### 1. 创建访客申请 (四大场景统一入口)
```http
POST /api/v1/visitors
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "scenario": "self_apply|employee_invite_known|employee_invite_unknown|employee_batch_invite",
  "visitor_info": {
    "name": "张三",
    "phone": "13800138000",
    "id_card": "310101199001011234",
    "company": "访客公司",
    "purpose": "商务洽谈"
  },
  "visit_info": {
    "visit_date": "2025-06-19",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "visit_type": "individual|department",
    "visitee_id": "emp_001",
    "department_id": "dept_001",
    "areas": ["building_a", "meeting_room_1"]
  },
  "scenario_data": {
    // 场景1: 自主申请
    "contact_verification": {
      "visitee_name": "李四",
      "visitee_phone": "13900139000"
    },
    
    // 场景2: 员工邀请已知访客
    "authorization_type": "temporary|long_term",
    "auto_approve": true,
    
    // 场景3: 员工邀请未知访客
    "activity_info": {
      "title": "产品发布会",
      "max_participants": 100,
      "invite_code": "ABC123",
      "link_expires": "2025-06-25T23:59:59Z"
    },
    
    // 场景4: 批量邀请
    "batch_data": [
      {
        "name": "王五",
        "phone": "13700137000",
        "id_card": "310101199002022345"
      }
    ]
  }
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "访客申请创建成功",
  "data": {
    "visitor_id": "visitor_001",
    "application_id": "app_001", 
    "status": "pending",
    "qr_code": "https://api.example.com/qr/visitor_001.png",
    "estimated_approval_time": "2小时内",
    "tracking_number": "VIS20250618001"
  }
}
```

### 2. 获取访客列表 (支持多维度筛选)
```http
GET /api/v1/visitors?status=pending&date_from=2025-06-01&date_to=2025-06-30&department=sales&page=1&size=20
Authorization: Bearer {access_token}
```

**查询参数**:
- `status`: 访客状态 (pending|approved|rejected|checked_in|checked_out|cancelled|expired)
- `date_from/date_to`: 访问日期范围
- `department`: 部门筛选
- `search`: 关键词搜索 (姓名、手机号、公司)
- `scenario`: 申请场景筛选
- `page/size`: 分页参数

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "total": 150,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": "visitor_001",
        "name": "张三",
        "phone": "138****8000",
        "company": "访客公司",
        "status": "pending",
        "visit_date": "2025-06-19",
        "visitee": "李四",
        "department": "销售部",
        "created_at": "2025-06-18T10:30:00Z",
        "qr_code_url": "https://api.example.com/qr/visitor_001.png"
      }
    ]
  }
}
```

### 3. 访客身份验证 (门岗/前台通用)
```http
POST /api/v1/visitors/verify
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "verification_method": "qr_code|id_card|phone|manual",
  "verification_data": {
    "qr_code": "visitor_001_qr_data",
    "id_card": "310101199001011234",
    "phone": "13800138000",
    "manual_input": {
      "name": "张三",
      "tracking_number": "VIS20250618001"
    }
  },
  "device_info": {
    "device_id": "gate_001",
    "device_type": "gate|reception",
    "location": "主门岗"
  }
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "验证成功",
  "data": {
    "visitor": {
      "id": "visitor_001",
      "name": "张三",
      "phone": "138****8000",
      "status": "approved",
      "visit_date": "2025-06-19",
      "time_window": "09:00-17:00",
      "authorized_areas": ["building_a", "meeting_room_1"],
      "visitee": "李四 (销售部)",
      "photo_url": "https://api.example.com/photos/visitor_001.jpg"
    },
    "verification_result": {
      "success": true,
      "risk_level": "low|medium|high",
      "warnings": [],
      "next_action": "allow_entry|require_escort|deny_entry"
    }
  }
}
```

## 📋 审批流程API

### 1. 获取待审批列表
```http
GET /api/v1/approvals?status=pending&priority=high&page=1&size=20
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "total": 25,
    "items": [
      {
        "id": "approval_001",
        "visitor_id": "visitor_001",
        "visitor_name": "张三",
        "company": "访客公司",
        "purpose": "商务洽谈",
        "visit_date": "2025-06-19",
        "visitee": "李四",
        "priority": "normal",
        "submit_time": "2025-06-18T10:30:00Z",
        "auto_approve_eligible": false,
        "risk_indicators": []
      }
    ]
  }
}
```

### 2. 批量审批
```http
POST /api/v1/approvals/batch
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "action": "approve|reject",
  "approval_ids": ["approval_001", "approval_002", "approval_003"],
  "reason": "批量审批通过",
  "conditions": {
    "escort_required": false,
    "area_restrictions": [],
    "time_restrictions": {}
  }
}
```

## 🏢 组织架构API

### 1. 获取员工列表 (支持被访人验证)
```http
GET /api/v1/organizations/employees?search=李四&phone=13900139000&department=sales
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": "emp_001",
        "name": "李四",
        "phone": "139****9000",
        "email": "lisi@example.com",
        "department": "销售部",
        "position": "销售经理",
        "employee_id": "EMP001",
        "can_be_visited": true,
        "authorization_level": 3
      }
    ]
  }
}
```

## ⚙️ 配置引擎API

### 1. 获取动态表单配置
```http
GET /api/v1/configurations/forms?scenario=self_apply&version=latest
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "form_id": "form_self_apply_v1",
    "scenario": "self_apply",
    "version": "1.0",
    "fields": [
      {
        "name": "name",
        "type": "text",
        "label": "姓名",
        "required": true,
        "validation": {
          "min_length": 2,
          "max_length": 20,
          "pattern": "^[\\u4e00-\\u9fa5a-zA-Z]+$"
        }
      },
      {
        "name": "phone",
        "type": "text",
        "label": "手机号",
        "required": true,
        "validation": {
          "pattern": "^1[3-9]\\d{9}$"
        }
      },
      {
        "name": "visit_purpose",
        "type": "select",
        "label": "访问目的",
        "required": true,
        "options": [
          {"value": "business", "label": "商务洽谈"},
          {"value": "interview", "label": "面试"},
          {"value": "delivery", "label": "送货"},
          {"value": "maintenance", "label": "设备维护"}
        ]
      }
    ],
    "layout": {
      "columns": 1,
      "spacing": "medium"
    },
    "conditional_logic": [
      {
        "field": "visit_purpose",
        "condition": "equals",
        "value": "interview",
        "action": "show",
        "target": "interview_position"
      }
    ]
  }
}
```

## 📱 设备管理API

### 1. 设备心跳上报
```http
POST /api/v1/devices/{device_id}/heartbeat
Authorization: Bearer {device_token}
Content-Type: application/json

{
  "timestamp": "2025-06-18T14:30:00Z",
  "status": "online",
  "metrics": {
    "cpu_usage": 15.5,
    "memory_usage": 45.2,
    "disk_usage": 60.0,
    "temperature": 35.5
  },
  "capabilities": ["qr_scan", "id_card_read", "face_recognition"],
  "last_sync": "2025-06-18T14:25:00Z"
}
```

### 2. 设备离线数据同步
```http
POST /api/v1/devices/{device_id}/sync
Authorization: Bearer {device_token}
Content-Type: application/json

{
  "offline_period": {
    "start": "2025-06-18T12:00:00Z",
    "end": "2025-06-18T14:30:00Z"
  },
  "offline_data": [
    {
      "type": "visitor_verification",
      "timestamp": "2025-06-18T13:15:00Z",
      "data": {
        "visitor_id": "visitor_001",
        "verification_method": "qr_code",
        "result": "success",
        "device_location": "main_gate"
      }
    }
  ]
}
```

## 🔔 通知服务API

### 1. 发送通知
```http
POST /api/v1/notifications/send
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "type": "visitor_approved|visitor_arrived|emergency_alert",
  "recipients": [
    {
      "type": "user",
      "id": "user_001",
      "channels": ["email", "wechat", "sms"]
    },
    {
      "type": "role", 
      "name": "security_guard",
      "channels": ["app_push"]
    }
  ],
  "content": {
    "title": "访客申请已通过",
    "body": "您的访客张三的申请已通过审批，预计到达时间：明天上午9点",
    "data": {
      "visitor_id": "visitor_001",
      "action_url": "/visitors/visitor_001"
    }
  },
  "priority": "normal|high|urgent",
  "schedule": {
    "send_immediately": true,
    "send_at": "2025-06-19T08:00:00Z"
  }
}
```

## 📊 数据分析API

### 1. 仪表板数据
```http
GET /api/v1/analytics/dashboard?period=today|week|month&tenant_id=tenant_001
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "summary": {
      "total_visitors": 156,
      "pending_approvals": 12,
      "checked_in_visitors": 23,
      "today_appointments": 45
    },
    "trends": {
      "visitor_flow": [
        {"hour": "09:00", "count": 15},
        {"hour": "10:00", "count": 28},
        {"hour": "11:00", "count": 22}
      ],
      "approval_rate": 95.5,
      "average_approval_time": "1.5小时"
    },
    "alerts": [
      {
        "type": "security",
        "message": "检测到黑名单访客申请",
        "visitor_id": "visitor_999",
        "timestamp": "2025-06-18T14:20:00Z"
      }
    ]
  }
}
```

## 🔧 通用约定

### 响应格式标准
```json
{
  "code": 0,           // 0:成功, >0:业务错误, <0:系统错误
  "message": "操作成功",  // 响应消息
  "data": {},          // 响应数据
  "timestamp": "2025-06-18T14:30:00Z",
  "request_id": "req_12345"
}
```

### 错误码定义
| 错误码 | 描述 | 示例 |
|--------|------|------|
| 0 | 成功 | 操作成功 |
| 1001 | 参数错误 | 必填字段缺失 |
| 1002 | 数据不存在 | 访客不存在 |
| 1003 | 权限不足 | 无访问权限 |
| 1004 | 状态错误 | 访客状态不允许此操作 |
| 1005 | 业务规则限制 | 超过申请频率限制 |
| 2001 | 认证失败 | Token无效或过期 |
| 2002 | 限流触发 | 请求过于频繁 |
| -1 | 系统错误 | 内部服务器错误 |

### 分页参数
```
page: 页码 (从1开始)
size: 每页数量 (默认20，最大100)
sort: 排序字段
order: 排序方向 (asc|desc)
```

### 日期时间格式
- 日期: `YYYY-MM-DD` (如: 2025-06-18)
- 时间: `HH:mm:ss` (如: 09:30:00)  
- 日期时间: `ISO 8601` (如: 2025-06-18T09:30:00Z)

---
**文档版本**: v2.1 | **最后更新**: 2025-01-27 