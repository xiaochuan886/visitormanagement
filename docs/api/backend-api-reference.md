# 访客管理系统后端 API 完整参考手册

## 🎯 API概述

访客管理系统提供 **53个API端点**，覆盖四大核心场景、门岗前台系统、移动端备用方案等完整业务功能。所有API遵循 **RESTful** 设计原则，支持 **JSON** 数据格式，提供完整的 **OpenAPI 3.0** 规范文档。

### API特性升级
- ✅ **场景化API设计**: 支持四大核心业务场景的专用端点
- ✅ **多端适配**: Web端、门岗设备端、前台系统、移动端统一API
- ✅ **离线支持**: 关键API支持离线缓存和同步机制
- ✅ **实时通信**: WebSocket集成，支持多端状态实时同步
- ✅ **多租户支持**: 所有API支持租户隔离
- ✅ **JWT认证**: 基于Token的无状态认证
- ✅ **数据验证**: Pydantic模型严格验证
- ✅ **错误处理**: 统一的错误响应格式
- ✅ **自动文档**: Swagger UI 和 ReDoc 支持

### 快速导航
- [认证授权API](#🔐-认证授权api) - 用户登录、Token管理、权限验证 (8个端点)
- [访客管理API](#👥-访客管理api) - 四大场景访客CRUD、状态管理 (15个端点)
- [审批流程API](#✅-审批流程api) - 工作流引擎、批量审批 (6个端点)
- [门岗系统API](#🚪-门岗系统api) - 身份验证、入园放行、离线支持 (8个端点)
- [前台系统API](#🏢-前台系统api) - 签到服务、被访人通知、会议室协调 (6个端点)
- [移动端备用API](#📱-移动端备用api) - APP/小程序离线验证、应急处理 (5个端点)
- [组织架构API](#🏬-组织架构api) - 员工、部门、权限管理 (9个端点)
- [配置引擎API](#⚙️-配置引擎api) - 场景配置、表单工作流 (8个端点)
- [设备管理API](#🔧-设备管理api) - 硬件设备、健康监控 (5个端点)
- [通知服务API](#📢-通知服务api) - 消息推送、实时通信 (3个端点)

## 🔧 通用规范

### 请求格式
```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
X-Tenant-ID: <tenant_id>  # 可选，默认从Token解析
```

### 响应格式
#### 成功响应
```json
{
  "id": "string",
  "name": "string",
  "created_at": "2025-06-17T07:00:00Z",
  "updated_at": "2025-06-17T07:00:00Z"
}
```

#### 错误响应
```json
{
  "detail": "错误描述信息",
  "error_code": "BUSINESS_ERROR_CODE",
  "timestamp": "2025-06-17T07:00:00Z"
}
```

### HTTP状态码
| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | OK | 成功获取资源 |
| 201 | Created | 成功创建资源 |
| 204 | No Content | 成功删除资源 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 认证失败 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

### 分页参数
```
?skip=0&limit=20&sort_by=created_at&sort_order=desc
```

## 🔐 认证授权API

### 1. 用户登录
**获取JWT访问令牌，支持多角色用户类型**

```http
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "username": "admin",
  "password": "secure_password",
  "tenant_id": "default_tenant",
  "login_type": "web|gate|reception|mobile"
}
```

**响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_info": {
    "user_id": "user_001",
    "username": "admin",
    "name": "管理员",
    "role": "admin|employee|security_guard|receptionist|dept_manager",
    "tenant_id": "default_tenant",
    "permissions": ["visitor:read", "visitor:write", "gate:verify", "reception:checkin"],
    "department_id": "dept_001",
    "authorization_level": 5
  }
}
```

### 2. 用户登出
**安全登出并使Token失效**

```http
POST /api/v1/auth/logout
```

**响应** (200):
```json
{
  "message": "登出成功",
  "timestamp": "2025-06-18T10:00:00Z"
}
```

### 3. Token刷新
**刷新访问令牌**

```http
POST /api/v1/auth/refresh
```

**请求体**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 4. Token验证
**验证Token有效性**

```http
POST /api/v1/auth/verify-token
```

**响应** (200):
```json
{
  "valid": true,
  "expires_at": "2025-06-18T15:30:00Z",
  "user_id": "user_001",
  "tenant_id": "default_tenant"
}
```

### 5. 获取用户信息
**获取当前登录用户详细信息**

```http
GET /api/v1/auth/profile
```

**响应** (200):
```json
{
  "user_id": "user_001",
  "username": "admin",
  "name": "管理员",
  "email": "admin@company.com",
  "role": "admin",
  "department": {
    "id": "dept_001",
    "name": "管理部门"
  },
  "permissions": ["visitor:read", "visitor:write", "system:config"],
  "last_login": "2025-06-18T09:00:00Z"
}
```

### 6. 更新用户信息
**更新当前用户基本信息**

```http
PUT /api/v1/auth/profile
```

**请求体**:
```json
{
  "name": "新姓名",
  "email": "new_email@company.com",
  "phone": "13800138000"
}
```

### 7. 修改密码
**修改当前用户密码**

```http
POST /api/v1/auth/change-password
```

**请求体**:
```json
{
  "current_password": "old_password",
  "new_password": "new_secure_password"
}
```

### 8. 忘记密码
**密码重置流程**

```http
POST /api/v1/auth/forgot-password
```

**请求体**:
```json
{
  "username": "admin",
  "email": "admin@company.com"
}
```

## 👥 访客管理API

### 9. 创建访客申请 (四大场景统一入口)
**支持访客自主申请、员工邀约等四大核心场景**

```http
POST /api/v1/visitors/
```

**请求体** (场景1: 访客自主申请):
```json
{
  "scenario": "self_apply",
  "visitor_info": {
    "name": "张三",
    "phone": "13800138000",
    "id_number": "110101199001011234",
    "company": "ABC公司",
    "purpose": "business_meeting"
  },
  "visit_info": {
    "visit_date": "2025-06-19",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "visit_type": "individual",
    "visitee_id": "emp_001",
    "areas": ["building_a", "meeting_room_1"]
  },
  "scenario_data": {
    "contact_verification": {
      "visitee_name": "李四",
      "visitee_phone": "13900139000"
    }
  }
}
```

**请求体** (场景2: 员工邀约已知访客):
```json
{
  "scenario": "employee_invite_known",
  "visitor_info": {
    "name": "王五",
    "phone": "13700137000",
    "id_number": "310101199505051234",
    "company": "合作伙伴公司",
    "purpose": "技术交流"
  },
  "visit_info": {
    "visit_date": "2025-06-20",
    "start_time": "14:00:00",
    "end_time": "16:00:00",
    "visit_type": "individual",
    "areas": ["building_b", "lab_room_1"]
  },
  "scenario_data": {
    "authorization_type": "temporary",
    "auto_approve": true,
    "special_permissions": ["lab_access"]
  }
}
```

**响应** (201):
```json
{
  "id": 1,
  "pass_code": "V20250619001",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "scenario": "self_apply",
  "name": "张三",
  "phone": "13800138000",
  "id_number": "110101199001011234",
  "company": "ABC公司",
  "purpose": "business_meeting",
  "status": "pending",
  "visit_date": "2025-06-19T09:00:00Z",
  "end_time": "2025-06-19T17:00:00Z",
  "visitee": {
    "id": "emp_001",
    "name": "李四",
    "department": "产品部"
  },
  "areas": ["building_a", "meeting_room_1"],
  "tenant_id": "default_tenant",
  "created_at": "2025-06-18T10:00:00Z",
  "updated_at": "2025-06-18T10:00:00Z"
}
```

### 10. 批量创建访客 (场景3&4)
**支持邀请未知访客和Excel批量导入**

```http
POST /api/v1/visitors/batch
```

**请求体** (场景3: 邀请未知访客):
```json
{
  "scenario": "employee_invite_unknown",
  "event_info": {
    "event_name": "技术分享会",
    "event_type": "training",
    "event_date": "2025-06-25",
    "location": "会议室A",
    "max_participants": 50
  },
  "invitation_config": {
    "registration_deadline": "2025-06-24T18:00:00Z",
    "approval_mode": "batch",
    "required_fields": ["name", "phone", "company", "position"]
  }
}
```

**响应** (201):
```json
{
  "invitation_id": "inv_001",
  "invitation_code": "TECH2025001",
  "invitation_link": "https://visitor.company.com/register/TECH2025001",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "event_name": "技术分享会",
  "max_participants": 50,
  "status": "active",
  "expires_at": "2025-06-24T18:00:00Z"
}
```

### 11. 获取访客列表
**获取当前租户的访客列表，支持多维度筛选**

```http
GET /api/v1/visitors/?skip=0&limit=20&status=pending&scenario=self_apply
```

**查询参数**:
- `skip` (int): 跳过记录数，默认0
- `limit` (int): 每页记录数，默认20，最大100
- `status` (string): 状态筛选 (`pending`, `approved`, `rejected`, `checked_in`, `checked_out`, `cancelled`, `expired`)
- `scenario` (string): 场景筛选 (`self_apply`, `employee_invite_known`, `employee_invite_unknown`, `employee_batch_invite`)
- `visitee_id` (string): 接待员工ID筛选
- `department_id` (string): 部门ID筛选
- `date_from` (string): 开始日期 (ISO格式)
- `date_to` (string): 结束日期 (ISO格式)
- `search` (string): 访客姓名或手机号搜索

**响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "pass_code": "V20250619001",
      "scenario": "self_apply",
      "name": "张三",
      "phone": "13800138000",
      "company": "ABC公司",
      "status": "pending",
      "purpose": "business_meeting",
      "visit_date": "2025-06-19T09:00:00Z",
      "visitee": {
        "id": "emp_001",
        "name": "李四",
        "department": "产品部"
      },
      "areas": ["building_a", "meeting_room_1"],
      "created_at": "2025-06-18T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  },
  "summary": {
    "pending": 5,
    "approved": 12,
    "checked_in": 3,
    "checked_out": 8
  }
}
```

### 12. 获取访客详情
**根据ID获取访客详细信息**

```http
GET /api/v1/visitors/{visitor_id}
```

**路径参数**:
- `visitor_id` (int): 访客ID

**响应** (200):
```json
{
  "id": 1,
  "pass_code": "V20250619001",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "scenario": "self_apply",
  "name": "张三",
  "phone": "13800138000",
  "id_number": "110101199001011234",
  "company": "ABC公司",
  "purpose": "business_meeting",
  "status": "approved",
  "visit_date": "2025-06-19T09:00:00Z",
  "end_time": "2025-06-19T17:00:00Z",
  "checkin_date": null,
  "checkout_date": null,
  "visitee": {
    "id": "emp_001",
    "name": "李四",
    "department": "产品部",
    "phone": "13900139000",
    "email": "li.si@company.com"
  },
  "areas": ["building_a", "meeting_room_1"],
  "access_permissions": {
    "can_enter_areas": ["building_a", "meeting_room_1"],
    "restricted_areas": ["server_room", "executive_floor"],
    "time_window": {
      "start": "2025-06-19T08:00:00Z",
      "end": "2025-06-19T18:00:00Z"
    }
  },
  "approval_history": [
    {
      "approver": "李四",
      "outcome": "approved",
      "comment": "同意访问",
      "approval_date": "2025-06-18T11:00:00Z"
    }
  ],
  "tenant_id": "default_tenant",
  "created_at": "2025-06-18T10:00:00Z",
  "updated_at": "2025-06-18T11:00:00Z"
}
```

### 13. 更新访客信息
**更新访客信息**

```http
PUT /api/v1/visitors/{visitor_id}
```

**请求体** (部分字段):
```json
{
  "phone": "13800138001",
  "company": "新公司名称",
  "purpose": "site_visit",
  "visit_date": "2025-06-20T09:00:00Z",
  "comment": "更新访客信息"
}
```

**响应** (200): 返回更新后的完整访客信息

### 14. 删除访客
**软删除访客记录**

```http
DELETE /api/v1/visitors/{visitor_id}
```

**响应** (204): 无内容

### 15. 更新访客状态
**更新访客状态（管理员权限）**

```http
PUT /api/v1/visitors/{visitor_id}/status
```

**请求体**:
```json
{
  "status": "approved|rejected|cancelled|expired",
  "comment": "状态变更原因",
  "operator_id": "admin_001"
}
```

### 16. 获取访客二维码
**获取访客专用二维码**

```http
GET /api/v1/visitors/{visitor_id}/qrcode
```

**响应** (200):
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "qr_content": "VISITOR:V20250619001:张三:13800138000",
  "expires_at": "2025-06-19T18:00:00Z"
}
```

### 17. 验证访客身份
**通用访客身份验证API**

```http
POST /api/v1/visitors/verify
```

**请求体**:
```json
{
  "verification_type": "qr_code|id_card|pass_code",
  "verification_data": "V20250619001",
  "checkpoint": "main_gate|reception|building_a_entrance"
}
```

**响应** (200):
```json
{
  "valid": true,
  "visitor": {
    "id": 1,
    "name": "张三",
    "company": "ABC公司",
    "visit_date": "2025-06-19",
    "visitee": "李四",
    "areas": ["building_a", "meeting_room_1"]
  },
  "permissions": {
    "can_enter": true,
    "allowed_areas": ["building_a", "meeting_room_1"],
    "time_valid": true,
    "blacklist_check": "passed"
  }
}
```

### 18. 访客签到
**访客到达签到**

```http
POST /api/v1/visitors/{visitor_id}/checkin
```

**请求体**:
```json
{
  "checkin_point": "main_entrance|reception_desk",
  "checkin_method": "qr_scan|id_verification|manual",
  "operator_id": "gate_001",
  "comment": "访客已到达前台"
}
```

**响应** (200):
```json
{
  "id": 1,
  "status": "checked_in",
  "checkin_date": "2025-06-19T09:15:00Z",
  "checkin_point": "main_entrance",
  "checkin_method": "qr_scan",
  "operator": "门岗1号",
  "updated_at": "2025-06-19T09:15:00Z"
}
```

### 19. 访客签出
**访客离开签出**

```http
POST /api/v1/visitors/{visitor_id}/checkout
```

**请求体**:
```json
{
  "checkout_point": "main_entrance",
  "checkout_method": "automatic|manual",
  "operator_id": "gate_001",
  "comment": "访客正常离开"
}
```

**响应** (200):
```json
{
  "id": 1,
  "status": "checked_out",
  "checkout_date": "2025-06-19T16:30:00Z",
  "checkout_point": "main_entrance",
  "visit_duration": "7小时15分钟",
  "updated_at": "2025-06-19T16:30:00Z"
}
```

### 20. 导出访客数据
**导出访客数据（Excel/CSV）**

```http
GET /api/v1/visitors/export?format=excel&date_from=2025-06-01&date_to=2025-06-30
```

**查询参数**:
- `format` (string): 导出格式 (`excel`, `csv`)
- `date_from` (string): 开始日期
- `date_to` (string): 结束日期
- `status` (string): 状态筛选
- `fields` (string): 导出字段，逗号分隔

**响应** (200): 返回文件下载链接或直接返回文件流

### 32. 离线数据缓存
**获取门岗离线验证所需的今日访客数据**

```http
GET /api/v1/gate/cache/today-visitors
```

**响应** (200):
```json
{
  "cache_timestamp": "2025-06-19T06:00:00Z",
  "cache_expiry": "2025-06-20T06:00:00Z",
  "visitors_data": [
    {
      "pass_code": "V20250619001",
      "name": "张三",
      "id_number": "110101199001011234",
      "visit_time_start": "09:00",
      "visit_time_end": "17:00",
      "areas": ["building_a"],
      "blacklist_status": "clear"
    }
  ],
  "blacklist": [
    {
      "id_number": "999999999999999999",
      "reason": "security_risk"
    }
  ]
}
```

### 33. 离线验证记录上传
**上传离线期间的验证记录**

```http
POST /api/v1/gate/offline/verify-sync
```

**请求体**:
```json
{
  "offline_period": {
    "start": "2025-06-19T10:00:00Z",
    "end": "2025-06-19T10:30:00Z"
  },
  "offline_records": [
    {
      "visitor_pass_code": "V20250619001",
      "verification_time": "2025-06-19T10:15:00Z",
      "verification_result": "success",
      "gate_id": "main_gate",
      "operator_id": "gate_001"
    }
  ]
}
```

### 34. 设备健康状态
**报告门岗设备健康状态**

```http
POST /api/v1/gate/devices/{device_id}/heartbeat
```

**请求体**:
```json
{
  "device_status": {
    "camera": "online",
    "id_reader": "online", 
    "printer": "paper_low",
    "network": "connected"
  },
  "performance_metrics": {
    "cpu_usage": 45,
    "memory_usage": 60,
    "storage_free": 75
  }
}
```

### 35. 应急开放模式
**紧急情况下的门禁开放**

```http
POST /api/v1/gate/emergency/open
```

**请求体**:
```json
{
  "emergency_type": "fire|evacuation|system_failure",
  "operator_id": "security_chief",
  "reason": "火警演练，开放所有通道"
}
```

## 🏢 前台系统API

### 36. 前台签到服务
**访客在前台完成签到**

```http
POST /api/v1/reception/visitors/{visitor_id}/checkin
```

**请求体**:
```json
{
  "checkin_method": "qr_scan|manual",
  "health_check": {
    "temperature": 36.5,
    "health_code": "green",
    "vaccination_status": "completed"
  },
  "safety_briefing": true,
  "receptionist_id": "reception_001"
}
```

**响应** (200):
```json
{
  "checkin_id": "checkin_001",
  "visitor_id": 1,
  "checkin_time": "2025-06-19T09:20:00Z",
  "receptionist": "前台小王",
  "visitor_badge": "VISITOR001",
  "safety_briefing_completed": true,
  "next_steps": "请前往电梯间，按访客卡进入对应楼层"
}
```

### 37. 通知被访人
**通知被访员工访客已到达**

```http
POST /api/v1/reception/hosts/{employee_id}/notify
```

**请求体**:
```json
{
  "visitor_id": 1,
  "notification_type": "sms|email|wechat|internal",
  "message": "您的访客张三已到达前台，请前往接待",
  "meeting_room": "会议室A"
}
```

**响应** (200):
```json
{
  "notification_id": "notify_001",
  "sent_at": "2025-06-19T09:21:00Z",
  "delivery_status": "sent",
  "employee_response": null,
  "estimated_arrival": "5分钟"
}
```

### 38. 会议室协调
**查询和预定会议室**

```http
GET /api/v1/reception/meeting-rooms/available
```

**查询参数**:
- `date` (string): 日期
- `start_time` (string): 开始时间
- `duration` (int): 持续时长（分钟）
- `capacity` (int): 最少容纳人数

**响应** (200):
```json
{
  "available_rooms": [
    {
      "room_id": "meeting_a",
      "name": "会议室A",
      "capacity": 10,
      "location": "3楼东侧",
      "equipment": ["投影仪", "白板", "视频会议"],
      "available_slots": [
        "09:00-10:00",
        "14:00-16:00"
      ]
    }
  ]
}
```

### 39. 访客等候管理
**管理访客等候区状态**

```http
GET /api/v1/reception/waiting-area/status
```

**响应** (200):
```json
{
  "current_capacity": 15,
  "max_capacity": 20,
  "waiting_visitors": [
    {
      "visitor_id": 1,
      "name": "张三",
      "waiting_since": "09:20",
      "expected_pickup_time": "09:30",
      "host_notified": true
    }
  ],
  "facilities": {
    "wifi_available": true,
    "refreshments": true,
    "reading_materials": true
  }
}
```

### 40. 访客服务反馈
**收集访客服务反馈**

```http
POST /api/v1/reception/services/feedback
```

**请求体**:
```json
{
  "visitor_id": 1,
  "rating": 5,
  "service_aspects": {
    "reception_service": 5,
    "waiting_environment": 4,
    "facility_quality": 5
  },
  "comments": "服务很好，环境舒适",
  "suggestions": "可以增加更多充电插座"
}
```

### 41. 内部协调通讯
**前台与其他部门的内部通讯**

```http
POST /api/v1/reception/internal/communicate
```

**请求体**:
```json
{
  "target_department": "security|it|admin",
  "message_type": "visitor_assistance|facility_issue|emergency",
  "priority": "low|normal|high|urgent",
  "message": "访客需要技术支持",
  "visitor_id": 1
}
```

## 📱 移动端备用API

### 42. 移动端数据同步
**APP/小程序获取离线数据**

```http
GET /api/v1/mobile/gate/sync
```

**响应** (200):
```json
{
  "sync_timestamp": "2025-06-19T09:00:00Z",
  "today_visitors": [
    {
      "pass_code": "V20250619001",
      "name": "张三",
      "phone_masked": "138****8000",
      "visit_time": "09:00-17:00",
      "areas": ["building_a"]
    }
  ],
  "configuration": {
    "offline_mode_enabled": true,
    "auto_sync_interval": 300,
    "cache_retention": 24
  }
}
```

### 43. 移动端二维码验证
**手机APP扫码验证访客**

```http
POST /api/v1/mobile/gate/verify-qr
```

**请求体**:
```json
{
  "qr_content": "VISITOR:V20250619001:张三:13800138000",
  "location": "main_gate",
  "operator_id": "mobile_gate_001",
  "verification_method": "mobile_app"
}
```

**响应** (200):
```json
{
  "verification_result": {
    "valid": true,
    "visitor_name": "张三",
    "visit_purpose": "business_meeting",
    "can_enter": true,
    "restrictions": []
  },
  "next_action": "allow_entry|require_additional_verification|deny_entry"
}
```

### 44. 移动端访客信息查询
**前台人员移动端查询访客详情**

```http
GET /api/v1/mobile/reception/visitor-info/{qr_code}
```

**响应** (200):
```json
{
  "visitor": {
    "id": 1,
    "name": "张三",
    "company": "ABC公司",
    "visit_purpose": "business_meeting",
    "visitee": "李四",
    "visit_time": "09:00-17:00",
    "status": "approved"
  },
  "quick_actions": [
    "notify_host",
    "checkin",
    "assign_meeting_room"
  ]
}
```

### 45. 移动端快速签到
**前台移动端快速签到**

```http
POST /api/v1/mobile/reception/quick-checkin
```

**请求体**:
```json
{
  "visitor_qr": "V20250619001",
  "checkin_location": "main_lobby",
  "receptionist_id": "mobile_reception_001",
  "quick_mode": true
}
```

### 46. 移动端离线缓存
**获取移动端离线验证数据**

```http
GET /api/v1/mobile/offline/visitor-cache
```

**响应** (200):
```json
{
  "cache_data": {
    "visitors": [
      {
        "pass_code": "V20250619001",
        "name": "张三",
        "basic_info": "encrypted_data",
        "permissions": ["building_a"],
        "valid_time": "09:00-17:00"
      }
    ],
    "cache_expiry": "2025-06-20T06:00:00Z"
  },
  "offline_config": {
    "max_offline_hours": 4,
    "auto_sync_when_online": true
  }
}
```

```http
GET /api/v1/config/spatial/?skip=0&limit=10&is_active=true
```

**响应** (200): 返回空间配置列表