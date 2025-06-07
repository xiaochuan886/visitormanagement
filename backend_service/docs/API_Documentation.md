# 访客管理系统 API 文档

## 概述

访客管理系统提供了完整的RESTful API，支持访客生命周期管理、用户认证、组织架构管理等功能。

**基础信息**:
- **Base URL**: `http://127.0.0.1:8001`
- **API版本**: v1
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证说明

### JWT Token 认证
所有需要认证的API都使用JWT Bearer Token认证方式：

```http
Authorization: Bearer <your_jwt_token>
```

### 获取Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

## API 端点列表

### 1. 认证模块 (Authentication)

#### 1.1 用户登录
```http
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "role": "string",
    "tenant_id": "uuid"
  }
}
```

#### 1.2 刷新访问令牌
```http
POST /api/v1/auth/refresh
```

**请求体**:
```json
{
  "refresh_token": "string"
}
```

**响应**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### 1.3 用户登出
```http
POST /api/v1/auth/logout
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "message": "Successfully logged out"
}
```

#### 1.4 获取当前用户信息
```http
GET /api/v1/auth/me
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "tenant_id": "uuid",
  "is_active": true,
  "created_at": "2025-06-07T11:17:00Z"
}
```

### 2. 访客管理模块 (Visitors)

#### 2.1 创建访客
```http
POST /api/v1/visitors/
```

**Headers**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "name": "张三",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "company": "ABC公司",
  "purpose": "商务洽谈",
  "visit_date": "2025-06-07",
  "visit_time": "14:00",
  "host_employee_id": "uuid",
  "department_id": "uuid",
  "site_id": "uuid",
  "id_card": "110101199001011234",
  "notes": "重要客户"
}
```

**响应**:
```json
{
  "id": "uuid",
  "name": "张三",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "company": "ABC公司",
  "purpose": "商务洽谈",
  "visit_date": "2025-06-07",
  "visit_time": "14:00:00",
  "status": "pending",
  "approval_status": "pending",
  "host_employee": {
    "id": "uuid",
    "name": "李四",
    "department": "销售部"
  },
  "qr_code": "string",
  "created_at": "2025-06-07T11:17:00Z"
}
```

#### 2.2 获取访客列表
```http
GET /api/v1/visitors/
```

**Headers**: `Authorization: Bearer <token>`

**查询参数**:
- `page`: 页码 (默认: 1)
- `size`: 每页数量 (默认: 20)
- `status`: 访客状态 (pending/approved/rejected/checked_in/checked_out)
- `date_from`: 开始日期 (YYYY-MM-DD)
- `date_to`: 结束日期 (YYYY-MM-DD)
- `search`: 搜索关键词 (姓名、公司、手机号)

**响应**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "张三",
      "phone": "13800138000",
      "company": "ABC公司",
      "purpose": "商务洽谈",
      "visit_date": "2025-06-07",
      "status": "approved",
      "host_employee": {
        "name": "李四",
        "department": "销售部"
      },
      "created_at": "2025-06-07T11:17:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

#### 2.3 获取访客详情
```http
GET /api/v1/visitors/{visitor_id}
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "id": "uuid",
  "name": "张三",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "company": "ABC公司",
  "purpose": "商务洽谈",
  "visit_date": "2025-06-07",
  "visit_time": "14:00:00",
  "status": "approved",
  "approval_status": "approved",
  "host_employee": {
    "id": "uuid",
    "name": "李四",
    "email": "lisi@company.com",
    "department": "销售部"
  },
  "department": {
    "id": "uuid",
    "name": "销售部"
  },
  "site": {
    "id": "uuid",
    "name": "总部大厦"
  },
  "qr_code": "string",
  "check_in_time": null,
  "check_out_time": null,
  "approval_history": [
    {
      "action": "approved",
      "approver": "管理员",
      "timestamp": "2025-06-07T11:17:00Z",
      "notes": "审批通过"
    }
  ],
  "created_at": "2025-06-07T11:17:00Z",
  "updated_at": "2025-06-07T11:17:00Z"
}
```

#### 2.4 更新访客信息
```http
PUT /api/v1/visitors/{visitor_id}
```

**Headers**: `Authorization: Bearer <token>`

**请求体**: (与创建访客相同，所有字段可选)

#### 2.5 删除访客
```http
DELETE /api/v1/visitors/{visitor_id}
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "message": "Visitor deleted successfully"
}
```

#### 2.6 审批访客
```http
POST /api/v1/visitors/{visitor_id}/approve
```

**Headers**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "action": "approve",  // approve | reject
  "notes": "审批通过，欢迎来访"
}
```

**响应**:
```json
{
  "id": "uuid",
  "status": "approved",
  "approval_status": "approved",
  "approval_notes": "审批通过，欢迎来访",
  "approved_by": "管理员",
  "approved_at": "2025-06-07T11:17:00Z"
}
```

#### 2.7 访客签到
```http
POST /api/v1/visitors/{visitor_id}/checkin
```

**Headers**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "checkin_point_id": "uuid",
  "notes": "正常签到"
}
```

**响应**:
```json
{
  "id": "uuid",
  "status": "checked_in",
  "check_in_time": "2025-06-07T14:00:00Z",
  "checkin_point": {
    "id": "uuid",
    "name": "前台签到处"
  }
}
```

#### 2.8 访客签出
```http
POST /api/v1/visitors/{visitor_id}/checkout
```

**Headers**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "notes": "正常签出"
}
```

**响应**:
```json
{
  "id": "uuid",
  "status": "checked_out",
  "check_out_time": "2025-06-07T17:00:00Z",
  "visit_duration": "03:00:00"
}
```

#### 2.9 获取访客二维码
```http
GET /api/v1/visitors/{visitor_id}/qrcode
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "qr_text": "VISITOR:uuid:张三:2025-06-07",
  "expires_at": "2025-06-07T23:59:59Z"
}
```

### 3. 员工管理模块 (Employees)

#### 3.1 获取员工列表
```http
GET /api/v1/employees/
```

**Headers**: `Authorization: Bearer <token>`

**查询参数**:
- `page`: 页码 (默认: 1)
- `size`: 每页数量 (默认: 20)
- `department_id`: 部门ID
- `search`: 搜索关键词

**响应**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "李四",
      "email": "lisi@company.com",
      "phone": "13900139000",
      "employee_id": "EMP001",
      "department": {
        "id": "uuid",
        "name": "销售部"
      },
      "position": "销售经理",
      "is_active": true
    }
  ],
  "total": 50,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

#### 3.2 获取员工详情
```http
GET /api/v1/employees/{employee_id}
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "id": "uuid",
  "name": "李四",
  "email": "lisi@company.com",
  "phone": "13900139000",
  "employee_id": "EMP001",
  "department": {
    "id": "uuid",
    "name": "销售部",
    "code": "SALES"
  },
  "position": "销售经理",
  "manager": {
    "id": "uuid",
    "name": "王五"
  },
  "is_active": true,
  "hire_date": "2023-01-01",
  "created_at": "2023-01-01T00:00:00Z"
}
```

### 4. 部门管理模块 (Departments)

#### 4.1 获取部门列表
```http
GET /api/v1/departments/
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "销售部",
      "code": "SALES",
      "description": "负责产品销售和客户关系管理",
      "parent_department": null,
      "manager": {
        "id": "uuid",
        "name": "王五"
      },
      "employee_count": 15,
      "is_active": true
    }
  ]
}
```

#### 4.2 获取部门详情
```http
GET /api/v1/departments/{department_id}
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "id": "uuid",
  "name": "销售部",
  "code": "SALES",
  "description": "负责产品销售和客户关系管理",
  "parent_department": null,
  "sub_departments": [
    {
      "id": "uuid",
      "name": "华北销售组",
      "code": "SALES_NORTH"
    }
  ],
  "manager": {
    "id": "uuid",
    "name": "王五",
    "email": "wangwu@company.com"
  },
  "employees": [
    {
      "id": "uuid",
      "name": "李四",
      "position": "销售经理"
    }
  ],
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

### 5. 站点管理模块 (Sites)

#### 5.1 获取站点列表
```http
GET /api/v1/sites/
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "总部大厦",
      "code": "HQ",
      "address": "北京市朝阳区xxx路xxx号",
      "description": "公司总部办公楼",
      "is_active": true,
      "checkin_points_count": 3
    }
  ]
}
```

#### 5.2 获取站点详情
```http
GET /api/v1/sites/{site_id}
```

**Headers**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "id": "uuid",
  "name": "总部大厦",
  "code": "HQ",
  "address": "北京市朝阳区xxx路xxx号",
  "description": "公司总部办公楼",
  "contact_person": "张管理员",
  "contact_phone": "010-12345678",
  "checkin_points": [
    {
      "id": "uuid",
      "name": "前台签到处",
      "location": "1楼大厅",
      "is_active": true
    }
  ],
  "departments": [
    {
      "id": "uuid",
      "name": "销售部",
      "floor": "3楼"
    }
  ],
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

## 错误响应格式

所有API错误都遵循统一的响应格式：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "timestamp": "2025-06-07T11:17:00Z",
  "path": "/api/v1/visitors/"
}
```

### 常见错误码

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | VALIDATION_ERROR | 请求参数验证失败 |
| 401 | UNAUTHORIZED | 未授权，需要登录 |
| 403 | FORBIDDEN | 权限不足 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突 |
| 422 | UNPROCESSABLE_ENTITY | 请求格式正确但语义错误 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

## 分页说明

所有列表API都支持分页，使用以下参数：

- `page`: 页码，从1开始 (默认: 1)
- `size`: 每页数量 (默认: 20，最大: 100)

分页响应格式：
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

## 排序和过滤

### 排序
使用 `sort` 参数指定排序字段和方向：
- `sort=created_at`: 按创建时间升序
- `sort=-created_at`: 按创建时间降序
- `sort=name,-created_at`: 多字段排序

### 过滤
各API支持特定的过滤参数，详见各端点说明。

## 速率限制

- **认证端点**: 每分钟最多10次请求
- **其他端点**: 每分钟最多100次请求
- **超出限制**: 返回429状态码

## 示例代码

### Python 示例
```python
import requests

# 登录获取token
login_response = requests.post(
    "http://127.0.0.1:8001/api/v1/auth/login",
    json={"username": "admin", "password": "password"}
)
token = login_response.json()["access_token"]

# 使用token访问API
headers = {"Authorization": f"Bearer {token}"}
visitors = requests.get(
    "http://127.0.0.1:8001/api/v1/visitors/",
    headers=headers
)
print(visitors.json())
```

### JavaScript 示例
```javascript
// 登录获取token
const loginResponse = await fetch('http://127.0.0.1:8001/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'password' })
});
const { access_token } = await loginResponse.json();

// 使用token访问API
const visitorsResponse = await fetch('http://127.0.0.1:8001/api/v1/visitors/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const visitors = await visitorsResponse.json();
console.log(visitors);
```

## 在线文档

- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc
- **OpenAPI规范**: http://127.0.0.1:8001/openapi.json 